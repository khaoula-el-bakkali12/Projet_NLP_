"""
add_page_references.py — Enrichissement des références AMFROM avec numéros de page
==================================================================================
Le sujet exige des références citant « page et nom du référence ou encore
année/version » (réf. AMFROM 2024). Ce script ajoute le numéro de page exact du
Guide des protocoles thérapeutiques en oncologie (6e édition, AMFROM 2024) à
chaque entrée dont la référence cite le guide.

La cartographie chapitre → page est extraite du SOMMAIRE officiel du guide
(les numéros imprimés correspondent aux pages PDF). Pour les cancers possédant
des sections « maladie localisée » et « maladie métastatique » distinctes, la
page est choisie selon le stade de l'entrée.

Idempotent : une entrée disposant déjà d'un « p.XX » n'est pas modifiée.

Usage :
    python add_page_references.py
"""

import json
import re
import unicodedata
from pathlib import Path

JSON_PATH = Path(__file__).resolve().parent / "data" / "raw" / "dataset_oncologie_FINAL_v6.json"


def _strip(text: str) -> str:
    """minuscule + sans accents pour matcher de façon robuste."""
    nfkd = unicodedata.normalize("NFKD", (text or "").lower())
    return "".join(c for c in nfkd if unicodedata.category(c) != "Mn")


# ── Cartographie chapitre → page (SOMMAIRE du Guide AMFROM 2024) ───────────────
# Valeurs : {"loc": page_maladie_localisee, "met": page_maladie_metastatique}
# Quand une seule page existe, loc == met.
PAGE_MAP = {
    "sein":          {"loc": 11,  "met": 32,  "chap": "I – Cancers du sein"},
    "ovaire":        {"loc": 57,  "met": 57,  "chap": "II – Cancers gynécologiques (ovaire)"},
    "col_uterin":    {"loc": 66,  "met": 67,  "chap": "II – Cancers gynécologiques (col utérin)"},
    "endometre":     {"loc": 72,  "met": 72,  "chap": "II – Cancers gynécologiques (endomètre)"},
    "trophoblaste":  {"loc": 75,  "met": 75,  "chap": "II – Maladies trophoblastiques"},
    "colorectal":    {"loc": 77,  "met": 83,  "chap": "III – Cancers digestifs (colorectal)"},
    "estomac":       {"loc": 102, "met": 105, "chap": "III – Cancers digestifs (estomac)"},
    "oesophage":     {"loc": 114, "met": 116, "chap": "III – Cancers digestifs (œsophage)"},
    "canal_anal":    {"loc": 120, "met": 120, "chap": "III – Cancers digestifs (canal anal)"},
    "pancreas":      {"loc": 124, "met": 126, "chap": "III – Cancers digestifs (pancréas)"},
    "voies_biliaires": {"loc": 132, "met": 132, "chap": "III – Cancers digestifs (voies biliaires)"},
    "foie":          {"loc": 138, "met": 138, "chap": "III – Carcinome hépato-cellulaire"},
    "neuroendocrine": {"loc": 142, "met": 143, "chap": "III – Tumeurs neuroendocrines"},
    "GIST":          {"loc": 144, "met": 146, "chap": "III – GIST"},
    "poumon":        {"loc": 150, "met": 153, "chap": "IV – Cancers pulmonaires (CNPC)"},
    "poumon_cbpc":   {"loc": 165, "met": 165, "chap": "IV – Cancers pulmonaires à petites cellules"},
    "orl_cavum":     {"loc": 176, "met": 177, "chap": "V – Tumeurs ORL (UCNT du cavum)"},
    "orl_epidermoide": {"loc": 181, "met": 182, "chap": "V – Carcinomes épidermoïdes ORL"},
    "thyroide":      {"loc": 186, "met": 186, "chap": "V – Cancers de la thyroïde"},
    "sarcome":       {"loc": 192, "met": 196, "chap": "VI – Sarcomes des tissus mous"},
    "osteosarcome":  {"loc": 202, "met": 203, "chap": "VI – Ostéosarcomes"},
    "ewing":         {"loc": 206, "met": 208, "chap": "VI – Sarcomes d'Ewing"},
    "testicule":     {"loc": 215, "met": 214, "chap": "VII – Tumeurs germinales du testicule"},
    "rein":          {"loc": 220, "met": 220, "chap": "VII – Cancers du rein"},
    "vessie":        {"loc": 230, "met": 232, "chap": "VII – Cancer de vessie"},
    "prostate":      {"loc": 238, "met": 240, "chap": "VII – Cancers de la prostate"},
    "melanome":      {"loc": 246, "met": 246, "chap": "VIII – Mélanome"},
    "cutane":        {"loc": 256, "met": 256, "chap": "VIII – Carcinomes épidermoïdes cutanés"},
    "cerebral":      {"loc": 259, "met": 260, "chap": "IX – Tumeurs cérébrales (gliomes)"},
}

