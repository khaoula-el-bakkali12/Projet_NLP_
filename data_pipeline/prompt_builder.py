"""
prompt_builder.py — Module de construction de prompts
======================================================

Génère des prompts enrichis pour le LLM à partir des documents
récupérés et de la question utilisateur.

Trois stratégies disponibles :
  1. Zero-Shot : Contexte + question directe
  2. Few-Shot  : 2 exemples Q/R + contexte + question
  3. Chain-of-Thought : Raisonnement étape par étape

Usage :
    from data_pipeline.prompt_builder import build_prompt, compare_prompts

    prompt = build_prompt(question, documents, strategy="zero_shot")
    all_prompts = compare_prompts(question, documents)
"""

import logging
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Configuration & Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("prompt_builder")


# ============================================================================
# 1. STRATÉGIES DISPONIBLES
# ============================================================================

AVAILABLE_STRATEGIES = ["zero_shot", "few_shot", "chain_of_thought"]


def get_available_strategies() -> List[str]:
    """Retourne la liste des stratégies de prompt disponibles."""
    return list(AVAILABLE_STRATEGIES)


# ============================================================================
# 2. FORMATAGE DES DOCUMENTS
# ============================================================================

def format_documents(documents: List[Dict[str, Any]], max_docs: int = 5) -> str:
    """
    Formate les documents récupérés en un bloc de contexte lisible.

    Chaque document est présenté avec :
      - Titre et identifiant
      - Catégorie et type de cancer
      - Contenu principal
      - Scénario patient (si disponible)
      - Protocole (si disponible)
      - Mots-clés
      - Référence

    Args:
        documents: Liste de documents enrichis (depuis retrieval.py)
        max_docs: Nombre maximum de documents à inclure

    Returns:
        Texte formaté du contexte
    """
    if not documents:
        return "[Aucun document pertinent trouvé.]"

    blocks = []
    for doc in documents[:max_docs]:
        # En-tête du document
        header = f"📄 Document {doc.get('rank', '?')} — {doc.get('id', 'N/A')}"
        header += f" (Score: {doc.get('score_final', 0):.3f})"

        lines = [header]
        lines.append(f"   Titre : {doc.get('titre', 'Sans titre')}")
        lines.append(f"   Catégorie : {doc.get('categorie', 'N/A')} | "
                     f"Type cancer : {doc.get('type_cancer', 'N/A')}")

        if doc.get("sous_type"):
            lines.append(f"   Sous-type : {doc['sous_type']}")
        if doc.get("stade"):
            lines.append(f"   Stade : {doc['stade']}")

        # Contenu principal
        contenu = doc.get("contenu", "")
        if contenu:
            lines.append(f"   Contenu : {contenu}")

        # Protocole (si disponible)
        protocole = doc.get("protocole")
        if protocole:
            lines.append(f"   Protocole : {protocole}")

        # Scénario patient
        scenario = doc.get("scenario_patient", "")
        if scenario:
            lines.append(f"   Scénario patient : {scenario}")

        # Effets secondaires
        effets = doc.get("effets_secondaires", [])
        if effets:
            lines.append(f"   Effets secondaires : {', '.join(effets)}")

        # Métastase
        metastase = doc.get("metastase", "")
        if metastase:
            lines.append(f"   Métastase : {metastase}")

        # Mots-clés
        mots_cles = doc.get("mots_cles", [])
        if mots_cles:
            lines.append(f"   Mots-clés : {', '.join(mots_cles)}")

        # Référence
        reference = doc.get("reference", "")
        if reference:
            lines.append(f"   Référence : {reference}")

        blocks.append("\n".join(lines))

    return "\n\n".join(blocks)


# ============================================================================
# 3. EXEMPLES FEW-SHOT (2 paires Q/R réelles du domaine oncologique)
# ============================================================================

