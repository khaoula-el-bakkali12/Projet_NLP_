"""
llm_module.py
=============
Local-only LLM benchmarking module for the Oncology RAG Assistant.
Person 4 — Module LLM / Génération & Benchmarking

All inference runs locally via HuggingFace Transformers.
No external API calls (no Gemini, Mistral API, Groq, OpenAI, etc.)

Models loaded:
  Model A — google/flan-t5-base          (seq2seq, fast, low RAM)
  Model B — microsoft/phi-2              (causal LM, quality/speed balance)
  Model C — TinyLlama/TinyLlama-1.1B-... (causal LM, ultra-lightweight)

Requirements (see requirements_local.txt):
  pip install transformers torch accelerate sentencepiece
  pip install rouge-score nltk bert-score
"""

import os
import time
import json
import logging
import warnings
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict

import torch
import nltk
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer
from bert_score import score as bert_score_fn

from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    AutoModelForCausalLM,
    pipeline,
)

# ─────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("llm_module")
warnings.filterwarnings("ignore", category=UserWarning)

# Download NLTK data once
# "punkt" provides sentence/word tokenizers used by BLEU scoring.
nltk.download("punkt", quiet=True)

# ─────────────────────────────────────────────
# Device detection
# ─────────────────────────────────────────────
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
logger.info(f"Inference device: {DEVICE.upper()}")

# ─────────────────────────────────────────────
# Safety keywords (oncology context)
# ─────────────────────────────────────────────
SAFETY_DISCLAIMER = (
    "\n\n⚠️ *Avertissement : Cette réponse est fournie à titre informatif uniquement "
    "et ne constitue pas un avis médical. Consultez toujours un professionnel de santé qualifié.*"
)

# ─────────────────────────────────────────────
# Data structures
# ─────────────────────────────────────────────
@dataclass
class Document:
    """Minimal document structure from the retrieval module."""
    id: str
    contenu: str
    categorie: str = ""
    type_cancer: str = ""
    mots_cles: list[str] = field(default_factory=list)
    protocole: str = ""
    source_reference: str = ""


@dataclass
class GenerationResult:
    model_name: str
    model_id: str
    response: str
    latency_seconds: float
    safe: bool
    prompt_template: str
    error: Optional[str] = None


@dataclass
class BenchmarkEntry:
    question: str
    gold_standard: str
    results: list[GenerationResult] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)


# ─────────────────────────────────────────────
# Prompt templates
# ─────────────────────────────────────────────
def build_context(top_k_docs: list[Document], max_chars: int = 1800) -> str:
    """
    Build a context block from retrieved documents for injection into the prompt.

    Truncation strategy (fixes naive mid-thought cut):
      1. Each document is formatted as a complete unit (never split mid-doc).
      2. Documents are included in retrieval-rank order (most relevant first).
      3. If a document would push the total over max_chars, it is SKIPPED
         rather than truncated mid-sentence — preserving semantic integrity.
      4. A lightweight fallback adds a partial summary line if zero docs fit.

    This is still lexical chunking. A production system should use semantic
    chunking (split by sentence, re-rank chunks by cosine similarity to query).
    That improvement belongs in Person 1's indexing pipeline.
    """
    parts: list[str] = []
    total: int = 0

    for doc in top_k_docs:
        # Build the full chunk for this document — never truncate mid-chunk.
        # No "[CATEGORIE]" prefix: extractive models (flan) copied that tag
        # verbatim into answers (e.g. a reply starting with "[SUIVI] …").
        lines = [doc.contenu]
        if doc.protocole:
            lines.append(f"Protocole : {doc.protocole}")
        # B2 citation grounding: tag the reference with [SOURCE] so the citation
        # instruction in prompt templates can point the LLM to a concrete label.
        if doc.source_reference:
            lines.append(f"[SOURCE] {doc.source_reference}")
        elif doc.id:
            lines.append(f"[SOURCE] {doc.id}")
        chunk = "\n".join(lines)

        if total + len(chunk) + 7 <= max_chars:   # +7 for the separator
            parts.append(chunk)
            total += len(chunk) + 7
        else:
            # Document doesn't fit — skip it entirely (no mid-thought cuts)
            # Log so developers know context was narrowed
            logger.debug(
                f"Context budget full — skipped doc {doc.id} "
                f"({len(chunk)} chars). Budget used: {total}/{max_chars}."
            )

    if not parts:
        # Edge case: even the first document is larger than max_chars.
        # Give as much of the doc as the budget allows (NOT a hardcoded 300 —
        # that cut the context mid-word and the model copied the truncation,
        # e.g. "…Ils sont in"). Build the full chunk, trim to max_chars, then
        # back off to the last sentence boundary so it never ends mid-word.
        if top_k_docs:
            first = top_k_docs[0]
            lines = [first.contenu]
            if first.protocole:
                lines.append(f"Protocole : {first.protocole}")
            chunk = "\n".join(lines)
            if len(chunk) > max_chars:
                chunk = chunk[:max_chars]
                cut = max(chunk.rfind(". "), chunk.rfind(".\n"), chunk.rfind("\n"))
                if cut > max_chars // 2:
                    chunk = chunk[:cut + 1]
            logger.warning(
                f"First document exceeds max_chars={max_chars}; "
                "using a sentence-bounded slice."
            )
            return chunk
        return "(aucun contexte disponible)"

    return "\n\n---\n\n".join(parts)


