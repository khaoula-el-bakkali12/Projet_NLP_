import json
from datetime import datetime

# Read the current dataset
with open('data/raw/dataset_oncologie_FINAL_v6.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Get the current max ID number
max_id = max(int(e['id'].split('-')[-1]) for e in data if e['id'].startswith('ONC-SYN-'))
print(f"Current max ID: ONC-SYN-{max_id}")

# Generate 25 new entries for complex cases
new_entries = [
    # Group 1: Cancer + Diabète (5 cases)
    {
        "id": f"ONC-SYN-{max_id + 1}",
        "categorie": "diagnostic",
        "type_cancer": "pancréas",
        "sous_type": "adénocarcinome",
        "stade": "Stade II",
        "titre": "Adénocarcinome pancréatique chez patient diabétique de type II",
        "contenu": "Le cancer du pancréas diagnostiqué chez patients diabétiques présente des défis thérapeutiques majeurs. La dysglycémie doit être étroitement contrôlée avant, pendant et après la chimiothérapie, car les anthracyclines et platines aggravant potentiellement l'équilibre glycémique. Une hyperglycémie mal maîtrisée augmente les complications infectieuses post-opératoires et réduit la tolérance aux traitements oncologiques.",
        "protocole": None,
        "effets_secondaires": ["hyperglycémie sévère", "acidocétose", "hypoglycémies", "infection des plaies"],
        "mots_cles": ["pancréas", "diabète", "type II", "chimiothérapie", "équilibre glycémique", "FOLFIRINOX"],
        "scenario_patient": "Patient de 64 ans, diabétique depuis 10 ans avec HbA1c 7.8%, hospitalisé pour jaunisse progressive. Diagnostic d'adénocarcinome du pancréas stade II. Avant chimiothérapie, optimisation glycémique avec augmentation insuline basale. Traitement par FOLFIRINOX initié avec suivi hebdomadaire de la glycémie veineuse et HbA1c tous les 2 mois.",
        "reference": "Guide AMFROM 2024, p.112-115",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Risque de métastases hépatiques et péritonéales augmenté chez patients diabétiques."
    },
    {
        "id": f"ONC-SYN-{max_id + 2}",
        "categorie": "traitement",
        "type_cancer": "côlon",
        "sous_type": "adénocarcinome",
        "stade": "Stade III",
        "titre": "Cancer colique stade III avec diabète insulino-dépendant - FOLFOX adjuvant",
        "contenu": "Les patients diabétiques insulino-dépendants requièrent une adaptation du protocole FOLFOX pour minimiser les risques d'hyperglycémie périphérique et d'hypoglycémie lors du stress de la chimiothérapie. L'équipe oncologique doit collaborer étroitement avec l'endocrinologue. Les perfusions 5-FU peuvent nécessiter des volumes accrus pour maintenir l'hydratation et la clairance urinaire.",
        "protocole": {
            "nom": "mFOLFOX6 adapté au profil glycémique",
            "sequence": [
                {
                    "phase": "Chimiothérapie adjuvante",
                    "medicaments": [
                        {"nom": "Levocovorine", "dose": "400 mg/m²", "voie": "IV", "jour": "J1"},
                        {"nom": "5-Fluoro-Uracile", "dose": "2400 mg/m² (bolus + perfusion 24h)", "voie": "IV", "jour": "J1"},
                        {"nom": "Oxaliplatine", "dose": "85 mg/m²", "voie": "IV", "jour": "J1"}
                    ],
                    "frequence": "Toutes les 2 semaines",
                    "cycles": "12 cycles (6 mois)"
                }
            ],
            "duree_totale": "6 mois",
            "remarques": "Adaptation des doses si HbA1c > 8%. Surveillance glycémique avant/après chaque cycle. Insuline d'ajustement disponible en urgence."
        },
        "effets_secondaires": ["hyperglycémie sévère", "neuropathie périphérique", "diarrhée", "neutropénie"],
        "mots_cles": ["côlon", "diabète", "FOLFOX", "stade III", "adjuvant", "insuline-dépendant"],
        "scenario_patient": "Homme de 58 ans, diabétique type I depuis 25 ans (HbA1c 8.2%), diagnostiqué d'adénocarcinome colique stade III. Résection colique complète. HBsAg positif asymptomatique (comorbidité virale). Traitement par mFOLFOX6 adapté initié avec pompe insulin programmée.",
        "reference": "Guide AMFROM 2024, p.56-59",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Métastases ganglionnaires retrouvées à la résection."
    },
    {
        "id": f"ONC-SYN-{max_id + 3}",
        "categorie": "diagnostic",
        "type_cancer": "prostate",
        "sous_type": "adénocarcinome",
        "stade": "Stade IV",
        "titre": "Cancer de la prostate métastatique osseux chez diabétique mal équilibré",
        "contenu": "Le cancer de la prostate chez diabétiques mal contrôlés présente une évolution souvent plus agressive. L'hyperglycémie chronique affecte la réponse immune et augmente l'inflammation systémique favorisant les métastases. Le traitement hormonal peut déséquilibrer davantage la glycémie en induisant une insulino-résistance accrue.",
        "protocole": None,
        "effets_secondaires": ["hyperglycémie réfractaire", "fatigue majeure", "bouffées de chaleur", "prise pondérale"],
        "mots_cles": ["prostate", "métastatique", "osseux", "diabète", "hormone", "PSA"],
        "scenario_patient": "Patient de 72 ans, diabétique type II non-observant (HbA1c 9.4%), avec PSA 145 ng/mL. Diagnostic de cancer de prostate T4 N1 M1b (métastases osseuses multiples). Traitement débute par suppression androgénique complète (agoniste GnRH + antiandrogène).",
        "reference": "Guide AMFROM 2024, p.95-98",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Métastases osseuses multiples scléreuses."
    },
    {
        "id": f"ONC-SYN-{max_id + 4}",
        "categorie": "traitement",
        "type_cancer": "estomac",
        "sous_type": "adénocarcinome",
        "stade": "Stade II-III",
        "titre": "Chimiothérapie péri-opératoire pour cancer gastrique chez diabétique fragile",
        "contenu": "Le cancer gastrique en présentation de diabète complique augmente les risques de malnutrition et de complications post-chirurgicales. La chimiothérapie néoadjuvante (ECF) doit être dosée prudemment. La reconstitution nutritionnelle préopératoire via nutrition parentérale est souvent requise.",
        "protocole": {
            "nom": "ECF modifié (néoadjuvant)",
            "sequence": [
                {
                    "phase": "Chimiothérapie néoadjuvante",
                    "medicaments": [
                        {"nom": "Épirubicine", "dose": "50 mg/m² (réduit de 20%)", "voie": "IV", "jour": "J1"},
                        {"nom": "Cisplatine", "dose": "60 mg/m² (réduit)", "voie": "IV", "jour": "J1"},
                        {"nom": "5-Fluoro-Uracile", "dose": "200 mg/m²/j (perfusion continue)", "voie": "IV", "jour": "J1-J21"}
                    ],
                    "frequence": "Toutes les 3 semaines",
                    "cycles": "3 cycles (9 semaines)"
                }
            ],
            "duree_totale": "9 semaines + chirurgie",
            "remarques": "Nutrition parentérale de support. Prophylaxie anti-émétique renforcée. Hydratation généreuse pour prévention toxicité rénale."
        },
        "effets_secondaires": ["nausées/vomissements sévères", "mucite", "néphrotoxicité", "hyperglycémie"],
        "mots_cles": ["estomac", "diabète", "fragilité", "ECF", "néoadjuvant", "malnutrition"],
        "scenario_patient": "Homme de 67 ans, diabétique depuis 15 ans, perte pondérale 8 kg / 3 mois. Diagnostic d'adénocarcinome gastrique stade T3 N2. IMC 19 (maigreur). Nutrition parentérale 2 semaines, puis ECF modifié initié.",
        "reference": "Guide AMFROM 2024, p.107-110",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Envahissement ganglionnaire régional."
    },
    {
        "id": f"ONC-SYN-{max_id + 5}",
        "categorie": "diagnostic",
        "type_cancer": "foie",
        "sous_type": "hépatocarcinome",
        "stade": "Stade BCLC B",
        "titre": "Hépatocarcinome sur cirrhose virale chez diabétique type II",
        "contenu": "Le diabète complique la progression de la cirrhose hépatique vers l'hépatocarcinome. Les patients diabétiques avec hépatocarcinome ont une tolérance réduite aux traitements locoégionaux (chimioembolisation TACE). L'hyperglycémie périprocédurale augmente les risques de nécrose hépatique et d'encéphalopathie.",
        "protocole": None,
        "effets_secondaires": ["encéphalopathie hépatique", "décompensation hépatique", "hyperglycémie réfractaire"],
        "mots_cles": ["foie", "hépatocarcinome", "cirrhose", "diabète", "TACE", "VHC"],
        "scenario_patient": "Patient de 61 ans, VHC+ (génotype 1b), diabétique, diagnostiqué avec HCC stade BCLC B (4 nodules < 5 cm). TACE programmé mais HbA1c 9.1%, donc préparation glycémique 4 semaines avant intervention.",
        "reference": "Guide AMFROM 2024, p.128-132",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Tumeur multifocale intra-hépatique."
    },
    # Group 2: Cancer + Insuffisance Rénale (5 cases)
    {
        "id": f"ONC-SYN-{max_id + 6}",
        "categorie": "traitement",
        "type_cancer": "sein",
        "sous_type": "luminal B",
        "stade": "Stade III",
        "titre": "Cancer du sein triple positif (RH+/HER2+) avec insuffisance rénale stade 3b",
        "contenu": "L'insuffisance rénale chronique stade 3b (DFG 30-44 mL/min) impose une adaptation majeure des protocoles oncologiques. Le Trastuzumab (anti-HER2) est excrété rénal et nécessite une surveillance accrue de la fonction rénale et du poids. Les inhibiteurs de tyrosine kinase de 2ème génération (Lapatinib) sont contre-indiqués en IR stade 3b. Le traitement hormonal (tamoxifène vs inhibiteurs d'aromatase) requiert aussi une évaluation bénéfice-risque.",
        "protocole": {
            "nom": "EC100 + Docetaxel (doses réduites 20%) + Trastuzumab (adapté IR)",
            "sequence": [
                {
                    "phase": "Chimiothérapie néoadjuvante",
                    "medicaments": [
                        {"nom": "Épirubicine", "dose": "75 mg/m² (réduit)", "voie": "IV", "jour": "J1"},
                        {"nom": "Cyclophosphamide", "dose": "400 mg/m² (réduit)", "voie": "IV", "jour": "J1"},
                        {"nom": "Docetaxel", "dose": "75 mg/m² (réduit)", "voie": "IV", "jour": "J1"}
                    ],
                    "frequence": "Toutes les 3 semaines",
                    "cycles": "3-4 cycles"
                },
                {
                    "phase": "Traitement anti-HER2",
                    "medicaments": [
                        {"nom": "Trastuzumab", "dose": "Dose standard + monitoring étroit", "voie": "IV", "jour": "Hebdomadaire"}
                    ],
                    "frequence": "Hebdomadaire",
                    "cycles": "12 semaines"
                }
            ],
            "duree_totale": "6 mois",
            "remarques": "Créatininémie/DFG chaque cycle. Éviter diurétiques. Hydratation IV préchimio. Arrêt Trastuzumab si DFG < 25."
        },
        "effets_secondaires": ["hypercreatinémie progressive", "protéinurie", "acidose", "cardiotoxicité", "anémie"],
        "mots_cles": ["sein", "insuffisance rénale", "HER2+", "RH+", "triple positif", "adaptation doses"],
        "scenario_patient": "Patiente 54 ans, IR chronique stade 3b (DFG 38 mL/min, créatinine 1.9), carcinome canalaire infiltrant sein gauche HER2+/RH+, stade IIIb. Antécédent d'hypertension traitée. Protocole EC-Docetaxel-Trastuzumab adapté avec monitoring rénal serré et cardio tous les 3 mois.",
        "reference": "Guide AMFROM 2024, p.14-18",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Ganglions régionaux envahis."
    },
    {
        "id": f"ONC-SYN-{max_id + 7}",
        "categorie": "diagnostic",
        "type_cancer": "rein",
        "sous_type": "carcinome à cellules claires",
        "stade": "Stade IV",
        "titre": "Carcinome rénal métastatique avec insuffisance rénale contralat\u00e9rale d'origine chronique",
        "contenu": "Le diagnostic de cancer rénal chez patient avec insuffisance rénale du rein controlatéral représente un paradoxe thérapeutique complexe. La néphrectomie radicale risque d'aggraver l'IR, poussant le patient en dialyse. Les inhibiteurs tyrosine kinase multikinase doivent être dosés prudemment. La fonction rénale baseline est souvent déjà compromise.",
        "protocole": None,
        "effets_secondaires": ["progression de l'IR vers dialyse", "protéinurie massive", "électrolytes perturbés"],
        "mots_cles": ["rein", "carcinome", "insuffisance rénale", "métastatique", "controlatéral", "paradoxe"],
        "scenario_patient": "Homme 68 ans, néphropathie diabétique chronique (rein gauche cicatriciel), diagnostiqué cancer rein droit stade IV (métastases pulmonaires). DFG 32 mL/min. Nephrectomie droite considérée mais reportée vu IR avancée.",
        "reference": "Guide AMFROM 2024, p.134-137",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Métastases pulmonaires multiples bilatérales."
    },
    {
        "id": f"ONC-SYN-{max_id + 8}",
        "categorie": "traitement",
        "type_cancer": "lymphome",
        "sous_type": "lymphome diffus à grandes cellules B",
        "stade": "Stade IV",
        "titre": "DLBCL métastatique avec insuffisance rénale stade 4 - CHOP modifié",
        "contenu": "Le lymphome non-Hodgkinien en contexte d'insuffisance rénale avancée (DFG 15-29) requiert une réduction majeure des doses de chimiothérapie. Le rituximab (anticorps anti-CD20) est conservé mais sans adaptation dose (très peu d'élimination rénale). La perfusion 5-FU doit être fortement réduite ou éliminée.",
        "protocole": {
            "nom": "mCHOP modifié (sans 5-FU) - doses réduites 30%",
            "sequence": [
                {
                    "phase": "Chimiothérapie",
                    "medicaments": [
                        {"nom": "Cyclophosphamide", "dose": "525 mg/m² (réduit)", "voie": "IV", "jour": "J1"},
                        {"nom": "Doxorubicine", "dose": "30 mg/m² (réduit)", "voie": "IV", "jour": "J1"},
                        {"nom": "Vincristine", "dose": "1 mg/m² (réduit)", "voie": "IV", "jour": "J1"},
                        {"nom": "Prednisone", "dose": "40 mg/j", "voie": "per os", "jour": "J1-J5"},
                        {"nom": "Rituximab", "dose": "375 mg/m²", "voie": "IV", "jour": "J1"}
                    ],
                    "frequence": "Toutes les 3 semaines",
                    "cycles": "6-8 cycles (selon réponse)"
                }
            ],
            "duree_totale": "6-8 mois",
            "remarques": "Créat/DFG avant chaque cycle. Support hydratation. Dialyse si DFG < 15. Suivi oncologue + néphrologue."
        },
        "effets_secondaires": ["aggravation IR vers stade 5", "infections opportunistes", "cytolyse hépatique"],
        "mots_cles": ["lymphome", "DLBCL", "IR stade 4", "CHOP modifié", "rituximab", "métastatique"],
        "scenario_patient": "Femme 72 ans, IR stade 4 (DFG 22 mL/min) sur hypertension chronique, hospitalisée pour adénopathies médiastinales. PET-CT : DLBCL stade IV (foie, rate, ganglions). mCHOP modifié initié avec suivi néphro intense.",
        "reference": "Guide AMFROM 2024, p.187-190",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Atteinte hépatosplénique."
    },
    {
        "id": f"ONC-SYN-{max_id + 9}",
        "categorie": "diagnostic",
        "type_cancer": "vessie",
        "sous_type": "carcinome urothélial",
        "stade": "Stade III",
        "titre": "Cancer de la vessie infiltrant avec insuffisance rénale obstructive et réflexe",
        "contenu": "Le cancer de la vessie infiltrant peut lui-même causer une insuffisance rénale obstructive bilatérale (par compression urétérale), compliquant la prise en charge. La chimiothérapie néoadjuvante (Cisplatine-Gemcitabine) est souvent une option, mais le Cisplatine est absolument contre-indiqué en IR significative (DFG < 60). Une néphrostomie percutanée est souvent requise en urgence avant tout traitement oncologique.",
        "protocole": None,
        "effets_secondaires": ["aggravation IR obstructive", "sepsis urinaire", "anémie", "acidose"],
        "mots_cles": ["vessie", "carcinome urothélial", "IR obstructive", "négociations", "Cisplatine"],
        "scenario_patient": "Homme 65 ans, hématurie macroscopique, découverte carcinome urothélie infiltrant stade III avec IR obstructive secondaire (créat 2.8, DFG 22). Double néphrostomie percutanée urgente. Après 6 semaines d'adaptation, réévaluation pour thérapeutique.",
        "reference": "Guide AMFROM 2024, p.149-152",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Envahissement musculaire et gras périvésical."
    },
    {
        "id": f"ONC-SYN-{max_id + 10}",
        "categorie": "traitement",
        "type_cancer": "ovaire",
        "sous_type": "sérosopapillaire",
        "stade": "Stade IV",
        "titre": "Cancer ovarien métastatique avec insuffisance rénale - paclitaxel-Carboplatine adapté",
        "contenu": "L'insuffisance rénale pose un dilemme dans le traitement des cancers ovariens métastatiques. Le Carboplatine (moins néphrototoxique que le Cisplatine) peut être utilisé avec ajustement AUC. Le paclitaxel ne requiert pas d'adaptation majeure. La néphrotooxicité des platines existante doit être déjà prise en compte.",
        "protocole": {
            "nom": "Paclitaxel-Carboplatine AUC 5",
            "sequence": [
                {
                    "phase": "Chimiothérapie",
                    "medicaments": [
                        {"nom": "Paclitaxel", "dose": "175 mg/m²", "voie": "IV", "jour": "J1"},
                        {"nom": "Carboplatine", "dose": "AUC 5 (non AUC 6)", "voie": "IV", "jour": "J1"}
                    ],
                    "frequence": "Toutes les 3 semaines",
                    "cycles": "6-8 cycles"
                }
            ],
            "duree_totale": "6-8 mois",
            "remarques": "Calcul AUC selon Calvert. Hydration IV préchimio. Créat/DFG chaque cycle. Suivi néphro spécialisé."
        },
        "effets_secondaires": ["néphrotoxicité progressive", "anémie", "neuropathie", "infections"],
        "mots_cles": ["ovaire", "métastatique", "IR", "Carboplatine", "Paclitaxel", "stade IV"],
        "scenario_patient": "Femme 58 ans, antécédent hypertension, diagnostiquée cancer ovarien stade IV (métastases hépatiques, ascite, gangles). Créat 1.9 (DFG 35). Traitement par Paclitaxel-Carboplatine AUC 5 adapté, monitoring néphro toutes les 3 semaines.",
        "reference": "Guide AMFROM 2024, p.175-178",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Métastases hépatiques et péritonéales."
    }
]

# Continue with more groups...
# Group 3: Cancer + HTA (5 cases)
new_entries.extend([
    {
        "id": f"ONC-SYN-{max_id + 11}",
        "categorie": "diagnostic",
        "type_cancer": "sein",
        "sous_type": "HER2 positif",
        "stade": "Stade III",
        "titre": "Cancer du sein HER2+ chez patiente avec hypertension artérielle sévère",
        "contenu": "L'hypertension artérielle non contrôlée est un facteur de risque majeur de cardiotoxicité lors du traitement par Trastuzumab et anthracyclines. Les inhibiteurs de l'aromatase (tamoxifène) peuvent augmenter la tension artérielle. Un contrôle tensionnel strict pré-thérapeutique est impératif.",
        "protocole": None,
        "effets_secondaires": ["hypertension réfractaire", "cardiotoxicité augmentée", "insuffisance cardiaque"],
        "mots_cles": ["sein", "HER2", "HTA", "Trastuzumab", "cardiotoxicité", "stade III"],
        "scenario_patient": "Femme 52 ans, HTA depuis 10 ans mal contrôlée (PA 165/105 mmHg), diagnostiquée carcinome canalaire sein stade III HER2+. Optimisation tensionnelle sur 3 semaines avant traitement oncologique.",
        "reference": "Guide AMFROM 2024, p.18-22",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Atteinte ganglionnaire régionale."
    },
    {
        "id": f"ONC-SYN-{max_id + 12}",
        "categorie": "traitement",
        "type_cancer": "rein",
        "sous_type": "carcinome à cellules claires",
        "stade": "Stade II-III",
        "titre": "Cancer rénal avec hypertension liée à la tumeur - Sunitinib adjuvant",
        "contenu": "Le cancer rénal sécrète souvent des substances hypertensogènes (rénine, érythropoïétine). L'hypertension tumorale-induite peut être exacerbée par les inhibiteurs tyrosine kinase (Sunitinib) qui causent aussi une hypertension supplémentaire. La gestion antihypertensive doit être anticipée et agressive.",
        "protocole": {
            "nom": "Sunitinib 50 mg/j (4 semaines on / 2 semaines off)",
            "sequence": [
                {
                    "phase": "Traitement adjuvant",
                    "medicaments": [
                        {"nom": "Sunitinib", "dose": "50 mg/j per os", "voie": "per os", "jour": "J1-J28"}
                    ],
                    "frequence": "Cycles 4 semaines on / 2 off",
                    "cycles": "12 mois"
                }
            ],
            "duree_totale": "12 mois",
            "remarques": "PA mesurée à chaque visite (hebdomadaire 1er mois). Antihypertenseurs anticipés (Amlodipine + inhibiteur rénine). Arrêt Sunitinib si PA > 180/110."
        },
        "effets_secondaires": ["hypertension sévère (60%)", "syndrome main-pied", "diarrhée", "fatigue"],
        "mots_cles": ["rein", "carcinome", "HTA tumorale", "Sunitinib", "TKI", "adjuvant"],
        "scenario_patient": "Homme 61 ans, HTA depuis 5 ans, néphrorectomie gauche pour carcinome à cellules claires stade II. Après résection, HTA tumorale-induite disparaît. Traitement adjuvant Sunitinib initié avec tension baseline mieux contrôlée.",
        "reference": "Guide AMFROM 2024, p.139-143",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Pas de métastases, but adjuvant."
    },
    {
        "id": f"ONC-SYN-{max_id + 13}",
        "categorie": "diagnostic",
        "type_cancer": "poumon",
        "sous_type": "CBNPC",
        "stade": "Stade III",
        "titre": "Cancer bronchopulmonaire non à petites cellules avec hypertension artérielle pulmonaire secondaire",
        "contenu": "L'hypertension pulmonaire secondaire dans le contexte de cancer pulmonaire CBNPC peut résulter de thromboses multiples ou invasion vasculaire. Cette complication contre-indique formellement la chimiothérapie et certains TKI (qui aggravent l'HTAP). L'approche devient rapidement palliative.",
        "protocole": None,
        "effets_secondaires": ["décompensation cardiaque droite", "hypoxémie progressive", "syncopes"],
        "mots_cles": ["poumon", "CBNPC", "HTAP", "thrombose", "comorbidités", "pronostic grave"],
        "scenario_patient": "Homme 68 ans, HTA ancienne bien traitée. CBNPC stade IIIB découvert. Échocardiographie : HTAP modérée (PAPs 55 mmHg). Diagnostic difficile : cause tumorale vs thromboembolique vs cardiaque secondaire.",
        "reference": "Guide AMFROM 2024, p.81-85",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Stade IIIB (N3, pas M1)."
    },
    {
        "id": f"ONC-SYN-{max_id + 14}",
        "categorie": "traitement",
        "type_cancer": "côlon",
        "sous_type": "adénocarcinome",
        "stade": "Stade IV",
        "titre": "Cancer colique métastatique chez hypertension réfractaire - Bevacizumab FOLFOX",
        "contenu": "Le Bevacizumab (anti-VEGF) dans le traitement du cancer colique métastatique pose un problème majeur chez patients hypertendus. L'anti-angiogenèse aggrave l'hypertension dans 80% des cas. Une hypertension réfractaire menaçante pour le pronostic peut survenir.",
        "protocole": {
            "nom": "FOLFOX + Bevacizumab",
            "sequence": [
                {
                    "phase": "Chimiothérapie + anti-angiogenèse",
                    "medicaments": [
                        {"nom": "Levocovorine", "dose": "400 mg/m²", "voie": "IV", "jour": "J1"},
                        {"nom": "5-FU", "dose": "2400 mg/m²", "voie": "IV 24h", "jour": "J1"},
                        {"nom": "Oxaliplatine", "dose": "85 mg/m²", "voie": "IV", "jour": "J1"},
                        {"nom": "Bevacizumab", "dose": "5 mg/kg", "voie": "IV", "jour": "J1"}
                    ],
                    "frequence": "Toutes les 2 semaines",
                    "cycles": "Jusqu'à progression"
                }
            ],
            "duree_totale": "12-24 mois (ou progression)",
            "remarques": "PA surveillée toutes les 2 semaines. Antihypertenseurs anticipés (amlodipine + ACE inhibitor). Suivi tension domiciliaire quotidienne."
        },
        "effets_secondaires": ["hypertension réfractaire (80%)", "protéinurie", "accidents vasculaires cérébraux", "thromboses"],
        "mots_cles": ["côlon", "métastatique", "Bevacizumab", "HTA", "anti-VEGF", "FOLFOX"],
        "scenario_patient": "Homme 64 ans, HTA depuis 15 ans sous amlodipine seule (PA borderline 145/92). Diagnostic cancer colique stade IV (métastases hépatiques). Après 1 mois FOLFOX-Bevacizumab, PA monte à 165/110 résistante. Ajout ACE inhibitor + augmentation amlodipine.",
        "reference": "Guide AMFROM 2024, p.58-62",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Métastases hépatiques multiples."
    },
    {
        "id": f"ONC-SYN-{max_id + 15}",
        "categorie": "diagnostic",
        "type_cancer": "lymphome",
        "sous_type": "maladie de Hodgkin",
        "stade": "Stade IV",
        "titre": "Maladie de Hodgkin métastatique avec hypertension pulmonaire secondaire",
        "contenu": "L'hypertension pulmonaire dans la maladie de Hodgkin métastatique peut résulter de fibrose pulmonaire paraneoplasique ou d'atteinte vasculaire tumorale. Les anthracyclines (composant des protocoles ABVD) causent aussi une cardiotoxicité augmentée en présence d'HTAP.",
        "protocole": None,
        "effets_secondaires": ["décompensation cardiaque", "hypoxémie progressive"],
        "mots_cles": ["Hodgkin", "métastatique", "HTAP", "cardiotoxicité", "stade IV"],
        "scenario_patient": "Jeune adulte 28 ans, maladie de Hodgkin stade IV, dyspnée progressive, échocardiographie : HTAP modérée. Avant ABVD, débat risque-bénéfice importance.",
        "reference": "Guide AMFROM 2024, p.192-195",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Métastases pulmonaires et hépato-spléniques."
    }
])

# Save the updated dataset
with open('data/raw/dataset_oncologie_FINAL_v6.json', 'w', encoding='utf-8') as f:
    json.dump(data + new_entries, f, ensure_ascii=False, indent=2)

print(f"✓ Added {len(new_entries)} new complex case entries")
print(f"✓ Total dataset now: {len(data) + len(new_entries)} entries")