DYNAMIC_FEW_SHOT_BANK = {
    "french": {
        "clinical": {
            "diagnostic": [
                {
                    "question": "Quels sont les critères diagnostiques du cancer du sein HER2 positif ?",
                    "answer": (
                        "Le diagnostic du cancer du sein HER2 positif repose sur "
                        "l'immunohistochimie (IHC) et l'hybridation in situ. Les critères sont :\n"
                        "• Score IHC 3+ : directement positif pour HER2\n"
                        "• Score IHC 2+ : nécessite une confirmation par FISH ou CISH "
                        "(hybridation in situ)\n"
                        "• Score IHC 0 ou 1+ : considéré comme HER2 négatif\n\n"
                        "Le HER2 est surexprimé dans 15 à 20% des cancers du sein. "
                        "Le ciblage thérapeutique par le Trastuzumab a considérablement "
                        "amélioré le pronostic de cette forme de cancer."
                    ),
                },
                {
                    "question": "Comment diagnostique-t-on un cancer colorectal ?",
                    "answer": (
                        "Le diagnostic de certitude du cancer colorectal repose sur la biopsie réalisée "
                        "au cours d'une coloscopie. Les examens complémentaires incluent :\n"
                        "• Le scanner thoraco-abdomino-pelvien (TAP) pour le bilan d'extension\n"
                        "• Le dosage de l'antigène carcino-embryonnaire (ACE)\n"
                        "• En cas de cancer du rectum : une IRM pelvienne et une écho-endoscopie rectale."
                    ),
                }
            ],
            "traitement": [
                {
                    "question": "Quels sont les principaux effets secondaires de la chimiothérapie dans le traitement du cancer colorectal ?",
                    "answer": (
                        "Les principaux effets secondaires de la chimiothérapie dans le "
                        "cancer colorectal varient selon le protocole utilisé :\n\n"
                        "**Protocoles à base de 5-FU (FOLFOX, FOLFIRI) :**\n"
                        "• Nausées et vomissements\n"
                        "• Mucite (inflammation des muqueuses)\n"
                        "• Diarrhée\n"
                        "• Neutropénie (baisse des globules blancs)\n\n"
                        "**Spécifiques à l'Oxaliplatine (FOLFOX) :**\n"
                        "• Neuropathie périphérique (engourdissements, fourmillements)\n"
                        "• Sensibilité au froid\n\n"
                        "**Spécifiques à l'Irinotécan (FOLFIRI) :**\n"
                        "• Diarrhée retardée (potentiellement sévère)\n"
                        "• Syndrome cholinergique aigu\n\n"
                        "Une surveillance régulière de la NFS (Numération Formule Sanguine) "
                        "est indispensable pendant le traitement."
                    ),
                },
                {
                    "question": "Quel est le traitement de première ligne pour un cancer du sein HER2+ métastatique ?",
                    "answer": (
                        "Le traitement de première ligne du cancer du sein HER2+ métastatique repose sur la double "
                        "inhibition de HER2 combinée à une chimiothérapie :\n"
                        "• Association de Trastuzumab (anti-HER2), Pertuzumab (anti-HER2) et un Taxane (généralement le Docétaxel).\n"
                        "• Ce protocole (CLEOPATRA) a démontré une amélioration significative de la survie globale.\n"
                        "• Une évaluation de la fonction cardiaque (fraction d'éjection ventriculaire gauche) est obligatoire avant et tous les 3 mois pendant le traitement par Trastuzumab/Pertuzumab."
                    ),
                }
            ],
            "suivi": [
                {
                    "question": "Quel est le protocole de suivi après traitement d'un cancer du sein précoce ?",
                    "answer": (
                        "Le suivi après traitement curatif d'un cancer du sein précoce comprend :\n"
                        "• Une consultation clinique tous les 3 à 6 mois pendant les 2 premières années, puis tous les 6 à 12 mois pendant les 3 années suivantes, puis annuellement.\n"
                        "• Une mammographie annuelle unilatérale ou bilatérale, éventuellement complétée par une échographie mammaire.\n"
                        "• La surveillance clinique de la tolérance de l'hormonothérapie si prescrite."
                    ),
                },
                {
                    "question": "Comment s'organise la surveillance après résection d'un cancer colorectal ?",
                    "answer": (
                        "La surveillance post-traitement d'un cancer colorectal réséqué comprend :\n"
                        "• Examen clinique et dosage de l'ACE tous les 3 mois pendant 3 ans, puis tous les 6 mois pendant 2 ans.\n"
                        "• Scanner thoraco-abdomino-pelvien tous les 3 à 6 mois pendant 3 ans, puis tous les 6 à 12 mois pendant 2 ans.\n"
                        "• Une coloscopie de contrôle à 1 an, puis à 3 ans, puis tous les 5 ans si normale."
                    ),
                }
            ],
            "general": [
                {
                    "question": "Quels sont les facteurs pronostiques du cancer du sein ?",
                    "answer": (
                        "Les principaux facteurs pronostiques du cancer du sein sont :\n"
                        "1. La taille de la tumeur (T) et l'envahissement ganglionnaire (N)\n"
                        "2. Le grade histoprognostique SBR (Scarff-Bloom-Richardson)\n"
                        "3. Le statut des récepteurs hormonaux (œstrogènes et progestérone)\n"
                        "4. L'expression de l'oncogène HER2\n"
                        "5. L'indice de prolifération Ki-67."
                    ),
                },
                {
                    "question": "Quelle est la différence entre un traitement adjuvant et néoadjuvant ?",
                    "answer": (
                        "• Un traitement **néoadjuvant** est administré *avant* le traitement principal (généralement la chirurgie) pour réduire la taille tumorale et évaluer la chimiosensibilité.\n"
                        "• Un traitement **adjuvant** est administré *après* la chirurgie pour détruire les micrométastases résiduelles et diminuer le risque de récidive."
                    ),
                }
            ]
        },
        "general": [
            {
                "question": "Qu'est-ce que le cancer et comment se développe-t-il ?",
                "answer": (
                    "Le cancer est une maladie caractérisée par la prolifération incontrôlée et désordonnée de cellules anormales.\n"
                    "Ces cellules résultent de mutations de l'ADN qui échappent aux mécanismes normaux de régulation et de mort cellulaire (apoptose).\n"
                    "Elles peuvent former une masse (tumeur) et envahir les tissus voisins ou migrer via le sang/la lymphe pour former des métastases."
                ),
            },
            {
                "question": "Quels sont les principaux facteurs de risque généraux de cancer ?",
                "answer": (
                    "Les facteurs de risque majeurs de cancer incluent :\n"
                    "• Le tabagisme (première cause évitable de cancer)\n"
                    "• La consommation d'alcool\n"
                    "• Une alimentation déséquilibrée et le surpoids\n"
                    "• L'exposition aux rayons UV (soleil) et à certains agents chimiques/professionnels\n"
                    "• Des facteurs génétiques et familiaux (ex: mutations BRCA)."
                ),
            }
        ]
    },
    "arabic": {
        "clinical": {
            "diagnostic": [
                {
                    "question": "كيف يتم تشخيص سرطان الثدي؟",
                    "answer": (
                        "يتضمن تشخيص سرطان الثدي الخطوات التالية:\n"
                        "1. الفحص السريري للثدي من قبل الطبيب.\n"
                        "2. الفحص بالأشعة: تصوير الثدي بالأشعة (الماموجرام) والموجات فوق الصوتية (الإيكو).\n"
                        "3. خزعة الإبرة (Biopsy): وهي الفحص الوحيد الذي يؤكد وجود خلايا سرطانية ويحدد نوعها ومستقبلاتها الهرمونية (ER, PR, HER2)."
                    ),
                },
                {
                    "question": "ما هي الفحوصات اللازمة لتحديد مرحلة سرطان القولون؟",
                    "answer": (
                        "لتحديد مرحلة سرطان القولون والمستقيم (Staging)، يتم إجراء الفحوصات التالية:\n"
                        "• الأشعة المقطعية للصدر والبطن والحوض (CT TAP) للكشف عن وجود نقائل.\n"
                        "• تحليل المؤشر السرطاني CEA في الدم.\n"
                        "• تصوير الرنين المغناطيسي للحوض (MRI) أو السونار الداخلي (EUS) في حالات سرطان المستقيم."
                    ),
                }
            ],
            "traitement": [
                {
                    "question": "ما هي الآثار الجانبية للعلاج الكيميائي لسرطان الثدي؟",
                    "answer": (
                        "تشمل الآثار الجانبية الشائعة للعلاج الكيميائي:\n"
                        "• الغثيان والقيء وفقدان الشهية.\n"
                        "• تساقط الشعر المؤقت.\n"
                        "• التعب الشديد والإرهاق.\n"
                        "• انخفاض كريات الدم البيضاء (مما يزيد خطر الإصابة بالعدوى).\n"
                        "• تقرحات الفم وتغيرات في التذوق."
                    ),
                },
                {
                    "question": "ما هو علاج سرطان الثدي الإيجابي لـ HER2؟",
                    "answer": (
                        "يعتمد علاج سرطان الثدي الإيجابي لـ HER2 على مرحلة المرض، ويشمل بشكل أساسي:\n"
                        "• العلاج الموجه (Targeted Therapy) مثل التراستوزوماب (Trastuzumab/Herceptin) والبيرتوزوماب.\n"
                        "• العلاج الكيميائي المصاحب.\n"
                        "• الجراحة والعلاج الإشعاعي حسب حجم الأورام وموقعها."
                    ),
                }
            ],
            "suivi": [
                {
                    "question": "ما هو بروتوكول المتابعة بعد علاج سرطان الثدي؟",
                    "answer": (
                        "تتضمن المتابعة بعد الشفاء من سرطان الثدي ما يلي:\n"
                        "• فحص سريري كل 3 إلى 6 أشهر في أول سنتين، ثم كل 6 إلى 12 شهر حتى 5 سنوات، ثم سنوياً.\n"
                        "• تصوير الماموجرام للثدي سنوياً بشكل دوري.\n"
                        "• مراقبة الآثار الجانبية للعلاج الهرموني إن وجد."
                    ),
                },
                {
                    "question": "كيف تتم المتابعة بعد جراحة سرطان القولون؟",
                    "answer": (
                        "تشمل المتابعة بعد استئصال ورم القولون:\n"
                        "• زيارة الطبيب وإجراء فحص CEA كل 3 أشهر لمدة 3 سنوات.\n"
                        "• أشعة مقطعية (CT) كل 6 إلى 12 شهراً.\n"
                        "• منظار القولون بعد سنة من الجراحة، ثم كل 3 إلى 5 سنوات حسب النتائج."
                    ),
                }
            ],
            "general": [
                {
                    "question": "ما الفرق بين العلاج الكيميائي المساعد والقبل مساعد؟",
                    "answer": (
                        "• العلاج القبل مساعد (Neoadjuvant): يُعطى قبل الجراحة لتصغير حجم الورم وتسهيل استئصاله.\n"
                        "• العلاج المساعد (Adjuvant): يُعطى بعد الجراحة للقضاء على أي خلايا سرطانية متبقية وتقليل خطر الارتداد."
                    ),
                },
                {
                    "question": "ما هي عوامل الخطورة للإصابة بالسرطان؟",
                    "answer": (
                        "تشمل عوامل الخطورة الرئيسية:\n"
                        "• التقدم في السن والتاريخ العائلي للمرض.\n"
                        "• التدخين واستهلاك الكحول.\n"
                        "• السمنة والنظام الغذائي غير الصحي.\n"
                        "• التعرض للمواد المسرطنة أو الأشعة فوق البنفسجية."
                    ),
                }
            ]
        },
        "general": [
            {
                "question": "ما هو مرض السرطان وكيف ينشأ؟",
                "answer": (
                    "السرطان هو نمو غير طبيعي وغير منضبط للخلايا في الجسم.\n"
                    "يحدث نتيجة طفرات جينية في الحمض النووي (DNA) تؤدي إلى فقدان الخلايا للتحكم في نموها وانقسامها، وتجنب الموت الخلوي المبرمج، مما يؤدي لتشكل ورم يمكن أن ينتشر إلى الأعضاء المجاورة أو البعيدة."
                ),
            },
            {
                "question": "ما هي أعراض السرطان العامة؟",
                "answer": (
                    "تشمل الأعراض العامة التي تستدعي استشارة الطبيب:\n"
                    "• فقدان الوزن غير المبرر وسريع.\n"
                    "• التعب والإرهاق المستمر.\n"
                    "• ظهور كتلة أو انتفاخ غير طبيعي تحت الجلد.\n"
                    "• تغيرات في عادات الإخراج أو التبول.\n"
                    "• السعال المستمر أو صعوبة البلع."
                ),
            }
        ]
    },
    "english": {
        "clinical": {
            "diagnostic": [
                {
                    "question": "What are the diagnostic criteria for HER2-positive breast cancer?",
                    "answer": (
                        "The diagnosis of HER2-positive breast cancer is established using immunohistochemistry (IHC) and in situ hybridization (ISH):\n"
                        "• IHC score of 3+ is considered positive.\n"
                        "• IHC score of 2+ is equivocal and requires testing with FISH or CISH to verify gene amplification.\n"
                        "• IHC score of 0 or 1+ is considered negative."
                    ),
                },
                {
                    "question": "How is colorectal cancer diagnosed?",
                    "answer": (
                        "Colorectal cancer diagnosis relies on pathological biopsy via colonoscopy. Additional tests for staging include:\n"
                        "• Contrast-enhanced CT scan of the chest, abdomen, and pelvis (CAP).\n"
                        "• Serum CEA tumor marker levels.\n"
                        "• Pelvic MRI or endorectal ultrasound (EUS) for rectal cancers."
                    ),
                }
            ],
            "traitement": [
                {
                    "question": "What are the side effects of FOLFOX chemotherapy for colorectal cancer?",
                    "answer": (
                        "Common side effects of FOLFOX chemotherapy include:\n"
                        "• Peripheral neuropathy (numbness/tingling in hands and feet, cold sensitivity due to Oxaliplatin).\n"
                        "• Nausea, vomiting, and diarrhea.\n"
                        "• Neutropenia and increased infection risk.\n"
                        "• Fatigue and hair thinning."
                    ),
                },
                {
                    "question": "What is the first-line treatment for metastatic HER2+ breast cancer?",
                    "answer": (
                        "The standard first-line treatment for metastatic HER2+ breast cancer is dual HER2 blockade combined with chemotherapy:\n"
                        "• Trastuzumab plus Pertuzumab combined with a Taxane (usually Docetaxel).\n"
                        "• Regular monitoring of cardiac function (LVEF) is required every 3 months."
                    ),
                }
            ],
            "suivi": [
                {
                    "question": "What is the follow-up schedule after curative breast cancer treatment?",
                    "answer": (
                        "The typical follow-up schedule includes:\n"
                        "• Clinical examination every 3-6 months for the first 2 years, every 6-12 months for years 3-5, and annually thereafter.\n"
                        "• Annual mammogram of the remaining breast tissue.\n"
                        "• Periodic monitoring for patients on adjuvant endocrine therapy."
                    ),
                },
                {
                    "question": "What is the surveillance protocol after colorectal cancer resection?",
                    "answer": (
                        "Surveillance following curative resection of colorectal cancer involves:\n"
                        "• History and physical exam plus CEA test every 3 months for 3 years, then every 6 months for 2 years.\n"
                        "• CAP CT scans every 6-12 months for 5 years.\n"
                        "• Surveillance colonoscopy at 1 year, 3 years, and then every 5 years."
                    ),
                }
            ],
            "general": [
                {
                    "question": "What is the difference between adjuvant and neoadjuvant therapy?",
                    "answer": (
                        "• **Neoadjuvant therapy** is given *before* the primary treatment (usually surgery) to shrink the tumor and assess responsiveness.\n"
                        "• **Adjuvant therapy** is given *after* surgery to eliminate micro-metastatic disease and reduce the risk of recurrence."
                    ),
                },
                {
                    "question": "What are the main prognostic factors in breast cancer?",
                    "answer": (
                        "Key prognostic factors in breast cancer include tumor size, lymph node involvement, histopathological grade (e.g., Nottingham score), hormone receptor status (ER/PR), HER2 expression, and proliferation index (Ki-67)."
                    ),
                }
            ]
        },
        "general": [
            {
                "question": "What is cancer and how does it develop?",
                "answer": (
                    "Cancer is a disease caused by the uncontrolled division of abnormal cells.\n"
                    "It occurs due to genetic mutations in DNA that bypass normal cell cycle regulation and programmed cell death (apoptosis). These cells can form tumors and spread to other parts of the body."
                ),
            },
            {
                "question": "What are the general risk factors for cancer?",
                "answer": (
                    "General risk factors for cancer include tobacco use, alcohol consumption, poor diet and obesity, physical inactivity, UV radiation exposure, occupational carcinogens, and inherited genetic mutations (such as BRCA1/2)."
                ),
            }
        ]
    }
}