def prompt_zero_shot(question: str, context: str) -> str:
    return (
        f"CONTEXTE:\n{context}\n\n"
        f"INSTRUCTION: Réponds en 3-4 phrases maximum en utilisant UNIQUEMENT les informations du CONTEXTE. "
        f"Copie les noms de médicaments, doses et protocoles EXACTEMENT tels qu'ils apparaissent dans le CONTEXTE. "
        f"Après chaque affirmation médicale, cite la source entre parenthèses en utilisant la balise [SOURCE] "
        f"du contexte, par exemple : (Guide AMFROM 2024 p.13). "
        f"N'ajoute aucune information extérieure. Sois concis.\n\n"
        f"QUESTION: {question}\n"
        "RÉPONSE (avec citations):"
    )


def prompt_few_shot(question: str, context: str) -> str:
    examples = (
        "EXEMPLE 1:\n"
        "Question: Quel est le protocole AC pour le cancer du sein ?\n"
        "Réponse: Le protocole AC associe Doxorubicine (60 mg/m²) et Cyclophosphamide (600 mg/m²) "
        "toutes les 3 semaines, généralement pour 4 cycles. Il est utilisé en situation adjuvante "
        "ou néoadjuvante selon le stade.\n\n"
        "EXEMPLE 2:\n"
        "Question: Quels sont les effets secondaires courants de la chimiothérapie ?\n"
        "Réponse: Les effets secondaires fréquents incluent nausées, vomissements, alopécie, "
        "fatigue, myélosuppression et mucites. La prise en charge symptomatique est essentielle "
        "tout au long du traitement.\n\n"
    )
    return (
        f"{examples}"
        f"CONTEXTE:\n{context}\n\n"
        f"INSTRUCTION: Réponds uniquement à partir du CONTEXTE. Copie les noms de médicaments et doses EXACTEMENT. "
        f"Cite la source [SOURCE] du contexte après chaque affirmation, au format (Guide AMFROM 2024 p.XX).\n\n"
        f"QUESTION: {question}\n"
        "RÉPONSE (avec citations):"
    )


def prompt_chain_of_thought(question: str, context: str) -> str:
    return (
        f"CONTEXTE:\n{context}\n\n"
        f"INSTRUCTION: Utilise UNIQUEMENT le CONTEXTE. Copie les noms de médicaments et doses EXACTEMENT. "
        f"Cite la source [SOURCE] après chaque fait au format (Guide AMFROM 2024 p.XX).\n\n"
        f"QUESTION: {question}\n\n"
        "Étape 1 — Informations clés du contexte:\n"
        "Étape 2 — Réponse finale (avec citations [SOURCE]):\n"
        "RÉPONSE:"
    )


PROMPT_BUILDERS = {
    "zero_shot": prompt_zero_shot,
    "few_shot": prompt_few_shot,
    "chain_of_thought": prompt_chain_of_thought,
}

# ─────────────────────────────────────────────
# Safety checker
# ─────────────────────────────────────────────
import re as _re

# Each pattern uses word boundaries (\b) where applicable so that
# "le patient a reçu" does not trigger on "le patient a" mid-word.
# Patterns are compiled once for performance.
_SAFETY_PATTERNS: list[_re.Pattern] = [
    _re.compile(r"\bje\s+diagnostique\b",                  _re.IGNORECASE),
    _re.compile(r"\bvous\s+avez\s+le\s+cancer\b",          _re.IGNORECASE),
    _re.compile(r"\bvous\s+souffrez\s+d[e']",              _re.IGNORECASE),
    _re.compile(r"\bce\s+médicament\s+guérit\b",           _re.IGNORECASE),
    _re.compile(r"\barrêtez\s+votre\s+traitement\b",       _re.IGNORECASE),
    _re.compile(r"\bne\s+consultez\s+pas\b",               _re.IGNORECASE),
    _re.compile(r"\bguaranteed\s+cure\b",                  _re.IGNORECASE),
    _re.compile(r"\bstop\s+your\s+medication\b",           _re.IGNORECASE),
    # Catch direct patient-labelling diagnosis statements
    _re.compile(r"\bvous\s+(êtes|souffrez|avez)\s+(atteint|un\s+cancer|le\s+cancer)\b",
                _re.IGNORECASE),
]

