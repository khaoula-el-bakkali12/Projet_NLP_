import json

with open('data/raw/dataset_oncologie_FINAL_v6.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'Total entries: {len(data)}')
synthetic_ids = [e['id'] for e in data if 'SYN' in e['id']]
print(f'Total synthetic entries: {len(synthetic_ids)}')
print(f'Synthetic entries: {synthetic_ids}')

# Find source entries for ONC-SYN-026, 027, 028
for syn_id in ['ONC-SYN-026', 'ONC-SYN-027', 'ONC-SYN-028']:
    entry = next((e for e in data if e['id'] == syn_id), None)
    if entry:
        print(f"\n{syn_id}:")
        print(f"  Type: {entry['type_cancer']}")
        print(f"  Reference: {entry['reference']}")
        print(f"  Title: {entry['titre']}")
