import json
import csv
import sys
from pathlib import Path

def sync_json_to_csv(json_path, csv_path):
    print(f"Synchronizing {json_path} to {csv_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    headers = [
        'id', 'categorie', 'type_cancer', 'sous_type', 'stade', 'titre', 
        'contenu', 'protocole', 'effets_secondaires', 'mots_cles', 
        'scenario_patient', 'reference', 'est_synthetique', 'date_creation'
    ]
    
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(headers)
        
        for item in json_data:
            row = []
            for h in headers:
                val = item.get(h)
                if val is None:
                    row.append('')
                elif h == 'protocole':
                    if isinstance(val, (dict, list)):
                        row.append(json.dumps(val, ensure_ascii=False))
                    else:
                        row.append(str(val))
                elif h == 'effets_secondaires' or h == 'mots_cles':
                    if isinstance(val, list):
                        row.append('; '.join(val))
                    else:
                        row.append(str(val))
                elif h == 'est_synthetique':
                    if isinstance(val, bool):
                        row.append('True' if val else 'False')
                    else:
                        row.append(str(val))
                else:
                    row.append(str(val))
            writer.writerow(row)
    print("Synchronization completed successfully!")

if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent
    json_p = base_dir / "data" / "raw" / "dataset_oncologie_FINAL_v6.json"
    csv_p = base_dir / "data" / "raw" / "dataset_oncologie_FINAL_v6.csv"
    sync_json_to_csv(json_p, csv_p)