# Maintenir FEW_SHOT_EXAMPLES pour compatibilité descendante
FEW_SHOT_EXAMPLES = [
    DYNAMIC_FEW_SHOT_BANK["french"]["clinical"]["diagnostic"][0],
    DYNAMIC_FEW_SHOT_BANK["french"]["clinical"]["traitement"][0],
]


def get_clinical_subcategory(question: str) -> str:
    """
    Détermine la sous-catégorie clinique d'une question.
    Retourne "diagnostic", "traitement", "suivi" ou "general".
    """
    question_lower = question.lower()
    
    # Termes liés au diagnostic
    diag_terms = [
        "diagnostic", "diagnostique", "diagnose", "diagnostiquer", "تشخيص",
        "stade", "stage", "grading", "classement", "score", "index",
        "scanner", "irm", "ct", "mri", "pet", "biopsy", "biopsie", "فحص",
        "her2", "receptor", "recepteur", "brca", "mutation"
    ]
    
    # Termes liés au traitement
    traitement_terms = [
        "traitement", "treatment", "علاج",
        "therapie", "therapy", "cure", "therapeutique",
        "chimiotherapie", "chemo", "chemotherapy", "كيماوي",
        "radiotherapie", "radiation", "rayons",
        "immunotherapie", "immuno", "immunotherapy",
        "hormonotherapie", "hormone", "hormonal",
        "protocole", "protocol", "protocolle", "dosage", "dose", "جرعة",
        "schema", "regimen", "نظام", "effet secondaire", "side effect", "الآثار الجانبية",
        "toxicite", "toxicity", "complications"
    ]
    
    # Termes liés au suivi/surveillance/pronostic
    suivi_terms = [
        "suivi", "surveillance", "follow-up", "follow up", "متابعة",
        "survie", "survival", "pronostic", "prognosis", "توقعات"
    ]
    
    # Compter les occurrences
    diag_score = sum(1 for term in diag_terms if term in question_lower)
    traitement_score = sum(1 for term in traitement_terms if term in question_lower)
    suivi_score = sum(1 for term in suivi_terms if term in question_lower)
    
    max_score = max(diag_score, traitement_score, suivi_score)
    if max_score == 0:
        return "general"
        
    if max_score == diag_score:
        return "diagnostic"
    elif max_score == traitement_score:
        return "traitement"
    else:
        return "suivi"