# NOTE on limitations: regex catches exact phrasing only — it does NOT
# understand paraphrased or semantically equivalent unsafe content.
# A proper solution for production would be a fine-tuned safety classifier
# (e.g. a small BERT model trained on safe/unsafe medical statements).
# This regex layer is a necessary first defence, not a complete solution.


def is_safe(response: str) -> bool:
    """Return True if no safety pattern is found in the response."""
    return not any(pat.search(response) for pat in _SAFETY_PATTERNS)


def apply_safety_filter(response: str) -> tuple[str, bool]:
    safe = is_safe(response)
    if not safe:
        response += SAFETY_DISCLAIMER
    return response, safe


# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
# Output post-processing for causal LMs
# ─────────────────────────────────────────────
_STOP_PATTERNS = _re.compile(
    r'\n(?:Question|QUESTION|Question\s*:|Q\s*:|\bQ\b\s*:|CONTEXTE|Contexte|INSTRUCTION)',
    _re.IGNORECASE
)

def _clean_causal_output(text: str) -> str:
    """Truncate causal LM output at the first sign of a new Q&A generation."""
    text = text.strip()
    m = _STOP_PATTERNS.search(text)
    if m:
        text = text[:m.start()].strip()
    # Also strip trailing incomplete sentence (ends without . ? !)
    if text and text[-1] not in '.?!»"':
        last = max(text.rfind('.'), text.rfind('?'), text.rfind('!'))
        if last > len(text) // 2:
            text = text[:last + 1].strip()
    return text


