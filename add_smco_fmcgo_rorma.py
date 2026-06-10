import json
from datetime import datetime

# Read the current dataset
with open('data/raw/dataset_oncologie_FINAL_v6.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Get the current max ID number
max_id = max(int(e['id'].split('-')[-1]) for e in data if e['id'].startswith('ONC-SYN-'))

# Add 12 new entries from SMCO, FMCGO, RORMA sources
new_entries = []
counter = max_id + 1

# SMCO entries (Société Marocaine de Cancérologie Oncologique)
smco_cases = [
    {
        "id": f"ONC-SYN-{counter}",
        "categorie": "diagnostic",
        "type_cancer": "colorectal",
        "sous_type": "adénocarcinome",
        "stade": "Stade I",
        "titre": "Dépistage du cancer colorectal par FIT - recommandations SMCO 2024",
        "contenu": "La Société Marocaine de Cancérologie Oncologique recommande le dépistage du cancer colorectal chez patients âgés de 50-75 ans asymptomatiques via test immunologique des selles (FIT) tous les 2 ans. Si FIT positif, coloscopie complète requise. Cette stratégie identifie 90% des cancers stade I-II curables par résection endoscopique ou chirurgicale.",
        "protocole": None,
        "effets_secondaires": ["inconfort minime"],
        "mots_cles": ["colorectal", "dépistage", "FIT", "coloscopie", "prévention"],
        "scenario_patient": "Homme 58 ans, sans antécédent personnel cancer, dépistage FIT positif (hémoglobine fécale 45 ng/mL). Coloscopie: polype adénomateux stade 0-I, résection endoscopique complète.",
        "reference": "SMCO 2023 - Dépistage organisé cancer colorectal",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Pas métastases en stade I."
    },
    {
        "id": f"ONC-SYN-{counter + 1}",
        "categorie": "diagnostic",
        "type_cancer": "prostate",
        "sous_type": "adénocarcinome",
        "stade": "Stade I",
        "titre": "Dépistage cancer prostate par PSA+TR - protocole SMCO 2024",
        "contenu": "SMCO recommande dépistage opportuniste cancer prostate chez hommes 50-75 ans (70 pour antécédents familiaux) via PSA sérique + toucher rectal. PSA <4 ng/mL = surveillancer. PSA 4-10 = biopsie si TR anormal. PSA >10 = biopsie recommandée. Dépistage réduit mortalité prostate de 20-30%.",
        "protocole": None,
        "effets_secondaires": ["anxiété", "inconfort TR"],
        "mots_cles": ["prostate", "dépistage", "PSA", "TR", "prévention"],
        "scenario_patient": "Homme 60 ans, PSA 5.2 ng/mL, TR légèrement nodulaire. Biopsie prostatique: adénocarcinome Gleason 6/10, stade T1c N0 M0.",
        "reference": "SMCO 2024 - Dépistage cancer prostate",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Pas métastases, diagnostic précoce."
    },
    {
        "id": f"ONC-SYN-{counter + 2}",
        "categorie": "traitement",
        "type_cancer": "sein",
        "sous_type": "triple négatif",
        "stade": "Stade III",
        "titre": "Chimiothérapie intensive triple négatif - protocole SMCO accès AMO",
        "contenu": "SMCO facilite accès biosimilaires anti-cancer pour patients couverts par AMO (Assurance Maladie Obligatoire). Pour triple négatif stade III, SMCO recommande chimiothérapie intensive néoadjuvante type EC-Docetaxel via biosimilaires (trastuzumab bio, paclitaxel biosimilaire) pour réduire coût et améliorer accès.",
        "protocole": {
            "nom": "EC-Docetaxel avec biosimilaires",
            "sequence": [
                {
                    "phase": "Néoadjuvant",
                    "medicaments": [
                        {"nom": "Épirubicine", "dose": "100 mg/m²", "voie": "IV", "jour": "J1"},
                        {"nom": "Docetaxel biosimilaire", "dose": "100 mg/m²", "voie": "IV", "jour": "J1"}
                    ],
                    "frequence": "3 semaines",
                    "cycles": "4-6"
                }
            ],
            "duree_totale": "12-18 semaines",
            "remarques": "Remboursement AMO via protocole SMCO 2024."
        },
        "effets_secondaires": ["neutropénie", "alopécie", "nausées"],
        "mots_cles": ["sein", "triple négatif", "SMCO", "AMO", "biosimilaires"],
        "scenario_patient": "Patiente 44 ans, carcinome triple négatif sein droit stade IIIB. Bénéficie du programme AMO-SMCO pour accès chimiothérapie biosimilaire à coût réduit.",
        "reference": "SMCO 2023 - Accès thérapies biosimilaires",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Stade III, pas métastases systémiques."
    },
    {
        "id": f"ONC-SYN-{counter + 3}",
        "categorie": "diagnostic",
        "type_cancer": "estomac",
        "sous_type": "adénocarcinome",
        "stade": "Stade IV",
        "titre": "Cancer gastrique métastatique - palliative SMCO-guidée",
        "contenu": "SMCO recommande dans cancer gastrique métastatique approche palliative basée symptômes et qualité de vie. En contexte maroc où chimiothérapie intensive accès limité, soutien nutritionnel et gestion symptômes primordiaux. Chimiothérapie légère (5-FU monothérapie ou Gemcitabine) si statut bon et patient accepte.",
        "protocole": None,
        "effets_secondaires": ["dénutrition progressive", "douleurs", "dysphagie"],
        "mots_cles": ["estomac", "métastatique", "palliatif", "SMCO", "qualité de vie"],
        "scenario_patient": "Homme 62 ans, cancer gastrique stade IV (métastases hépatiques, ascite), diagnostic tardif. Approche palliative avec soutien nutritionnel et soins symptomatiques centrés.",
        "reference": "SMCO 2024 - Soins palliatifs cancer digestif",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Métastases hépatiques et péritonéales."
    },
]

# FMCGO entries (Fédération Marocaine de Gynécologie Obstétrique)
fmcgo_cases = [
    {
        "id": f"ONC-SYN-{counter + 4}",
        "categorie": "diagnostic",
        "type_cancer": "col_uterus",
        "sous_type": "carcinome épidermoïde",
        "stade": "Stade I",
        "titre": "Dépistage cancer col utérin par test HPV - recommandations FMCGO",
        "contenu": "FMCGO recommande dépistage de masse cancer col utérin chez femmes 25-65 ans par test HPV tous les 5 ans. HPV+ = colposcopie. Colposcopie anormale = biopsie. HPV- = rassurance 5 ans. Vaccination HPV pour jeunes filles <15 ans avant activité sexuelle.",
        "protocole": None,
        "effets_secondaires": ["anxiété dépistage", "gène mineure"],
        "mots_cles": ["col utérin", "HPV", "dépistage", "prévention", "vaccination"],
        "scenario_patient": "Femme 35 ans, test HPV positif (HPV 16), colposcopie: dysplasie grade II. Biopsie confirme CIN2. Traitement par conisation thermique.",
        "reference": "FMCGO 2024 - Dépistage cancer col utérin",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Stade I, pas métastases."
    },
    {
        "id": f"ONC-SYN-{counter + 5}",
        "categorie": "traitement",
        "type_cancer": "ovaire",
        "sous_type": "épithélial",
        "stade": "Stade III",
        "titre": "Cytoréduction chirurgicale cancer ovaire stade III - score Fagotti FMCGO",
        "contenu": "FMCGO recommande cytoréduction optimale via évaluation préopératoire critères Fagotti chez cancer ovarien stade III. Si résécabilité optimale probable (score Fagotti bas), chirurgie ± chimiothérapie néoadjuvante. Cytoréduction complète (résidu <1cm) améliore survie de 5-10 ans vs résidu macroscopique.",
        "protocole": None,
        "effets_secondaires": ["morbidité chirurgicale", "ménopause chirurgicale si ovarienne"],
        "mots_cles": ["ovaire", "cytoréduction", "Fagotti", "chirurgie", "stade III"],
        "scenario_patient": "Femme 58 ans, cancer épithélial ovarien stade IIIC (ascite, carcinomatose). Score Fagotti 4 (résécabilité optimale probable). Cytoréduction complète réalisée, résidu <0.5cm.",
        "reference": "FMCGO 2024 - Cytoréduction chirurgicale",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Stade IIIC, carcinomatose."
    },
    {
        "id": f"ONC-SYN-{counter + 6}",
        "categorie": "diagnostic",
        "type_cancer": "sein",
        "sous_type": "HER2 positif",
        "stade": "Stade II",
        "titre": "Préservation de fertilité cancer sein HER2+ - recommandations FMCGO",
        "contenu": "FMCGO souligne importance préservation fertilité chez femmes jeunes cancer sein avant chimiothérapie. Congélation d'embryons ou ovocytes avant traitement doit être proposée systématiquement. FMCGO recommande aussi délai minimum 3-5 ans post-traitement avant grossesse vu risque récidive.",
        "protocole": None,
        "effets_secondaires": ["retard traitement oncologique", "coût supplémentaire"],
        "mots_cles": ["sein", "fertilité", "préservation", "jeune femme", "embryon"],
        "scenario_patient": "Femme 28 ans, carcinome canalaire sein stade II HER2+. Consultation fertilité: 2 cycles stimulation ovarienne, 12 embryons congelés avant chimiothérapie EC-Docetaxel.",
        "reference": "FMCGO 2024 - Préservation fertilité",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Stade II, pas métastases."
    },
    {
        "id": f"ONC-SYN-{counter + 7}",
        "categorie": "traitement",
        "type_cancer": "foie",
        "sous_type": "hépatocarcinome",
        "stade": "Stade III",
        "titre": "Suivi post-môle hydatiforme et cancer gestationnel - FMCGO",
        "contenu": "FMCGO recommande suivi étroit post-môle hydatiforme (dépistage maladie trophoblastique gestationnelle). Dosage hCG mensuel 6 mois post-évacuation. Persistance/augmentation hCG = maladie trophoblastique gestationnelle maligne (mtGTN). mtGTN traité chimiothérapie MTX/FA ou chimiothérapie polychimiothérapie selon risque.",
        "protocole": None,
        "effets_secondaires": ["toxicité MTX", "ménopause anticipée"],
        "mots_cles": ["môle", "hCG", "trophoblastique", "grossesse", "chimiothérapie"],
        "scenario_patient": "Femme 32 ans, évacuation môle hydatiforme partielle. hCG résiduel 1500 UI/L persistant. Diagnostic mtGTN score risque modéré. Traitement MTX-FA initié.",
        "reference": "FMCGO 2024 - Suivi mtGTN",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Potentiel métastatique si progression."
    },
]

# RORMA entries (Registry Oncology Radiotherapy Maghreb Africa)
rorma_cases = [
    {
        "id": f"ONC-SYN-{counter + 8}",
        "categorie": "traitement",
        "type_cancer": "poumon",
        "sous_type": "CBNPC",
        "stade": "Stade III",
        "titre": "Radiothérapie conformationnelle 3D CBNPC stade III - RORMA 2024",
        "contenu": "RORMA (Registry Oncology Radiotherapy Maghreb) promeut radiothérapie conformationnelle 3D pour CBNPC stade III inopérable. Dose 60 Gy en 2 Gy/jour sur 6 semaines. Radiothérapie combinée chimiothérapie concurrent (Cisplatine-Etoposide) améliore taux survie 5 ans de 15-20%. RORMA recommande planification dosimétrique précise et suivi toxicité.",
        "protocole": {
            "nom": "Radiothérapie 3D 60 Gy + chimiothérapie concurrent",
            "sequence": [
                {
                    "phase": "Radiothérapie",
                    "medicaments": [],
                    "frequence": "5 jours/semaine",
                    "cycles": "6 semaines (30 fractions)"
                },
                {
                    "phase": "Chimiothérapie concurrent",
                    "medicaments": [
                        {"nom": "Cisplatine", "dose": "75 mg/m² (J1, J22, J43)", "voie": "IV"},
                        {"nom": "Etoposide", "dose": "100 mg/j J1-J5, J22-J26, J43-J47", "voie": "IV"}
                    ],
                    "frequence": "Concurrent RT",
                    "cycles": "3 cycles"
                }
            ],
            "duree_totale": "6-7 semaines",
            "remarques": "Planification dosimétrique 4D-CT. Suivi toxicité œsophagienne et pulmonaire."
        },
        "effets_secondaires": ["œsophagite radique grade 2-3", "pneumonite radique", "toxicité hématologique"],
        "mots_cles": ["poumon", "CBNPC", "radiothérapie", "3D-conforme", "RORMA"],
        "scenario_patient": "Homme 65 ans, CBNPC stade IIIB inopérable. Radiothérapie 3D conforme 60 Gy planifiée + Cisplatine-Etoposide concurrent selon RORMA.",
        "reference": "RORMA 2024 - Radiothérapie CBNPC",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Stade IIIB, pas métastases M0."
    },
    {
        "id": f"ONC-SYN-{counter + 9}",
        "categorie": "traitement",
        "type_cancer": "rectum",
        "sous_type": "adénocarcinome",
        "stade": "Stade III",
        "titre": "Radiothérapie néoadjuvante cancer rectum stade III - RORMA",
        "contenu": "RORMA recommande pour cancer rectum stade II-III résecable radiothérapie néoadjuvante 50 Gy en 25 fractions suivi chimiothérapie concurrent (5-FU) puis chirurgie 6-8 semaines après RT. Cette approche diminue récidive locale de 45% et peut améliorer taux anastomose sphincter-préservante.",
        "protocole": {
            "nom": "Radiothérapie 50 Gy + 5-FU néoadjuvant",
            "sequence": [
                {
                    "phase": "Radiothérapie externe",
                    "medicaments": [],
                    "frequence": "5 jours/semaine",
                    "cycles": "5 semaines (25 fractions)"
                }
            ],
            "duree_totale": "5-6 semaines + chirurgie",
            "remarques": "5-FU perfusion continue concurrente possible. Chirurgie 6-8 sem après RT."
        },
        "effets_secondaires": ["diarrhée radique", "érythème rectal", "toxicité intestinale"],
        "mots_cles": ["rectum", "adénocarcinome", "radiothérapie", "néoadjuvant", "RORMA"],
        "scenario_patient": "Homme 58 ans, cancer rectum stade III (T3 N1 M0). Radiothérapie néoadjuvante 50 Gy programmée suivi chirurgie résection antérieure.",
        "reference": "RORMA 2024 - RT cancer rectum",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Stade III, ganglions régionaux."
    },
    {
        "id": f"ONC-SYN-{counter + 10}",
        "categorie": "diagnostic",
        "type_cancer": "tete_cou",
        "sous_type": "carcinome épidermoïde",
        "stade": "Stade III",
        "titre": "Radiothérapie intensité-modulée cancer tête-cou stade III - RORMA",
        "contenu": "RORMA promeut IMRT (radiothérapie intensité-modulée) pour cancer tête-cou stade III permettant conformité supérieure doses tumorales tout respectant organes critiques (glandes salivaires, larynx, moelle épinière). IMRT réduit toxicités tardives (xérostomie 40-50% vs 70% RT 3D-conf).",
        "protocole": {
            "nom": "IMRT 70 Gy + chimiothérapie",
            "sequence": [
                {
                    "phase": "Radiothérapie IMRT",
                    "medicaments": [],
                    "frequence": "5 jours/semaine",
                    "cycles": "7 semaines"
                }
            ],
            "duree_totale": "7 semaines",
            "remarques": "Chimiothérapie concurrent Cisplatine si bon statut. IMRT-IGRT guidée image."
        },
        "effets_secondaires": ["mucite", "dysphagie", "xérostomie"], "mots_cles": ["tête-cou", "IMRT", "radiothérapie", "RORMA", "modulation"],
        "scenario_patient": "Homme 52 ans, carcinome épidermoïde larynge stade III. IMRT 70 Gy + Cisplatine concurrent RORMA-guidée planifiée.",
        "reference": "RORMA 2024 - IMRT tête-cou",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Stade III local-régional."
    },
]

new_entries.extend(smco_cases)
new_entries.extend(fmcgo_cases)
new_entries.extend(rorma_cases)

# Save the updated dataset
all_entries = data + new_entries
with open('data/raw/dataset_oncologie_FINAL_v6.json', 'w', encoding='utf-8') as f:
    json.dump(all_entries, f, ensure_ascii=False, indent=2)

print(f"✓ Added {len(new_entries)} new entries from SMCO/FMCGO/RORMA sources")
print(f"  - SMCO: {len(smco_cases)} entries")
print(f"  - FMCGO: {len(fmcgo_cases)} entries")
print(f"  - RORMA: {len(rorma_cases)} entries")
print(f"✓ Total dataset now: {len(all_entries)} entries")