def select_few_shot_examples(question: str) -> List[Dict[str, str]]:
    """
    Sélectionne dynamiquement les deux meilleurs exemples few-shot
    en fonction de la langue, de l'intention et de la sous-catégorie.
    """
    from data_pipeline.nlp_query_processor import detect_language, classify_intent
    
    lang = detect_language(question)
    # Si la langue détectée est "mixed" ou non supportée, on choisit "french" par défaut
    if lang not in ["french", "arabic", "english"]:
        lang = "french"
        
    intent_info = classify_intent(question)
    intent = intent_info.get("intent", "general")
    
    # Récupérer les exemples pour la langue correspondante
    lang_bank = DYNAMIC_FEW_SHOT_BANK.get(lang, DYNAMIC_FEW_SHOT_BANK["french"])
    
    if intent == "general":
        # Retourne les exemples généraux de la langue
        examples = lang_bank.get("general", [])
        return examples[:2]
        
    # Si clinique, on cherche par sous-catégorie
    subcategory = get_clinical_subcategory(question)
    clinical_bank = lang_bank.get("clinical", {})
    
    # Essayer de récupérer les exemples de la sous-catégorie clinique spécifique
    selected = list(clinical_bank.get(subcategory, []))
    
    # Si on a moins de 2 exemples, on complète avec les exemples de "general" clinique
    if len(selected) < 2 and subcategory != "general":
        for ex in clinical_bank.get("general", []):
            if ex not in selected:
                selected.append(ex)
                if len(selected) == 2:
                    break
                    
    # Si on a toujours moins de 2 exemples, on complète avec n'importe quel autre exemple clinique
    if len(selected) < 2:
        for sub in ["traitement", "diagnostic", "suivi", "general"]:
            if sub != subcategory:
                for ex in clinical_bank.get(sub, []):
                    if ex not in selected:
                        selected.append(ex)
                        if len(selected) == 2:
                            break
            if len(selected) == 2:
                break
                
    # Si toujours moins de 2, on complète avec les exemples généraux
    if len(selected) < 2:
        for ex in lang_bank.get("general", []):
            if ex not in selected:
                selected.append(ex)
                if len(selected) == 2:
                    break
                    
    return selected[:2]