# Model registry — loaded ONCE at import time
# ─────────────────────────────────────────────
class ModelRegistry:
    """
    Loads all three local models once and exposes a unified generate() interface.

    Model A — google/flan-t5-base
        Seq2Seq encoder-decoder. Excellent at instruction following for short
        structured answers. Very fast on CPU (~500 MB RAM).

    Model B — microsoft/phi-2
        2.7B causal LM from Microsoft. Strong reasoning, fits in ~6 GB VRAM
        or ~12 GB RAM with float32. Good balance of quality vs. size.

    Model C — TinyLlama/TinyLlama-1.1B-Chat-v1.0
        1.1B causal LM. Extremely lightweight (~2.2 GB RAM). Ideal for
        rapid prototyping or low-resource environments.

    HOW TO SWAP MODELS:
        Change the MODEL_* constants below to any HuggingFace model ID.
        Ensure the model is downloaded with:
            huggingface-cli download <model_id>
        or set HF_HUB_OFFLINE=1 after first download for fully offline use.
    """

    MODEL_A_ID = "google/flan-t5-base"               # seq2seq
    MODEL_B_ID = "Qwen/Qwen2.5-1.5B-Instruct"       # causal, 1.5B, CPU-friendly
    MODEL_C_ID = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  # causal lightweight

    def __init__(self):
        self._pipelines: dict = {}
        self._load_all()

    # ── internal loaders ──────────────────────

    def _load_seq2seq(self, model_id: str, name: str):
        logger.info(f"Loading {name} ({model_id}) — seq2seq …")
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForSeq2SeqLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
            device_map="auto" if DEVICE == "cuda" else None,
            low_cpu_mem_usage=True,
        )
        if DEVICE == "cpu":
            model = model.to("cpu")
        # transformers 5.x removed "text2text-generation" as a pipeline task and
        # also removed Text2TextGenerationPipeline from the public API.
        # Store model+tokenizer directly and call model.generate() in generate().
        self._pipelines[name] = ("seq2seq_raw", (tokenizer, model))
        logger.info(f"  ✓ {name} ready.")

    def _load_causal(self, model_id: str, name: str, max_new_tokens: int = 300):
        logger.info(f"Loading {name} ({model_id}) — causal LM …")
        tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            trust_remote_code=True,
        )
        # ── Pad token strategy ────────────────────────────────────────────
        # Priority 1: tokenizer already has a pad token → nothing to do.
        # Priority 2: tokenizer has a [PAD] in its vocabulary → use it.
        # Priority 3: fall back to eos_token (safe for generation, but we
        #             must set padding_side="left" so it doesn't corrupt
        #             the generated text for batch inference).
        if tokenizer.pad_token is None:
            if "[PAD]" in tokenizer.get_vocab():
                tokenizer.pad_token = "[PAD]"
            else:
                tokenizer.pad_token = tokenizer.eos_token
                tokenizer.padding_side = "left"   # required when pad==eos

        # ── phi-2 (model_b) needs 4-bit quantisation to fit in 4 GB VRAM ──
        # bitsandbytes quantisation halves the effective model size:
        # phi-2 at float16 ≈ 5.5 GB → 4-bit ≈ 1.7 GB, comfortably within GTX 1050.
        # Models A and C are small enough to load without quantisation.
        if name == "model_b" and DEVICE == "cuda":
            from transformers import BitsAndBytesConfig
            quantization_config = BitsAndBytesConfig(load_in_4bit=True)
            logger.info(f"  ↳ Applying 4-bit quantisation for {name} (GTX 1050 / 4 GB VRAM)")
        else:
            quantization_config = None

        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
            device_map="auto",          # handles multi-GPU / CPU offload automatically
            trust_remote_code=True,
            low_cpu_mem_usage=True,
            quantization_config=quantization_config,
        )
        gen_pipeline = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.3,
            top_p=0.9,
            # 1.2 was too aggressive for medical vocab — the model mangled drug
            # names (Carboplatine → "Carboplate") to avoid repeating tokens.
            # Qwen's own recommended value is 1.05; 1.1 is a safe middle ground.
            repetition_penalty=1.1,
            pad_token_id=tokenizer.pad_token_id,
            return_full_text=False,
        )
        self._pipelines[name] = ("causal", gen_pipeline)
        logger.info(f"  ✓ {name} ready.")

    # Model metadata — used for lazy loading
    _MODEL_META = {
        "model_a": (None, "seq2seq"),   # model_id filled in __init__
        "model_b": (None, "causal"),
        "model_c": (None, "causal"),
    }

    def _load_all(self):
        """Register model metadata. Models are loaded lazily on first generate() call."""
        self._MODEL_META = {
            "model_a": (self.MODEL_A_ID, "seq2seq"),
            "model_b": (self.MODEL_B_ID, "causal"),
            "model_c": (self.MODEL_C_ID, "causal"),
        }
        # Mark all as "unloaded" (not "error") so generate() knows to load them
        for name in self._MODEL_META:
            self._pipelines[name] = ("unloaded", None)
        logger.info("ModelRegistry: lazy mode — models load on first use.")

    def _evict_others(self, keep: str):
        """Free VRAM held by every loaded model except `keep`.

        This hardware (GTX 1050, 4 GB) cannot hold more than one LLM plus the
        SBERT retrieval model at once. Since the API serves one model per
        request, we keep only the active LLM resident and unload the rest.
        Evicted models return to "unloaded" and reload on next use.
        """
        import gc
        for other, (kind, pipe) in list(self._pipelines.items()):
            if other == keep or kind in ("unloaded", "error"):
                continue
            logger.info(f"Evicting {other} to free VRAM for {keep}.")
            self._pipelines[other] = ("unloaded", None)
            del pipe
        gc.collect()
        if DEVICE == "cuda":
            torch.cuda.empty_cache()

    def _ensure_loaded(self, name: str):
        """Load a model the first time it is requested."""
        if self._pipelines.get(name, (None,))[0] not in ("unloaded",):
            return  # already loaded or errored
        # On a small GPU, free the other models' VRAM before loading this one.
        if DEVICE == "cuda":
            self._evict_others(keep=name)
        model_id, kind = self._MODEL_META[name]
        try:
            if kind == "seq2seq":
                self._load_seq2seq(model_id, name)
            else:
                # Qwen (model_b): 320 — chain_of_thought prints reasoning steps
                #   and needs the room; with the chat template + tuned rep penalty
                #   it no longer rambles.
                # TinyLlama (model_c): 160 — at 1.1B it nails the grounded content
                #   then invents (e.g. a fake "carboplatine 100 mg/m² oral" dose)
                #   once it runs out of facts. Capping it short keeps it on the
                #   grounded answer; _clean_causal_output trims any partial tail.
                tokens = 320 if name == "model_b" else 160
                self._load_causal(model_id, name, max_new_tokens=tokens)
        except Exception as e:
            logger.error(f"Failed to load {name} ({model_id}): {e}")
            self._pipelines[name] = ("error", str(e))

    # ── public generate ───────────────────────

    def generate(self, name: str, prompt: str) -> tuple[str, float]:
        """
        Run inference for a given model name.
        Returns (response_text, latency_seconds).
        Raises RuntimeError if model failed to load.
        """
        self._ensure_loaded(name)
        entry = self._pipelines.get(name)
        if entry is None:
            raise RuntimeError(f"Model '{name}' not registered.")
        kind, pipe = entry
        if kind == "error":
            raise RuntimeError(f"Model '{name}' failed to load: {pipe}")

        t0 = time.perf_counter()
        if kind == "seq2seq_raw":
            # Direct model.generate() — works with all transformers versions
            tokenizer, model = pipe
            inputs = tokenizer(
                prompt, return_tensors="pt", truncation=True, max_length=512
            )
            if DEVICE == "cuda":
                inputs = {k: v.cuda() for k, v in inputs.items()}
            with torch.no_grad():
                # flan-t5-base decoding fixes:
                #  - num_beams=4: beam search >> greedy for flan-t5 QA quality.
                #    Greedy was producing empty ("les suivantes :") and circular
                #    ("Cette méthode est le protocole…") answers on broad questions.
                #  - min_new_tokens=24: stop it returning a one-line non-answer.
                #  - no_repeat_ngram_size=3: kill loops without a heavy penalty.
                #  - repetition_penalty 1.3 → 1.15: 1.3 over-penalised and
                #    suppressed real content (same bug class as Qwen at 1.2).
                output_ids = model.generate(
                    **inputs,
                    # 350 was the real cause of the mid-word cut-offs ("Ils sont
                    # in…"): flan-t5's multilingual tokenizer splits French medical
                    # terms into many sub-tokens, so 350 tokens ≈ only ~50 words.
                    # 512 lets these answers finish; early_stopping=True returns the
                    # first EOS-terminated beam, so it ends on a complete sentence.
                    max_new_tokens=512,
                    min_new_tokens=24,
                    num_beams=4,
                    no_repeat_ngram_size=3,
                    repetition_penalty=1.15,
                    early_stopping=True,
                    length_penalty=1.0,
                )
            text = tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()
        elif kind == "seq2seq":
            out = pipe(prompt, max_new_tokens=512)
            text = (out[0].get("generated_text") or "").strip()
        else:  # causal
            # Qwen2.5-Instruct / TinyLlama-Chat are INSTRUCT models trained on a
            # strict chat format (<|im_start|>…). Feeding a raw completion string
            # runs them off-distribution → garbled drug names + hallucination.
            # Apply the model's native chat template when it has one.
            tok = getattr(pipe, "tokenizer", None)
            chat_prompt = prompt
            if tok is not None and getattr(tok, "chat_template", None):
                messages = [
                    {"role": "system", "content":
                        "Tu es un assistant médical en oncologie. Tu réponds "
                        "TOUJOURS et UNIQUEMENT en français — jamais en anglais. "
                        "Réponds directement à la QUESTION, de façon claire et "
                        "factuelle, en te basant uniquement sur le CONTEXTE fourni. "
                        "Lorsque le contexte mentionne des médicaments ou des doses, "
                        "recopie-les exactement. Ne pose aucun diagnostic."},
                    {"role": "user", "content": prompt},
                ]
                chat_prompt = tok.apply_chat_template(
                    messages, tokenize=False, add_generation_prompt=True
                )
            if name == "model_c":
                # TinyLlama (1.1B) is English-dominant and drifts to English /
                # meta-commentary despite the French system message. Priming the
                # reply forces it to continue in French (models stay in the
                # language they start in). Beam search keeps it coherent.
                if tok is not None and getattr(tok, "chat_template", None):
                    chat_prompt += "Réponse en français : "
                out = pipe(
                    chat_prompt,
                    do_sample=False,
                    num_beams=4,
                    no_repeat_ngram_size=3,
                    repetition_penalty=1.15,
                )
            else:
                out = pipe(chat_prompt)
            raw = out[0].get("generated_text") or out[0].get("text") or ""
            text = _clean_causal_output(raw)
        latency = time.perf_counter() - t0
        return text, latency

    @property
    def available_models(self) -> list[str]:
        return [k for k, v in self._pipelines.items() if v[0] not in ("error", "unloaded")]

    @property
    def registered_models(self) -> list[str]:
        """All registered model names, regardless of load state (lazy mode)."""
        return list(self._MODEL_META.keys())


