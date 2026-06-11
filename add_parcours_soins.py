"""
add_parcours_soins.py — Ajout de la catégorie « parcours_de_soins »
===================================================================
Le sujet impose que la base couvre explicitement le « parcours de soins »
(au même titre que diagnostic / traitement / suivi). Cette catégorie était
absente du dataset. Ce script ajoute des entrées « parcours_de_soins »
reformulées (brèves, techniques, pédagogiques) décrivant le parcours
oncologique en 7 phases (consultation → bilan → RCP → plan → traitement →
réévaluation → surveillance), général puis spécifique par localisation.

Les contenus s'appuient sur les recommandations AMFROM 2024 et reprennent,
en les reformulant pour le retrieval, les étapes du parcours patient.

Idempotent : les entrées PARC-* existantes sont remplacées (pas de doublon).

Usage :
    python add_parcours_soins.py
"""

import json
from pathlib import Path

JSON_PATH = Path(__file__).resolve().parent / "data" / "raw" / "dataset_oncologie_FINAL_v6.json"
DATE = "2026-06-11"

# Chaque entrée : parcours de soins type par localisation.
PARCOURS = [
    {
        "id": "PARC-001",
        "type_cancer": "general",
        "sous_type": "parcours oncologique type",
        "titre": "Parcours de soins oncologique type en 7 étapes",
        "contenu": (
            "Le parcours de soins en oncologie suit sept étapes coordonnées. "
            "1) Consultation initiale : anamnèse, examen clinique et suspicion diagnostique. "
            "2) Bilan d'extension : biopsie, imagerie (scanner thoraco-abdomino-pelvien, IRM, TEP) et marqueurs tumoraux pour stadifier la tumeur. "
            "3) RCP (Réunion de Concertation Pluridisciplinaire) : décision collégiale entre oncologues, chirurgiens, radiologues et anatomopathologistes. "
            "4) Plan personnalisé : consultation d'annonce et Programme Personnalisé de Soins (PPS) avec consentement éclairé. "
            "5) Traitement : chimiothérapie, chirurgie, radiothérapie, immunothérapie ou thérapie ciblée selon le protocole retenu. "
            "6) Évaluation de la réponse : réévaluation tumorale selon les critères RECIST, adaptation de la stratégie si nécessaire. "
            "7) Surveillance post-traitement : consultations régulières, marqueurs, imagerie et soins de support à long terme."
        ),
        "protocole": None,
        "effets_secondaires": [],
        "mots_cles": ["parcours de soins", "RCP", "PPS", "bilan d'extension", "RECIST", "surveillance", "consultation d'annonce"],
        "scenario_patient": "Patient adressé pour suspicion de cancer : il suit successivement consultation, bilan d'extension, RCP, annonce, traitement, réévaluation puis surveillance.",
        "reference": "Guide AMFROM 2024 – Organisation du parcours de soins en oncologie",
        "metastase": "Le parcours intègre la prise en charge des formes métastatiques (soins de support précoces, RCP de recours).",
    },
    {
        "id": "PARC-002",
        "type_cancer": "sein",
        "sous_type": "carcinome mammaire",
        "titre": "Parcours de soins du cancer du sein",
        "contenu": (
            "Parcours type du cancer du sein. 1) Consultation : examen des seins et des aires ganglionnaires, évaluation du risque familial (BRCA1/2). "
            "2) Bilan diagnostique : mammographie + échographie, IRM si sein dense ou HER2+, microbiopsie avec récepteurs hormonaux RE/RP, HER2 et Ki-67. "
            "3) RCP sénologique : staging TNM et classification du sous-type moléculaire (Luminal A/B, HER2+, triple négatif), choix néoadjuvant vs adjuvant. "
            "4) Programme personnalisé : protocole adapté (AC-T, EC-T, ou double blocage Trastuzumab + Pertuzumab si HER2+), bilan pré-chimiothérapie et pose de voie veineuse centrale. "
            "5) Traitement : chimiothérapie néoadjuvante puis chirurgie (tumorectomie + curage ou mastectomie) et radiothérapie adjuvante. "
            "6) Réponse : IRM à mi-traitement, recherche d'une réponse complète histologique (pCR), facteur pronostique majeur. "
            "7) Surveillance : mammographie annuelle, hormonothérapie 5 à 10 ans si RE+, surveillance cardiaque sous Trastuzumab."
        ),
        "protocole": "Néoadjuvant : AC×4 → Paclitaxel×12 (± Trastuzumab/Pertuzumab si HER2+) ; surveillance LVEF si anti-HER2.",
        "effets_secondaires": ["cardiotoxicité", "neutropénie", "neuropathie", "alopécie"],
        "mots_cles": ["sein", "parcours de soins", "RCP sénologique", "pCR", "HER2", "hormonothérapie", "mammographie"],
        "scenario_patient": "Femme de 50 ans, masse mammaire : mammographie, biopsie HER2+, RCP, chimiothérapie néoadjuvante, chirurgie, radiothérapie puis surveillance prolongée.",
        "reference": "Guide AMFROM 2024, Chapitre I – Cancers du sein, p.11",
        "metastase": "En cas de maladie métastatique, le parcours bascule vers une prise en charge palliative active (chapitre stades métastatiques, p.32).",
    },
    {
        "id": "PARC-003",
        "type_cancer": "poumon",
        "sous_type": "CBNPC",
        "titre": "Parcours de soins du cancer du poumon (CBNPC)",
        "contenu": (
            "Parcours type du carcinome bronchique non à petites cellules. 1) Consultation : signes d'alerte (toux persistante, hémoptysie, dyspnée), anamnèse tabagique. "
            "2) Bilan diagnostique et moléculaire : TDM thoracique, TEP-scan, biopsie bronchique ou transthoracique, panel NGS obligatoire (EGFR, ALK, ROS1, BRAF, KRAS G12C) et score PD-L1. "
            "3) RCP thoracique : staging UICC 8e édition, évaluation de l'opérabilité (VEMS, ECOG-PS), identification de la mutation driver. "
            "4) Plan thérapeutique : EGFR muté → Osimertinib ; ALK/ROS1 → Alectinib ; PD-L1 ≥ 50 % → Pembrolizumab ; sans driver → platine doublet ± immunothérapie. "
            "5) Traitement systémique : TKI oral en continu ou cycles de chimio-immunothérapie. "
            "6) Réponse : TDM thoracique selon RECIST, biopsie liquide (ctDNA) en cas de progression sous TKI. "
            "7) Surveillance et soins de support : TDM semestriel, aide au sevrage tabagique, soins palliatifs précoces si stade IV."
        ),
        "protocole": "Selon biomarqueur : Osimertinib 80 mg/j (EGFR), Alectinib 600 mg×2/j (ALK), Pembrolizumab 200 mg J1=J21 (PD-L1≥50%).",
        "effets_secondaires": ["toxicité cutanée", "diarrhée", "pneumopathie immuno-induite", "cytopénies"],
        "mots_cles": ["poumon", "CBNPC", "parcours de soins", "NGS", "PD-L1", "thérapie ciblée", "RCP thoracique"],
        "scenario_patient": "Homme de 62 ans, tabagique, toux et amaigrissement : TDM, biopsie, NGS EGFR muté, RCP, Osimertinib puis surveillance.",
        "reference": "Guide AMFROM 2024, Chapitre IV – Cancers pulmonaires (CNPC), p.150",
        "metastase": "Au stade IV, le parcours associe traitement systémique et soins de support précoces (page 153).",
    },
    {
        "id": "PARC-004",
        "type_cancer": "colorectal",
        "sous_type": "côlon et rectum",
        "titre": "Parcours de soins du cancer colorectal",
        "contenu": (
            "Parcours type du cancer colorectal. 1) Consultation : symptômes (rectorragie, troubles du transit, anémie ferriprive), toucher rectal, dosage ACE. "
            "2) Coloscopie et bilan : coloscopie totale avec biopsies (gold standard), TDM thoraco-abdomino-pelvien, IRM pelvienne si rectum, statut RAS/BRAF et MSI/MMR. "
            "3) RCP digestive : staging TNM, résécabilité des métastases hépatiques, MSI-H → immunothérapie en 1re ligne. "
            "4) Plan : côlon stade II-III → chirurgie puis FOLFOX adjuvant ; rectum localement avancé → radiochimiothérapie néoadjuvante puis chirurgie. "
            "5) Traitement : résection carcinologique R0 puis chimiothérapie adjuvante ou traitement métastatique selon RAS/BRAF/MSI. "
            "6) Réponse : TDM selon RECIST, suivi de l'ACE, réévaluation de la résécabilité hépatique. "
            "7) Surveillance : examen clinique + ACE semestriel 5 ans, coloscopie de contrôle à 1 puis 3 ans, dépistage familial si Lynch."
        ),
        "protocole": "FOLFOX (Oxaliplatine 85 mg/m² + Leucovorin + 5-FU) J1=J14 ; ± Bevacizumab ou anti-EGFR si RAS sauvage métastatique.",
        "effets_secondaires": ["neuropathie périphérique", "diarrhée", "neutropénie", "mucite"],
        "mots_cles": ["colorectal", "parcours de soins", "coloscopie", "FOLFOX", "RAS", "MSI", "RCP digestive"],
        "scenario_patient": "Patient de 58 ans, rectorragies : coloscopie + biopsie, TDM, RCP, colectomie puis FOLFOX adjuvant et surveillance.",
        "reference": "Guide AMFROM 2024, Chapitre III – Cancers digestifs (colorectal), p.77",
        "metastase": "Les métastases hépatiques résécables sont rediscutées en RCP (down-staging) ; maladie métastatique p.83.",
    },
    {
        "id": "PARC-005",
        "type_cancer": "ovaire",
        "sous_type": "carcinome épithélial de l'ovaire",
        "titre": "Parcours de soins du cancer de l'ovaire",
        "contenu": (
            "Parcours type du carcinome ovarien, souvent diagnostiqué à un stade avancé. 1) Consultation : distension abdominale, douleurs pelviennes, dosage CA-125 et HE4 (score ROMA). "
            "2) Bilan : TDM thoraco-abdomino-pelvien (carcinose péritonéale), score de résécabilité, test BRCA1/2 germinal et somatique. "
            "3) RCP gynéco-oncologique : objectif de résidu tumoral nul (R0), chirurgie première vs chimiothérapie néoadjuvante selon le score de Fagotti. "
            "4) Plan : Carboplatine AUC5-6 + Paclitaxel × 6 cycles, ± Bevacizumab si stade avancé, maintenance par inhibiteur de PARP (Olaparib) si BRCA muté. "
            "5) Traitement : chirurgie de cytoréduction maximale et chimiothérapie, puis maintenance. "
            "6) Réponse : CA-125 après chaque cycle, TDM en fin de traitement, distinction platine-sensible / platine-résistant. "
            "7) Surveillance : CA-125 et examen clinique trimestriels, poursuite de la maintenance, conseil génétique familial."
        ),
        "protocole": "Carboplatine AUC5 + Paclitaxel 175 mg/m² J1=J21 × 6 ; maintenance Olaparib 300 mg×2/j si BRCA muté.",
        "effets_secondaires": ["neuropathie", "asthénie", "cytopénies", "hypertension (Bevacizumab)"],
        "mots_cles": ["ovaire", "parcours de soins", "CA-125", "cytoréduction", "BRCA", "PARP", "RCP gynécologique"],
        "scenario_patient": "Femme de 60 ans, ascite et CA-125 élevé : TDM, chirurgie de cytoréduction, chimiothérapie, maintenance Olaparib (BRCA+) et surveillance.",
        "reference": "Guide AMFROM 2024, Chapitre II – Cancers gynécologiques (ovaire), p.57",
        "metastase": "La carcinose péritonéale et les métastases conditionnent la stratégie chirurgicale et la maintenance.",
    },
    {
        "id": "PARC-006",
        "type_cancer": "prostate",
        "sous_type": "adénocarcinome prostatique",
        "titre": "Parcours de soins du cancer de la prostate",
        "contenu": (
            "Parcours type du cancer de la prostate. 1) Consultation : dosage PSA, toucher rectal, score IPSS, antécédents familiaux. "
            "2) Bilan : IRM multiparamétrique (score PI-RADS), biopsies écho-guidées avec fusion IRM, score de Gleason / groupe ISUP, scintigraphie osseuse si haut risque. "
            "3) RCP urologique : stratification du risque selon D'Amico, estimation de l'espérance de vie, discussion surveillance active vs traitement curatif. "
            "4) Plan : faible risque → surveillance active ; risque intermédiaire/haut → prostatectomie ou radiothérapie + hormonothérapie ; métastatique → ADT + Enzalutamide/Apalutamide ou Docétaxel. "
            "5) Traitement : prostatectomie totale ou radiothérapie conformationnelle, hormonothérapie (ADT) par analogue LH-RH. "
            "6) Réponse : PSA nadir post-traitement, définition de la rechute biochimique, TEP-PSMA si rechute. "
            "7) Surveillance : PSA et testostérone semestriels, prévention de l'ostéoporose (densitométrie) et du risque cardiovasculaire sous ADT."
        ),
        "protocole": "ADT (Leuproréline/Goséréline) ± Enzalutamide 160 mg/j ; surveillance castration (testostérone < 50 ng/dL).",
        "effets_secondaires": ["bouffées de chaleur", "ostéoporose", "asthénie", "troubles métaboliques"],
        "mots_cles": ["prostate", "parcours de soins", "PSA", "Gleason", "PI-RADS", "ADT", "RCP urologique"],
        "scenario_patient": "Homme de 68 ans, PSA élevé : IRM, biopsies Gleason 7, RCP, radiothérapie + hormonothérapie puis surveillance du PSA.",
        "reference": "Guide AMFROM 2024, Chapitre VII – Cancers de la prostate, p.238",
        "metastase": "Le cancer métastatique résistant à la castration (mCRPC) relève d'une intensification (page 240).",
    },
    {
        "id": "PARC-007",
        "type_cancer": "col_uterin",
        "sous_type": "carcinome du col utérin",
        "titre": "Parcours de soins du cancer du col utérin",
        "contenu": (
            "Parcours type du cancer du col utérin. 1) Consultation : métrorragies, leucorrhées, examen au spéculum, frottis cervico-vaginal et test HPV. "
            "2) Bilan : biopsie cervicale (confirmation histologique), IRM pelvienne (référence pour le staging local), TDM pour les ganglions, marqueur SCC. "
            "3) RCP gynéco-oncologique : staging FIGO 2018, opérabilité (chirurgie si IB1-IIA1, radiochimiothérapie si stade ≥ IB2). "
            "4) Plan : stade précoce → hystérectomie radicale (Wertheim) + curage ; stade avancé → radiochimiothérapie concomitante (Cisplatine hebdomadaire + RT) puis curiethérapie. "
            "5) Traitement : chirurgie ou radiochimiothérapie + curiethérapie de haut débit de dose. "
            "6) Réponse : IRM pelvienne à 3 mois (gold standard), normalisation du SCC, TEP en cas de doute. "
            "7) Surveillance : examen gynécologique trimestriel 2 ans, IRM annuelle, prise en charge des effets tardifs (sténose vaginale, cystite radique)."
        ),
        "protocole": "Radiochimiothérapie : RT pelvienne 45-50 Gy + Cisplatine 40 mg/m² hebdomadaire × 5, puis curiethérapie HDR.",
        "effets_secondaires": ["cystite radique", "sténose vaginale", "néphrotoxicité (Cisplatine)", "diarrhée"],
        "mots_cles": ["col utérin", "parcours de soins", "FIGO", "radiochimiothérapie", "curiethérapie", "HPV", "Cisplatine"],
        "scenario_patient": "Femme de 45 ans, métrorragies : biopsie, IRM pelvienne, RCP, radiochimiothérapie + curiethérapie puis surveillance gynécologique.",
        "reference": "Guide AMFROM 2024, Chapitre II – Cancer du col utérin, p.66",
        "metastase": "La maladie métastatique relève d'une chimiothérapie systémique ± immunothérapie (page 67).",
    },
]


def main():
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))

    new_ids = {p["id"] for p in PARCOURS}
    # Retirer d'anciennes entrées PARC-* pour rester idempotent
    data = [d for d in data if d.get("id") not in new_ids]

    for p in PARCOURS:
        entry = {
            "id": p["id"],
            "categorie": "parcours_de_soins",
            "type_cancer": p["type_cancer"],
            "sous_type": p["sous_type"],
            "stade": "tous stades",
            "titre": p["titre"],
            "contenu": p["contenu"],
            "protocole": p["protocole"],
            "effets_secondaires": p["effets_secondaires"],
            "mots_cles": p["mots_cles"],
            "scenario_patient": p["scenario_patient"],
            "reference": p["reference"],
            "est_synthetique": False,
            "date_creation": DATE,
            "metastase": p["metastase"],
        }
        data.append(entry)

    JSON_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    total = len(data)
    parc = sum(1 for d in data if d.get("categorie") == "parcours_de_soins")
    print(f"Entrées parcours_de_soins ajoutées : {len(PARCOURS)}")
    print(f"Total parcours_de_soins dans la base : {parc}")
    print(f"Total entrées dans la base : {total}")


if __name__ == "__main__":
    main()