# ============================================================================
# 4. TEMPLATES DE PROMPT
# ============================================================================

def _build_zero_shot_prompt(question: str, context: str) -> str:
    """
    Template Zero-Shot : Contexte + question directe.

    Approche minimaliste — le LLM répond directement à partir du
    contexte fourni, sans exemples ni instructions de raisonnement.
    """
    prompt = (
        "Tu es un assistant médical expert spécialisé en oncologie. "
        "Tu réponds aux questions médicales en te basant strictement "
        "sur le contexte fourni ci-dessous. Si l'information n'est pas "
        "disponible dans le contexte, indique-le clairement.\n\n"
        "### Contexte :\n"
        f"{context}\n\n"
        "### Question :\n"
        f"{question}\n\n"
        "### Réponse :"
    )
    return prompt


def _build_few_shot_prompt(
    question: str,
    context: str,
    examples: Optional[List[Dict[str, str]]] = None,
) -> str:
    """
    Template Few-Shot : 2 exemples Q/R + contexte + question.

    Les exemples guidés aident le LLM à comprendre le format
    et le niveau de détail attendu dans les réponses oncologiques.
    """
    if examples is None:
        examples = select_few_shot_examples(question)

    prompt = (
        "Tu es un assistant médical expert spécialisé en oncologie. "
        "Tu réponds aux questions médicales en te basant sur le contexte "
        "fourni. Voici des exemples de questions-réponses pour illustrer "
        "le format et le niveau de détail attendu.\n\n"
    )

    # Ajouter les exemples
    for i, example in enumerate(examples, 1):
        prompt += f"### Exemple {i} :\n"
        prompt += f"**Question** : {example['question']}\n"
        prompt += f"**Réponse** : {example['answer']}\n\n"

    # Contexte et question réelle
    prompt += (
        "---\n\n"
        "Maintenant, réponds à la question suivante en utilisant le même "
        "format détaillé que les exemples ci-dessus.\n\n"
        "### Contexte :\n"
        f"{context}\n\n"
        "### Question :\n"
        f"{question}\n\n"
        "### Réponse :"
    )
    return prompt