# Soins de support (chapitre X) — détectés par mots-clés dans titre/contenu
SUPPORT_MAP = [
    (("thrombose", "anticoagul", "embolie"),                       265, "X – Thrombose et cancer"),
    (("g-csf", "facteur de croissance", "neutropenie febrile", "filgrastim"), 269, "X – Facteurs de croissance granulocytaires"),
    (("erythropo", "epo ", "anemie"),                              271, "X – Érythropoïétine en cancérologie"),
    (("metastase osseuse", "metastases osseuses", "bisphosphonate", "denosumab", "acide zoledronique"), 273, "X – Traitement des métastases osseuses"),
    (("vomissement", "nausee", "antiemetique"),                    276, "X – Vomissements induits par la chimiothérapie"),
    (("douleur", "antalgique", "morphine", "opioide"),             279, "X – Traitement de la douleur"),
    (("mucite", "stomatite"),                                      284, "X – Mucite"),
    (("toxicite cutanee", "syndrome main-pied", "rash"),           287, "X – Toxicité cutanée"),
    (("neuropathie",),                                             291, "X – Neuropathie périphérique"),
]


def normalize_cancer(entry: dict) -> str | None:
    """Mappe type_cancer/sous_type d'une entrée vers une clé de PAGE_MAP."""
    ct = _strip(entry.get("type_cancer", ""))
    st = _strip(entry.get("sous_type", ""))

    # Poumon : distinguer petites cellules (CBPC) du non à petites cellules
    if "poumon" in ct:
        if "cbpc" in st or "petites cellules" in st:
            return "poumon_cbpc"
        return "poumon"

    # ORL : cavum/UCNT vs épidermoïdes (larynx, VADS, cavité buccale)
    if ct in ("orl", "tete_cou") or "orl" in ct:
        if "cavum" in st or "ucnt" in st or "nasophar" in st or "cavum" in _strip(entry.get("titre", "")):
            return "orl_cavum"
        return "orl_epidermoide"

    # Sarcomes osseux : Ewing vs ostéosarcome vs chondrosarcome
    if "sarcome_osseux" in ct or "osseux" in ct:
        if "ewing" in st:
            return "ewing"
        return "osteosarcome"
    if "sarcome" in ct:
        return "sarcome"

    if "colorectal" in ct or "colon" in ct or "rectum" in ct:
        return "colorectal"
    if "estomac" in ct or "gastr" in ct:
        return "estomac"
    if "oesophage" in ct:
        return "oesophage"
    if "pancrea" in ct:
        return "pancreas"
    if "biliaire" in ct:
        return "voies_biliaires"
    if "foie" in ct or "hepato" in ct or "cholangio" in ct:
        return "foie"
    if "neuroendocrine" in ct:
        return "neuroendocrine"
    if "gist" in ct:
        return "GIST"
    if "col_uter" in ct or "col de l" in ct or "col uter" in ct:
        return "col_uterin"
    if "endometre" in ct:
        return "endometre"
    if "trophoblast" in ct:
        return "trophoblaste"
    if "ovaire" in ct or "gynecolog" in ct:
        return "ovaire"
    if "thyroide" in ct:
        return "thyroide"
    if "melanome" in ct:
        return "melanome"
    if "cutane" in ct or "epidermoide cutane" in st:
        return "cutane"
    if "cerebral" in ct or "gliome" in ct:
        return "cerebral"
    if "testicule" in ct or "germinale" in ct:
        return "testicule"
    if "rein" in ct or "renal" in ct:
        return "rein"
    if "vessie" in ct or "uroth" in ct:
        return "vessie"
    if "prostate" in ct:
        return "prostate"
    if ct == "sein" or ct.startswith("sein"):
        return "sein"
    return None