# Singleton — loaded once when the module is imported
logger.info("Initialising ModelRegistry (this may take a few minutes on first run)…")
_registry = ModelRegistry()
logger.info(f"Registry ready. Available models: {_registry.available_models}")


# ─────────────────────────────────────────────
# Public generation interface (RAG-compatible)
# ─────────────────────────────────────────────
def generate_response(
    question: str,
    top_k_docs: list[Document],
    model_name: str = "model_a",
    prompt_template: str = "zero_shot",
) -> GenerationResult:
    """
    Generate a response for a single model.
    Compatible with the RAG pipeline interface expected by Person 3 & Person 5.

    Args:
        question:        User question (fr/ar).
        top_k_docs:      Retrieved documents from the retrieval module.
        model_name:      One of "model_a", "model_b", "model_c".
        prompt_template: One of "zero_shot", "few_shot", "chain_of_thought".

    Returns:
        GenerationResult dataclass.
    """
    builder = PROMPT_BUILDERS.get(prompt_template, prompt_zero_shot)
    # flan-t5-base (seq2seq) is a weak 250M model. Given 2+ docs it echoes an
    # arbitrary context span (often the wrong doc) instead of synthesising.
    # Feed it ONLY the top-1 retrieved doc so it can't grab a lower-ranked fiche.
    if model_name == "model_a":
        # 900 was too small: docs with a long protocole (contenu + protocole
        # ~1100 chars) overflowed it, triggering the truncated fallback and
        # feeding flan a context cut mid-word. 1400 fits a full doc (incl. doses)
        # and still leaves room under flan's 512-token input limit.
        context = build_context(top_k_docs[:1], max_chars=1400)
        prompt = (
            f"Answer in French based only on the context below. "
            f"If the context does not directly answer the question, "
            f"respond ONLY with: "
            f"\"Je n'ai pas d'information sur ce sujet dans ma base de données.\"\n"
            f"Context: {context}\n"
            f"Question: {question}\n"
            "Answer:"
        )
    elif model_name == "model_c":
        # TinyLlama (1.1B) is too weak to separate task-instructions from the
        # actual question: when the user turn is mostly instructions it just
        # echoes/translates them instead of answering. So we put NO instructions
        # here — they live in the chat-template system message (see generate()).
        # The user turn carries only context + question, with the question last.
        # Top-1 doc only: 2 docs make it narrate/compare ("l'article indique…")
        # instead of answering; one clear doc keeps it on a single answer.
        context = build_context(top_k_docs[:1], max_chars=900)
        prompt = (
            f"Contexte :\n{context}\n\n"
            f"Question : {question}"
        )
    else:
        context = build_context(top_k_docs)
        prompt = builder(question, context)

    model_ids = {
        "model_a": ModelRegistry.MODEL_A_ID,
        "model_b": ModelRegistry.MODEL_B_ID,
        "model_c": ModelRegistry.MODEL_C_ID,
    }

    try:
        raw_text, latency = _registry.generate(model_name, prompt)
        response, safe = apply_safety_filter(raw_text)
        return GenerationResult(
            model_name=model_name,
            model_id=model_ids.get(model_name, "unknown"),
            response=response,
            latency_seconds=round(latency, 3),
            safe=safe,
            prompt_template=prompt_template,
        )
    except Exception as e:
        return GenerationResult(
            model_name=model_name,
            model_id=model_ids.get(model_name, "unknown"),
            response="",
            latency_seconds=0.0,
            safe=False,
            prompt_template=prompt_template,
            error=str(e),
        )