def _build_chain_of_thought_prompt(question: str, context: str) -> str:
    """
    Template Chain-of-Thought : Raisonnement étape par étape.

    Encourage le LLM à décomposer son raisonnement avant de
    produire la réponse finale, ce qui améliore la précision
    sur les questions complexes (multi-facteurs, diagnostic
    différentiel, choix de protocole).
    """
    prompt = (
        "Tu es un assistant médical expert spécialisé en oncologie. "
        "Tu dois répondre à la question posée en te basant strictement "
        "sur le contexte fourni.\n\n"
        "**Important** : Avant de donner ta réponse finale, raisonne "
        "étape par étape en suivant cette démarche :\n"
        "1. Identifier les informations clés présentes dans le contexte\n"
        "2. Relier ces informations à la question posée\n"
        "3. Évaluer la pertinence et la complétude des informations\n"
        "4. Formuler une réponse structurée et complète\n\n"
        "### Contexte :\n"
        f"{context}\n\n"
        "### Question :\n"
        f"{question}\n\n"
        "### Raisonnement étape par étape :\n\n"
        "**Étape 1 — Informations clés identifiées :**\n"
        "[Extraire les éléments pertinents du contexte]\n\n"
        "**Étape 2 — Lien avec la question :**\n"
        "[Relier les informations à ce qui est demandé]\n\n"
        "**Étape 3 — Évaluation :**\n"
        "[Évaluer si le contexte couvre entièrement la question]\n\n"
        "**Étape 4 — Synthèse :**\n"
        "[Construire la réponse finale]\n\n"
        "### Réponse finale :"
    )
    return prompt