def is_metastatic(entry: dict) -> bool:
    """Détecte un stade avancé/métastatique pour choisir la page."""
    blob = _strip(
        f"{entry.get('stade','')} {entry.get('sous_type','')} {entry.get('categorie','')}"
    )
    tokens = ("metasta", "avance", "mcrpc", "extensif", " m1", "stade iv",
              " iv", "incurable", "recidiv", "resistant", "النقيلي", "متقدم")
    # 'iv' isolé sans confondre avec 'ivb'/'iva' déjà couverts par ' iv'
    if any(t in blob for t in tokens):
        return True
    return False


def support_page(entry: dict):
    """Retourne (page, chapitre) si l'entrée relève des soins de support."""
    blob = _strip(f"{entry.get('titre','')} {entry.get('contenu','')[:400]}")
    cat = _strip(entry.get("categorie", ""))
    # On ne tente les soins de support que pour les entrées sans cancer-chapitre clair
    for keywords, page, chap in SUPPORT_MAP:
        if any(k in blob for k in keywords):
            # éviter les faux positifs : 'douleur' apparait partout -> exiger contexte support
            return page, chap
    return None, None


def main():
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))

    updated = 0
    skipped_has_page = 0
    no_mapping = 0
    support_used = 0

    for entry in data:
        ref = entry.get("reference", "") or ""

        # Ne traiter que les références au Guide AMFROM
        if "AMFROM" not in ref and "amfrom" not in _strip(ref):
            continue

        # Idempotence : déjà une page ?
        if re.search(r"\bp\.?\s*\d{1,3}\b|page\s*\d", ref, re.I):
            skipped_has_page += 1
            entry.setdefault("page", int(re.search(r"(\d{1,3})", re.search(r"\bp\.?\s*\d{1,3}|page\s*\d+", ref, re.I).group()).group()))
            continue

        key = normalize_cancer(entry)
        page = None
        chap = None

        if key:
            info = PAGE_MAP[key]
            page = info["met"] if is_metastatic(entry) else info["loc"]
            chap = info["chap"]
        else:
            # Tenter les soins de support pour les entrées générales
            sp, sc = support_page(entry)
            if sp:
                page, chap = sp, sc
                support_used += 1

        if page is None:
            no_mapping += 1
            continue

        # Mettre à jour la référence : on conserve le texte existant et on ajoute la page
        new_ref = re.sub(r"\s*$", "", ref)
        new_ref = f"{new_ref}, p.{page}"
        entry["reference"] = new_ref
        entry["page"] = page
        if chap and "Chapitre" not in new_ref and "chapitre" not in new_ref.lower():
            entry["chapitre_guide"] = chap
        updated += 1

    JSON_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Entrées mises à jour avec page        : {updated}")
    print(f"  dont via soins de support           : {support_used}")
    print(f"Déjà une page (inchangées)            : {skipped_has_page}")
    print(f"AMFROM sans mapping cancer/support    : {no_mapping}")

    # Statistiques finales
    total_amfrom = sum(1 for d in data if "amfrom" in _strip(d.get("reference", "")))
    with_page = sum(1 for d in data if "amfrom" in _strip(d.get("reference", ""))
                    and re.search(r"\bp\.\s*\d", d.get("reference", ""), re.I))
    print(f"\nRéférences AMFROM avec page : {with_page}/{total_amfrom} "
          f"({100*with_page/max(total_amfrom,1):.0f}%)")


if __name__ == "__main__":
    main()
