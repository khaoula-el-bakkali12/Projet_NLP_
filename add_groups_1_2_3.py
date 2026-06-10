import json
from datetime import datetime

# Read the current dataset
with open('data/raw/dataset_oncologie_FINAL_v6.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Get the current max ID number
max_id = max(int(e['id'].split('-')[-1]) for e in data if e['id'].startswith('ONC-SYN-'))

# New 15 complex case entries (Groups 1, 2, 3)
new_15_entries = []

# Group 1: Cancer + Diabète (5)
entries_diabetes = [
    {
        "id": f"ONC-SYN-{max_id + 1}",
        "categorie": "diagnostic",
        "type_cancer": "pancréas",
        "sous_type": "adénocarcinome",
        "stade": "Stade II",
        "titre": "Adénocarcinome pancréatique chez patient diabétique type II",
        "contenu": "Le cancer du pancréas diagnostiqué chez patients diabétiques présente des défis thérapeutiques majeurs. L'hyperglycémie doit être étroitement contrôlée avant chimiothérapie (risque d'infection, réduction tolérance). Les platines peuvent déséquilibrer davantage le diabète.",
        "protocole": None,
        "effets_secondaires": ["hyperglycémie sévère", "acidocétose", "hypoglycémies"],
        "mots_cles": ["pancréas", "diabète", "type II"],
        "scenario_patient": "Patient de 64 ans, diabétique depuis 10 ans (HbA1c 7.8%), jaunisse progressive, adénocarcinome pancréas stade II. Avant chimiothérapie FOLFIRINOX, optimisation glycémique avec suivi hebd.",
        "reference": "Guide AMFROM 2024, p.112-115",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Risque métastases hépatiques augmenté."
    },
    {
        "id": f"ONC-SYN-{max_id + 2}",
        "categorie": "traitement",
        "type_cancer": "côlon",
        "sous_type": "adénocarcinome",
        "stade": "Stade III",
        "titre": "Cancer colique stade III avec diabète insulino-dépendant - FOLFOX adapté",
        "contenu": "Les patients diabétiques insulino-dépendants nécessitent collaboration oncologue-endocrinologue. L'équilibre glycémique affecte la tolérance chimiothérapique. Perfusion 5-FU peut nécessiter volumes accrus pour hydratation et clairance.",
        "protocole": {"nom": "mFOLFOX6 adapté", "sequence": [{"phase": "Adjuvant", "medicaments": [{"nom": "5-FU", "dose": "2400 mg/m²", "voie": "IV"}], "frequence": "2 semaines", "cycles": "12"}], "duree_totale": "6 mois", "remarques": "Surveillance glycémique étroite."},
        "effets_secondaires": ["hyperglycémie", "neuropathie"],
        "mots_cles": ["côlon", "diabète", "FOLFOX"],
        "scenario_patient": "Homme 58 ans, diabétique type I (HbA1c 8.2%), adénocarcinome colique stade III. mFOLFOX6 adapté avec pompe insulin programmée.",
        "reference": "Guide AMFROM 2024, p.56-59",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Métastases ganglionnaires."
    },
    {
        "id": f"ONC-SYN-{max_id + 3}",
        "categorie": "diagnostic",
        "type_cancer": "prostate",
        "sous_type": "adénocarcinome",
        "stade": "Stade IV",
        "titre": "Cancer prostate métastatique osseux avec diabète mal équilibré",
        "contenu": "Hyperglycémie chronique affecte réponse immune et favorise métastases. Traitement hormonal peut déséquilibrer davantage la glycémie via insulino-résistance accrue.",
        "protocole": None,
        "effets_secondaires": ["hyperglycémie réfractaire", "fatigue"],
        "mots_cles": ["prostate", "métastatique", "diabète"],
        "scenario_patient": "Patient 72 ans, diabétique type II non-observant (HbA1c 9.4%), PSA 145 ng/mL, cancer prostate T4 N1 M1b avec métastases osseuses. Suppression androgénique initiale.",
        "reference": "Guide AMFROM 2024, p.95-98",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Métastases osseuses multiples."
    },
    {
        "id": f"ONC-SYN-{max_id + 4}",
        "categorie": "traitement",
        "type_cancer": "estomac",
        "sous_type": "adénocarcinome",
        "stade": "Stade II-III",
        "titre": "Chimiothérapie périopératoire cancer gastrique avec diabète fragile",
        "contenu": "Diabète complique malnutrition et complications post-chirurgicales. Reconstitution nutritionnelle préopératoire via NPT souvent requise. Adaptation doses ECF nécessaire.",
        "protocole": {"nom": "ECF modifié", "sequence": [{"phase": "Néoadjuvant", "medicaments": [{"nom": "Épirubicine", "dose": "50 mg/m²", "voie": "IV"}], "frequence": "3 semaines", "cycles": "3"}], "duree_totale": "9 semaines", "remarques": "NPT support."},
        "effets_secondaires": ["nausées sévères", "mucite"],
        "mots_cles": ["estomac", "diabète", "ECF"],
        "scenario_patient": "Homme 67 ans, diabétique (15 ans), perte 8 kg/3 mois, adénocarcinome gastrique stade T3 N2. IMC 19. NPT 2 semaines avant ECF modifié.",
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
        "titre": "Hépatocarcinome cirrhose virale avec diabète type II",
        "contenu": "Diabète complique progression cirrhose vers hépatocarcinome. Tolérance réduite aux traitements locoégionaux (TACE). Hyperglycémie périprocédurale augmente risques nécrose et encéphalopathie.",
        "protocole": None,
        "effets_secondaires": ["encéphalopathie hépatique", "hyperglycémie réfractaire"],
        "mots_cles": ["foie", "hépatocarcinome", "diabète"],
        "scenario_patient": "Patient 61 ans, VHC+, diabétique, HCC stade BCLC B (4 nodules <5cm). HbA1c 9.1%, préparation glycémique 4 semaines avant TACE.",
        "reference": "Guide AMFROM 2024, p.128-132",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Tumeur multifocale intra-hépatique."
    }
]

# Group 2: Cancer + Insuffisance Rénale (5)
entries_renal = [
    {
        "id": f"ONC-SYN-{max_id + 6}",
        "categorie": "traitement",
        "type_cancer": "sein",
        "sous_type": "luminal B",
        "stade": "Stade III",
        "titre": "Cancer sein triple positif (RH+/HER2+) avec IR stade 3b",
        "contenu": "IR chronique stade 3b (DFG 30-44) impose adaptation majeure. Trastuzumab excrété rénal, surveillance rénale accrue. TKI 2ème génération contre-indiqués en IR 3b.",
        "protocole": {"nom": "EC100+Docetaxel doses réduites 20%", "sequence": [{"phase": "Néoadjuvant", "medicaments": [{"nom": "Épirubicine", "dose": "75 mg/m²", "voie": "IV"}], "frequence": "3 semaines", "cycles": "3-4"}], "duree_totale": "6 mois", "remarques": "Créat/DFG chaque cycle."},
        "effets_secondaires": ["hypercreatinémie progressive", "cardiotoxicité"],
        "mots_cles": ["sein", "IR", "HER2+"],
        "scenario_patient": "Patiente 54 ans, IR stade 3b (DFG 38, créat 1.9), carcinome canalaire sein gauche HER2+/RH+, stade IIIb. EC-Docetaxel-Trastuzumab adapté.",
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
        "titre": "Carcinome rénal métastatique avec IR controlatérale",
        "contenu": "Paradoxe thérapeutique: cancer rénal avec IR du rein controlatéral. Néphrectomie risque d'aggraver IR vers dialyse. TKI dosés prudemment. Fonction rénale baseline compromise.",
        "protocole": None,
        "effets_secondaires": ["progression IR vers dialyse", "protéinurie massive"],
        "mots_cles": ["rein", "carcinome", "IR", "métastatique"],
        "scenario_patient": "Homme 68 ans, néphropathie diabétique (rein gauche cicatriciel), cancer rein droit stade IV (métastases pulm). DFG 32. Néphrectomie reportée.",
        "reference": "Guide AMFROM 2024, p.134-137",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Métastases pulmonaires bilatérales."
    },
    {
        "id": f"ONC-SYN-{max_id + 8}",
        "categorie": "traitement",
        "type_cancer": "lymphome",
        "sous_type": "DLBCL",
        "stade": "Stade IV",
        "titre": "DLBCL métastatique avec IR stade 4 - mCHOP modifié",
        "contenu": "IR avancée (DFG 15-29) requiert réduction majeure doses. Rituximab conservé (peu élimination rénale). 5-FU fortement réduit ou éliminé.",
        "protocole": {"nom": "mCHOP modifié (sans 5-FU) doses réduites 30%", "sequence": [{"phase": "Chimiothérapie", "medicaments": [{"nom": "Cyclophosphamide", "dose": "525 mg/m²", "voie": "IV"}], "frequence": "3 semaines", "cycles": "6-8"}], "duree_totale": "6-8 mois", "remarques": "Créat/DFG chaque cycle."},
        "effets_secondaires": ["aggravation IR stade 5", "infections opportunistes"],
        "mots_cles": ["lymphome", "DLBCL", "IR"],
        "scenario_patient": "Femme 72 ans, IR stade 4 (DFG 22), adénopathies médiastinales. PET-CT DLBCL stade IV. mCHOP modifié avec suivi néphro.",
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
        "titre": "Cancer vessie infiltrant avec IR obstructive bilatérale",
        "contenu": "Cancer vessie infiltrant peut causer IR obstructive bilatérale (compression urétérale). Cisplatine contre-indiqué en IR significative (DFG <60). Néphrostomie percutanée urgente avant traitement oncologique.",
        "protocole": None,
        "effets_secondaires": ["aggravation IR", "sepsis urinaire"],
        "mots_cles": ["vessie", "carcinome", "IR obstructive"],
        "scenario_patient": "Homme 65 ans, hématurie macroscopique, carcinome urothélial stade III avec IR obstructive (créat 2.8, DFG 22). Double néphrostomie percutanée urgente.",
        "reference": "Guide AMFROM 2024, p.149-152",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Envahissement musculaire perivésical."
    },
    {
        "id": f"ONC-SYN-{max_id + 10}",
        "categorie": "traitement",
        "type_cancer": "ovaire",
        "sous_type": "sérosopapillaire",
        "stade": "Stade IV",
        "titre": "Cancer ovarien métastatique avec IR - Paclitaxel-Carboplatine AUC 5",
        "contenu": "IR complexifie traitement cancer ovarien. Carboplatine (moins néphrotoxique que Cisplatine) utilisé avec ajustement AUC. Paclitaxel pas d'adaptation majeure. IR baseline doit être comptabilisée.",
        "protocole": {"nom": "Paclitaxel-Carboplatine AUC 5", "sequence": [{"phase": "Chimiothérapie", "medicaments": [{"nom": "Paclitaxel", "dose": "175 mg/m²", "voie": "IV"}], "frequence": "3 semaines", "cycles": "6-8"}], "duree_totale": "6-8 mois", "remarques": "AUC selon Calvert."},
        "effets_secondaires": ["néphrotoxicité progressive", "anémie"],
        "mots_cles": ["ovaire", "métastatique", "IR", "Carboplatine"],
        "scenario_patient": "Femme 58 ans, hypertension, cancer ovarien stade IV (métastases hépat, ascite). Créat 1.9 (DFG 35). Paclitaxel-Carboplatine AUC 5, monitoring néphro.",
        "reference": "Guide AMFROM 2024, p.175-178",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Métastases hépatiques et péritonéales."
    }
]

# Group 3: Cancer + HTA (5)
entries_hta = [
    {
        "id": f"ONC-SYN-{max_id + 11}",
        "categorie": "diagnostic",
        "type_cancer": "sein",
        "sous_type": "HER2 positif",
        "stade": "Stade III",
        "titre": "Cancer sein HER2+ avec HTA sévère non-contrôlée",
        "contenu": "HTA non-contrôlée est facteur risque majeur cardiotoxicité lors Trastuzumab+anthracyclines. Inhibiteurs aromatase peuvent augmenter PA. Contrôle tensionnel strict pré-thérapeutique impératif.",
        "protocole": None,
        "effets_secondaires": ["hypertension réfractaire", "cardiotoxicité augmentée"],
        "mots_cles": ["sein", "HER2", "HTA"],
        "scenario_patient": "Femme 52 ans, HTA mal contrôlée (PA 165/105), carcinome canalaire sein stade III HER2+. Optimisation tensionnelle 3 semaines avant traitement.",
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
        "titre": "Cancer rénal avec HTA tumorale-induite - Sunitinib adjuvant",
        "contenu": "Cancer rénal sécrète substances hypertensogènes (rénine, EPO). HTA tumorale exacerbée par Sunitinib qui cause HTA supplémentaire. Gestion antihypertensive anticipée et agressive requise.",
        "protocole": {"nom": "Sunitinib 50 mg/j (4sem on/2sem off)", "sequence": [{"phase": "Adjuvant", "medicaments": [{"nom": "Sunitinib", "dose": "50 mg/j", "voie": "per os"}], "frequence": "Cycles 4-2", "cycles": "12 mois"}], "duree_totale": "12 mois", "remarques": "PA hebdo 1er mois."},
        "effets_secondaires": ["hypertension sévère (60%)", "syndrome main-pied"],
        "mots_cles": ["rein", "carcinome", "HTA tumorale", "Sunitinib"],
        "scenario_patient": "Homme 61 ans, HTA depuis 5 ans, néphrectomie gauche carcinome stade II. Après résection, HTA disparaît. Sunitinib avec tension mieux contrôlée.",
        "reference": "Guide AMFROM 2024, p.139-143",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Pas métastases, adjuvant."
    },
    {
        "id": f"ONC-SYN-{max_id + 13}",
        "categorie": "diagnostic",
        "type_cancer": "poumon",
        "sous_type": "CBNPC",
        "stade": "Stade III",
        "titre": "CBNPC avec HTAP secondaire",
        "contenu": "HTAP secondaire CBNPC peut résulter thromboses ou invasion vasculaire. Contre-indique formellement chimiothérapie et certains TKI (aggravent HTAP). Approche devient palliative.",
        "protocole": None,
        "effets_secondaires": ["décompensation cardiaque droite", "hypoxémie"],
        "mots_cles": ["poumon", "CBNPC", "HTAP"],
        "scenario_patient": "Homme 68 ans, HTA ancienne. CBNPC stade IIIB. Échocardiographie: HTAP modérée (PAPs 55). Diagnostic difficile: tumorale vs thromboembolique.",
        "reference": "Guide AMFROM 2024, p.81-85",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Stade IIIB (N3)."
    },
    {
        "id": f"ONC-SYN-{max_id + 14}",
        "categorie": "traitement",
        "type_cancer": "côlon",
        "sous_type": "adénocarcinome",
        "stade": "Stade IV",
        "titre": "Cancer colique métastatique avec HTA réfractaire - Bevacizumab FOLFOX",
        "contenu": "Bevacizumab anti-VEGF dans cancer colique métastatique pose problème majeur. Anti-angiogenèse aggrave HTA dans 80% des cas. HTA réfractaire menaçante peut survenir.",
        "protocole": {"nom": "FOLFOX+Bevacizumab", "sequence": [{"phase": "Chimiothérapie", "medicaments": [{"nom": "5-FU", "dose": "2400 mg/m²", "voie": "IV"}], "frequence": "2 semaines", "cycles": "progression"}], "duree_totale": "12-24 mois", "remarques": "PA tous les 2 weeks."},
        "effets_secondaires": ["HTA réfractaire (80%)", "protéinurie"],
        "mots_cles": ["côlon", "métastatique", "Bevacizumab", "HTA"],
        "scenario_patient": "Homme 64 ans, HTA mal contrôlée (PA 145/92), cancer colique stade IV (métastases hépatiques). Après 1 mois FOLFOX-Bevacizumab, PA monte 165/110 résistante.",
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
        "titre": "Maladie Hodgkin métastatique avec HTAP secondaire",
        "contenu": "HTAP maladie Hodgkin peut résulter fibrose pulmonaire paraneoplasique ou atteinte vasculaire tumorale. Anthracyclines (ABVD) causent cardiotoxicité augmentée avec HTAP.",
        "protocole": None,
        "effets_secondaires": ["décompensation cardiaque", "hypoxémie progressive"],
        "mots_cles": ["Hodgkin", "métastatique", "HTAP"],
        "scenario_patient": "Jeune adulte 28 ans, maladie Hodgkin stade IV, dyspnée progressive. Échocardiographie: HTAP modérée. Avant ABVD, débat risque-bénéfice.",
        "reference": "Guide AMFROM 2024, p.192-195",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": "Métastases pulmonaires et hépato-spléniques."
    }
]

new_15_entries.extend(entries_diabetes)
new_15_entries.extend(entries_renal)
new_15_entries.extend(entries_hta)

# Save the updated dataset
all_entries = data + new_15_entries
with open('data/raw/dataset_oncologie_FINAL_v6.json', 'w', encoding='utf-8') as f:
    json.dump(all_entries, f, ensure_ascii=False, indent=2)

print(f"✓ Added {len(new_15_entries)} new entries (Groups 1, 2, 3)")
print(f"✓ Total dataset now: {len(all_entries)} entries")
print(f"✓ Last ID added: ONC-SYN-{max_id + 15}")