def generate_all_models(
    question: str,
    top_k_docs: list[Document],
    prompt_template: str = "zero_shot",
    parallel: bool = None,           # None = auto-detect based on device
    models_filter: list[str] = None, # e.g. ["model_a"] to run only one model
) -> list[GenerationResult]:
    """
    Run all three models (or a subset) and return one GenerationResult per model.

    Parallelism strategy:
      - GPU  → sequential (parallel=False forced) to avoid VRAM OOM.
              Three models sharing one GPU simultaneously will crash
              on anything below 24 GB VRAM.
      - CPU  → parallel with max_workers=2 (not 3) to cap RAM pressure.
              Full parallelism on CPU just causes thrashing.

    You can override with parallel=True/False explicitly.
    models_filter: if provided, only the named models run (e.g. ["model_a"]).
    """
    all_models = _registry.registered_models
    models = (
        [m for m in all_models if m in models_filter]
        if models_filter
        else all_models
    )

    # Auto-detect safest strategy
    if parallel is None:
        parallel = (DEVICE == "cpu")          # sequential on GPU, parallel on CPU

    if parallel:
        results = []
        # cap at 2 workers even on CPU — 3 large models × RAM = thrashing risk
        with ThreadPoolExecutor(max_workers=min(2, len(models))) as executor:
            futures = {
                executor.submit(generate_response, question, top_k_docs, m, prompt_template): m
                for m in models
            }
            for future in as_completed(futures):
                results.append(future.result())
        return results
    else:
        # Sequential: one model at a time — safe for GPU, avoids VRAM conflicts
        return [generate_response(question, top_k_docs, m, prompt_template) for m in models]


# ─────────────────────────────────────────────
# Evaluation metrics
# ─────────────────────────────────────────────
def compute_bleu(hypothesis: str, reference: str) -> float:
    """Sentence-level BLEU with smoothing."""
    ref_tokens = nltk.word_tokenize(reference.lower())
    hyp_tokens = nltk.word_tokenize(hypothesis.lower())
    if not hyp_tokens:
        return 0.0
    smoothie = SmoothingFunction().method4
    return round(sentence_bleu([ref_tokens], hyp_tokens, smoothing_function=smoothie), 4)


def compute_rouge_l(hypothesis: str, reference: str) -> float:
    """ROUGE-L F1 score."""
    scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
    scores = scorer.score(reference, hypothesis)
    return round(scores["rougeL"].fmeasure, 4)