# ============================================================================
# 5. API PRINCIPALE : build_prompt()
# ============================================================================

def build_prompt(
    question: str,
    documents: List[Dict[str, Any]],
    strategy: str = "zero_shot",
    max_docs: int = 5,
    examples: Optional[List[Dict[str, str]]] = None,
) -> str:
    """
    Construit un prompt enrichi à partir des documents et de la question.

    Args:
        question: Question de l'utilisateur
        documents: Documents récupérés (depuis retrieval.py)
        strategy: Stratégie de prompt ("zero_shot", "few_shot", "chain_of_thought")
        max_docs: Nombre max de documents dans le contexte
        examples: Exemples personnalisés pour Few-Shot (optionnel)

    Returns:
        Prompt complet prêt à être envoyé au LLM

    Raises:
        ValueError: Si la stratégie n'est pas reconnue
    """
    if strategy not in AVAILABLE_STRATEGIES:
        raise ValueError(
            f"Stratégie inconnue : '{strategy}'. "
            f"Choisir parmi : {AVAILABLE_STRATEGIES}"
        )

    # Formater les documents en contexte
    context = format_documents(documents, max_docs=max_docs)

    # Construire le prompt selon la stratégie
    if strategy == "zero_shot":
        prompt = _build_zero_shot_prompt(question, context)
    elif strategy == "few_shot":
        prompt = _build_few_shot_prompt(question, context, examples)
    elif strategy == "chain_of_thought":
        prompt = _build_chain_of_thought_prompt(question, context)

    logger.info(
        "Prompt construit | Stratégie: %s | Docs: %d | Longueur: %d chars",
        strategy, min(len(documents), max_docs), len(prompt),
    )

    return prompt


# ============================================================================
# 6. COMPARAISON DES PROMPTS
# ============================================================================

