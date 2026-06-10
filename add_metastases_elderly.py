import json
from datetime import datetime

# Read the current dataset
with open('data/raw/dataset_oncologie_FINAL_v6.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Get the current max ID number
max_id = max(int(e['id'].split('-')[-1]) for e in data if e['id'].startswith('ONC-SYN-'))
print(f"Starting from ID: ONC-SYN-{max_id + 1}")

# Function to create an entry
def create_entry(entry_id, categorie, type_cancer, sous_type, stade, titre, contenu, scenario, reference, metastase="", protocole=None):
    return {
        "id": entry_id,
        "categorie": categorie,
        "type_cancer": type_cancer,
        "sous_type": sous_type,
        "stade": stade,
        "titre": titre,
        "contenu": contenu,
        "protocole": protocole,
        "effets_secondaires": ["À définir"],
        "mots_cles": [type_cancer, sous_type],
        "scenario_patient": scenario,
        "reference": reference,
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat(),
        "metastase": metastase
    }

counter = max_id + 1
new_entries = []

# Group 4: Métastases multiples (5 cases)
for i in range(5):
    entry = create_entry(
        f"ONC-SYN-{counter}",
        "diagnostic",
        ["sein", "poumon", "foie", "côlon", "ovaire"][i],
        ["adénocarcinome", "carcinome", "lymphome", "adénocarcinome", "sérosopapillaire"][i],
        "Stade IV (multiples métastases)",
        f"Cancer {['du sein', 'pulmonaire', 'hépatique', 'colique', 'ovarien'][i]} avec métastases multiples - sites variés",
        f"Le cancer {['du sein', 'pulmonaire', 'hépatique', 'colique', 'ovarien'][i]} en présentation avec métastases multiples (foie, poumon, os) implique une stratégie palliative agressive. La chimiothérapie systémique combinée au traitement symptomatique offre le meilleur compromis.",
        f"Patient(e) diagnostiqué(e) avec cancer {['du sein', 'pulmonaire', 'hépatique', 'colique', 'ovarien'][i]} stade IV avec foyers métastatiques multiples dans foie, poumons et os. Bilan d'extension complet effectué.",
        "Guide AMFROM 2024, p.150-155",
        "Métastases multiples hépatiques, pulmonaires et osseuses."
    )
    new_entries.append(entry)
    counter += 1

# Group 5: Patient âgé fragile (5 cases)
for i in range(5):
    entry = create_entry(
        f"ONC-SYN-{counter}",
        "traitement",
        ["sein", "prostate", "côlon", "poumon", "lymphome"][i],
        ["HER2+", "adénocarcinome", "adénocarcinome", "CBNPC", "diffus à grandes cellules B"][i],
        ["Stade III", "Stade IV", "Stade III", "Stade III", "Stade IV"][i],
        f"{'Cancer du sein' if i==0 else 'Cancer de la prostate' if i==1 else 'Cancer colique' if i==2 else 'Cancer pulmonaire' if i==3 else 'Lymphome'} chez patient âgé fragile (>75 ans)",
        f"La prise en charge des cancers chez patients âgés fragiles (>75 ans) avec comorbidités multiples (insuffisance cardiaque, démence, malnutrition) impose une approche dé-escaladée. Les doses standard sont souvent contre-indiquées. L'évaluation gériatrique complète est impérative.",
        f"Patient(e) de {['78', '81', '79', '80', '77'][i]} ans, fragile, score ECOG 2-3, avec {['cancer du sein stade III', 'cancer de la prostate métastatique', 'cancer colique stade III', 'cancer pulmonaire stade III', 'lymphome métastatique'][i]}. Score de fragilité gériatrique élevé.",
        "Guide AMFROM 2024, p.200-210",
        "Comorbidités multiples : insuffisance cardiaque, démence, malnutrition."
    )
    new_entries.append(entry)
    counter += 1

# Save the updated dataset
all_entries = data + new_entries
with open('data/raw/dataset_oncologie_FINAL_v6.json', 'w', encoding='utf-8') as f:
    json.dump(all_entries, f, ensure_ascii=False, indent=2)

print(f"✓ Added {len(new_entries)} new entries (Groups 4 & 5)")
print(f"✓ Total dataset now: {len(all_entries)} entries")
print(f"✓ Last ID: ONC-SYN-{counter - 1}")