def compute_bertscore(hypothesis: str, reference: str) -> float:
    """
    BERTScore F1 using bert-base-multilingual-cased.
    Supports French and Arabic — matches this project's data.
    We use model_type directly instead of lang= to avoid version-dependent
    language-to-model mapping issues in bert-score >=0.3.x.
    """
    try:
        _, _, F1 = bert_score_fn(
            [hypothesis],
            [reference],
            model_type="bert-base-multilingual-cased",
            num_layers=9,              # optimal layer for multilingual BERT
            rescale_with_baseline=False,
            verbose=False,
        )
        return round(F1.item(), 4)
    except Exception as e:
        logger.warning(f"BERTScore failed: {e}")
        return 0.0


def evaluate_result(result: GenerationResult, gold_standard: str) -> dict:
    """Compute all metrics for one GenerationResult vs. its gold standard."""
    if result.error or not result.response:
        return {
            "bleu": 0.0,
            "rouge_l": 0.0,
            "bertscore": 0.0,
            "latency_seconds": result.latency_seconds,
            "safe": result.safe,
            "error": result.error,
        }
    return {
        "bleu": compute_bleu(result.response, gold_standard),
        "rouge_l": compute_rouge_l(result.response, gold_standard),
        "bertscore": compute_bertscore(result.response, gold_standard),
        "latency_seconds": result.latency_seconds,
        "safe": result.safe,
        "error": None,
    }


# ─────────────────────────────────────────────
# Benchmarking pipeline
# ─────────────────────────────────────────────
def run_benchmark(
    test_set: list[dict],
    retrieval_fn,
    prompt_template: str = "zero_shot",
    output_path: str = "benchmark_results.json",
    models: list[str] = None,
) -> list[BenchmarkEntry]:
    """
    Run the benchmark across all models (or a subset).

    Args:
        test_set:       List of dicts with keys "question" and "gold_standard".
        retrieval_fn:   Callable(question: str) -> list[Document].
        prompt_template: Prompt strategy to use for this benchmark run.
        output_path:    Where to save the JSON results.
        models:         Optional list of model names to run, e.g. ["model_a"].
                        If None (default), all three models run.

    Returns:
        List of BenchmarkEntry objects with metrics filled in.
    """
    entries: list[BenchmarkEntry] = []

    for i, item in enumerate(test_set):
        question = item["question"]
        gold = item["gold_standard"]
        logger.info(f"[{i+1}/{len(test_set)}] Benchmarking: {question[:60]}…")

        # Retrieve documents via Person 3's module
        top_k_docs: list[Document] = retrieval_fn(question)

        # Generate with selected models
        results = generate_all_models(
            question, top_k_docs,
            prompt_template=prompt_template,
            models_filter=models,
        )

        # Compute metrics per model
        metrics = {}
        for res in results:
            metrics[res.model_name] = evaluate_result(res, gold)

        entry = BenchmarkEntry(
            question=question,
            gold_standard=gold,
            results=results,
            metrics=metrics,
        )
        entries.append(entry)

    # Persist results
    _save_benchmark(entries, output_path)
    logger.info(f"Benchmark complete. Results saved to '{output_path}'.")
    return entries


def _save_benchmark(entries: list[BenchmarkEntry], path: str):
    serializable = []
    for e in entries:
        serializable.append({
            "question": e.question,
            "gold_standard": e.gold_standard,
            "results": [asdict(r) for r in e.results],
            "metrics": e.metrics,
        })
    with open(path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, ensure_ascii=False, indent=2)


# ─────────────────────────────────────────────
# Summary report
# ─────────────────────────────────────────────
def summarize_benchmark(entries: list[BenchmarkEntry]) -> dict:
    """
    Aggregate metrics across all benchmark entries.
    Returns a dict ready for plotting or printing.
    """
    from collections import defaultdict
    import statistics

    agg = defaultdict(lambda: defaultdict(list))
    for entry in entries:
        for model_name, m in entry.metrics.items():
            for metric, value in m.items():
                if isinstance(value, (int, float)):
                    agg[model_name][metric].append(value)

    summary = {}
    for model_name, metrics in agg.items():
        summary[model_name] = {
            k: round(statistics.mean(v), 4) for k, v in metrics.items()
        }

    logger.info("=== BENCHMARK SUMMARY ===")
    for model, scores in summary.items():
        logger.info(f"  {model}: {scores}")

    return summary


def print_comparison_table(summary: dict):
    """Print a markdown-style comparison table to stdout."""
    models = list(summary.keys())
    metrics = ["bleu", "rouge_l", "bertscore", "latency_seconds"]

    header = "| Metric           | " + " | ".join(f"{m:>12}" for m in models) + " |"
    sep    = "|" + "-" * 18 + "|" + "|".join(["-" * 14] * len(models)) + "|"
    print(header)
    print(sep)
    for metric in metrics:
        row = f"| {metric:<16} | "
        row += " | ".join(f"{summary[m].get(metric, 0.0):>12.4f}" for m in models)
        row += " |"
        print(row)