def compare_prompts(
    question: str,
    documents: List[Dict[str, Any]],
    max_docs: int = 5,
) -> Dict[str, Any]:
    """
    Génère les prompts pour les 3 stratégies et les compare.

    Retourne un dictionnaire avec :
      - Les 3 prompts générés
      - Statistiques (longueur, nombre de tokens estimé)

    Args:
        question: Question de l'utilisateur
        documents: Documents récupérés

    Returns:
        {
            "question": str,
            "num_documents": int,
            "strategies": {
                "zero_shot": {"prompt": str, "length": int, "estimated_tokens": int},
                "few_shot": {"prompt": str, "length": int, "estimated_tokens": int},
                "chain_of_thought": {"prompt": str, "length": int, "estimated_tokens": int},
            }
        }
    """
    result = {
        "question": question,
        "num_documents": len(documents),
        "strategies": {},
    }

    for strategy in AVAILABLE_STRATEGIES:
        prompt = build_prompt(question, documents, strategy=strategy, max_docs=max_docs)

        result["strategies"][strategy] = {
            "prompt": prompt,
            "length": len(prompt),
            "estimated_tokens": len(prompt) // 4,  # estimation ~4 chars/token
        }

    # Log la comparaison
    logger.info("\n--- Comparaison des prompts ---")
    for strategy, info in result["strategies"].items():
        logger.info(
            "  %-20s | %6d chars | ~%5d tokens",
            strategy, info["length"], info["estimated_tokens"],
        )

    return result


# ============================================================================
# POINT D'ENTRÉE (pour test rapide)
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("PROMPT BUILDER — Test rapide")
    print("=" * 70)

    # Documents simulés
    test_docs = [
        {
            "rank": 1,
            "id": "ONC-001",
            "categorie": "diagnostic",
            "type_cancer": "sein",
            "sous_type": "HER2 positif",
            "stade": "tout stade",
            "titre": "Critères diagnostiques du cancer du sein HER2+",
            "contenu": "Le cancer du sein HER2 positif est défini par une surexpression "
                       "du gène HER2, présent dans 15 à 20% des cancers du sein.",
            "mots_cles": ["sein", "HER2", "IHC", "FISH", "diagnostic"],
            "scenario_patient": "Femme de 48 ans, masse mammaire gauche.",
            "protocole": None,
            "effets_secondaires": [],
            "metastase": "",
            "reference": "Guide AMFROM 2024, Chapitre I",
            "score_final": 0.92,
            "score_faiss_norm": 0.95,
            "score_bm25_norm": 0.85,
        },
        {
            "rank": 2,
            "id": "ONC-005",
            "categorie": "traitement",
            "type_cancer": "sein",
            "sous_type": "HER2 positif",
            "stade": "stade précoce",
            "titre": "Protocole de traitement néoadjuvant du cancer du sein HER2+",
            "contenu": "Le traitement néoadjuvant du cancer du sein HER2+ repose sur "
                       "la chimiothérapie associée au trastuzumab et pertuzumab.",
            "mots_cles": ["sein", "HER2", "trastuzumab", "néoadjuvant"],
            "scenario_patient": "",
            "protocole": "TCHP (Docétaxel, Carboplatine, Trastuzumab, Pertuzumab)",
            "effets_secondaires": ["cardiotoxicité", "neutropénie"],
            "metastase": "",
            "reference": "Guide AMFROM 2024, Chapitre I",
            "score_final": 0.88,
            "score_faiss_norm": 0.90,
            "score_bm25_norm": 0.82,
        },
    ]

    question = "Quel est le traitement du cancer du sein HER2+ ?"

    # Test chaque stratégie
    for strategy in AVAILABLE_STRATEGIES:
        print(f"\n{'='*70}")
        print(f"STRATÉGIE : {strategy.upper()}")
        print(f"{'='*70}")
        prompt = build_prompt(question, test_docs, strategy=strategy)
        print(prompt[:800])
        print("..." if len(prompt) > 800 else "")
        print(f"\n[Longueur : {len(prompt)} caractères, ~{len(prompt)//4} tokens]")

    # Comparaison
    print(f"\n{'='*70}")
    print("COMPARAISON")
    print(f"{'='*70}")
    comparison = compare_prompts(question, test_docs)
    for strategy, info in comparison["strategies"].items():
        print(f"  {strategy:20s} : {info['length']:6d} chars | ~{info['estimated_tokens']:5d} tokens")

    print("\n" + "=" * 70)
    print("Test terminé !")
    print("=" * 70)