# ─────────────────────────────────────────────
# Hybrid treatment helper — pre-built prompt
# ─────────────────────────────────────────────
def generate_with_prompt(prompt: str, model_name: str = "model_b") -> dict:
    """
    Generate from a fully pre-built prompt string (used by hybrid treatment).
    model_a (FLAN seq2seq) is not supported here — falls back to model_b.
    """
    if model_name == "model_a":
        model_name = "model_b"

    model_ids = {
        "model_a": ModelRegistry.MODEL_A_ID,
        "model_b": ModelRegistry.MODEL_B_ID,
        "model_c": ModelRegistry.MODEL_C_ID,
    }
    try:
        raw_text, latency = _registry.generate(model_name, prompt)
        response, safe = apply_safety_filter(raw_text)
        return {
            "response": response,
            "model": model_name,
            "model_id": model_ids.get(model_name, "unknown"),
            "latency": round(latency, 3),
            "safe": safe,
            "error": None,
        }
    except Exception as e:
        return {
            "response": "",
            "model": model_name,
            "model_id": model_ids.get(model_name, "unknown"),
            "latency": 0.0,
            "safe": False,
            "error": str(e),
        }


# ─────────────────────────────────────────────
# FastAPI-compatible endpoint helper
# ─────────────────────────────────────────────
def ask(
    question: str,
    top_k_docs: list[Document],
    model_name: str = "model_a",
    prompt_template: str = "zero_shot",
) -> dict:
    """
    Single-question endpoint, called by Person 5's FastAPI route POST /ask.

    Returns a JSON-serialisable dict:
    {
        "response": str,
        "model": str,
        "model_id": str,
        "latency": float,
        "safe": bool,
        "prompt_template": str,
        "sources": [{"id": ..., "categorie": ..., "source_reference": ...}, ...]
    }
    """
    result = generate_response(question, top_k_docs, model_name, prompt_template)
    return {
        "response": result.response,
        "model": result.model_name,
        "model_id": result.model_id,
        "latency": result.latency_seconds,
        "safe": result.safe,
        "prompt_template": result.prompt_template,
        "error": result.error,
        "sources": [
            {
                "id": d.id,
                "categorie": d.categorie,
                "type_cancer": d.type_cancer,
                "source_reference": d.source_reference,
            }
            for d in top_k_docs
        ],
    }


# ─────────────────────────────────────────────
# Quick smoke test (run as script)
# ─────────────────────────────────────────────
if __name__ == "__main__":
    logger.info("Running smoke test…")

    # Minimal fake docs (replace with real retrieval in production)
    docs = [
        Document(
            id="ONC-001",
            contenu=(
                "Le protocole AC pour le cancer du sein associe Doxorubicine 60 mg/m² "
                "et Cyclophosphamide 600 mg/m² IV J1, toutes les 3 semaines × 4 cycles."
            ),
            categorie="traitement",
            type_cancer="sein",
            mots_cles=["AC", "doxorubicine", "cyclophosphamide", "chimiothérapie"],
            protocole="Doxorubicine 60 mg/m² + Cyclophosphamide 600 mg/m² J1 / 3 sem × 4",
            source_reference="Guide AMFROM 2024 — p. 47",
        ),
        Document(
            id="ONC-002",
            contenu=(
                "Les effets secondaires fréquents de la chimiothérapie incluent : "
                "nausées, vomissements, alopécie, fatigue, myélosuppression."
            ),
            categorie="suivi",
            type_cancer="général",
            mots_cles=["effets secondaires", "chimiothérapie", "nausées", "alopécie"],
        ),
    ]

    question = "Quel est le protocole AC pour le cancer du sein ?"
    gold = (
        "Le protocole AC associe Doxorubicine 60 mg/m² et Cyclophosphamide 600 mg/m² "
        "IV J1, toutes les 3 semaines pour 4 cycles."
    )

    print("\n── Generating responses for all models ──")
    results = generate_all_models(question, docs, prompt_template="few_shot")

    for res in results:
        print(f"\n[{res.model_name} | {res.prompt_template} | {res.latency_seconds}s]")
        print(res.response[:300])

    print("\n── Evaluating metrics ──")
    for res in results:
        m = evaluate_result(res, gold)
        print(f"{res.model_name}: {m}")

    print("\n── ask() endpoint test ──")
    out = ask(question, docs, model_name="model_a", prompt_template="chain_of_thought")
    print(json.dumps(out, ensure_ascii=False, indent=2))
