import json
from datetime import datetime

# Read the dataset
with open('data/raw/dataset_oncologie_FINAL_v6.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# New synthetic entries to replace ONC-SYN-026, 027, 028
new_entries = [
    # ONC-SYN-026: Cancer du sein triple négatif chez femme jeune avec métastases
    {
        "id": "ONC-SYN-026",
        "categorie": "traitement",
        "type_cancer": "sein",
        "sous_type": "Triple négatif",
        "stade": "Stade IV (métastases hépatiques)",
        "titre": "Carcinome canalaire triple négatif métastatique - Schéma FOLEC pallia tif",
        "contenu": "Le carcinome canalaire triple négatif (absence de récepteurs hormonaux et HER2) représente 10-15% des cancers du sein avec un pronostic particulièrement agressif en présentation métastatique. En l'absence de ciblage hormonal ou anti-HER2, la chimiothérapie conventionnelle reste le pilier du traitement palliatif. Le schéma FOLEC (5-Fluoro-Uracile, Épirubicine, Cyclophosphamide) hebdomadaire est utilisé chez les patients avec bon statut de performance et fonction hépatique préservée. L'objectif premier est l'obtention d'une réponse objective (diminution de 30% minimum des foyers tumoraux) et l'amélioration de la qualité de vie.",
        "protocole": {
            "nom": "FOLEC Hebdomadaire",
            "sequence": [
                {
                    "phase": "Chimiothérapie palliative",
                    "medicaments": [
                        {
                            "nom": "5-Fluoro-Uracile",
                            "dose": "500 mg/m²",
                            "voie": "IV",
                            "jour": "J1, J8, J15"
                        },
                        {
                            "nom": "Épirubicine",
                            "dose": "40 mg/m²",
                            "voie": "IV",
                            "jour": "J1, J8, J15"
                        },
                        {
                            "nom": "Cyclophosphamide",
                            "dose": "300 mg/m²",
                            "voie": "IV",
                            "jour": "J1, J8, J15"
                        }
                    ],
                    "frequence": "Toutes les 3 semaines",
                    "cycles": "Jusqu'à 6 cycles ou progression"
                }
            ],
            "duree_totale": "18 semaines minimum ou jusqu'à progression",
            "remarques": "Surveillance mensuelle de la fonction hépatique et rénale. Évaluation de réponse par imagerie tous les 2-3 cycles. Support symptomatique prioritaire."
        },
        "effets_secondaires": [
            "neutropénie fébrile (risque augmenté)",
            "mucite sévère",
            "syndrome main-pied",
            "cardiotoxicité (surveillance FEVG)",
            "anémie et thrombocytopénie",
            "neuropathie périphérique grade 2-3"
        ],
        "mots_cles": [
            "sein",
            "triple négatif",
            "métastatique",
            "hépatique",
            "FOLEC",
            "palliatif",
            "femme jeune",
            "pronostic grave"
        ],
        "scenario_patient": "Patiente de 35 ans, mère de deux jeunes enfants, diagnostiquée 18 mois plus tôt d'un carcinome canalaire infiltrant du sein gauche grade III, triple négatif (RH-, HER2-), stade IIB. Après traitement adjuvant par EC-Docetaxel, elle a présenté une rechute avec métastases hépatiques multiples et ascite. ECOG 1. Fonction hépatique légèrement dégradée (bilirubin 1,8 mg/dL). Elle reçoit le schéma FOLEC hebdomadaire. Après 3 cycles, imagerie montre stabilité des foyers hépatiques et régression de l'ascite. Tolérance marquée par une mucite grade 2 contrôlée et neutropénie grade 1.",
        "reference": "Guide AMFROM 2024, p.45-48",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat()
    },
    # ONC-SYN-027: Cancer colorectal métastatique avec mutation BRAF V600E
    {
        "id": "ONC-SYN-027",
        "categorie": "traitement",
        "type_cancer": "colorectal",
        "sous_type": "BRAF V600E muté",
        "stade": "Stade IV (métastases pulmonaires + péritonéales)",
        "titre": "Adénocarcinome colique BRAF-muté métastatique - Triple combinaison Encorafénib + Cétuximab + Irinotecan",
        "contenu": "La mutation BRAF V600E, identifiée dans 5-10% des cancers colorectaux métastatiques, confère un profil très agressif et une résistance aux inhibiteurs simples de la MAPK. L'inhibition complète de la voie nécessite une stratégie combinée associant un inhibiteur BRAF (Encorafénib), un anticorps anti-EGFR (Cétuximab) et une chimiothérapie de base (Irinotecan). Cette triple combinaison améliore la survie globale médiane à 14 mois vs 5-6 mois en chimiothérapie conventionnelle seule. Le traitement est toléré si les fonctions hépatique et rénale sont préservées.",
        "protocole": {
            "nom": "Encorafénib + Cétuximab + Irinotecan",
            "sequence": [
                {
                    "phase": "Traitement continu BRAF-inhibé",
                    "medicaments": [
                        {
                            "nom": "Encorafénib",
                            "dose": "300 mg",
                            "voie": "per os",
                            "jour": "J1-J21"
                        },
                        {
                            "nom": "Cétuximab",
                            "dose": "500 mg/m² (charge), puis 250 mg/m² hebdo",
                            "voie": "IV",
                            "jour": "Hebdomadaire"
                        },
                        {
                            "nom": "Irinotecan",
                            "dose": "180 mg/m²",
                            "voie": "IV",
                            "jour": "J1"
                        }
                    ],
                    "frequence": "Cycles de 3 semaines",
                    "cycles": "Jusqu'à progression"
                }
            ],
            "duree_totale": "Jusqu'à progression clinique ou intolérance",
            "remarques": "Dépistage BRAF V600E obligatoire par NGS avant traitement. Surveillance mensuelle LFT. Gestion proactive de l'éruption cutanée liée au Cétuximab (grade 2-3 fréquent)."
        },
        "effets_secondaires": [
            "éruption cutanée acnéiforme (80-90% des patients)",
            "diarrhée chronique",
            "nausées/vomissements modérés",
            "anémie progressiva",
            "hypomagnesémie (nécessite supplémentation IV)",
            "photosensibilité"
        ],
        "mots_cles": [
            "colorectal",
            "BRAF V600E",
            "métastatique",
            "Encorafénib",
            "Cétuximab",
            "Irinotecan",
            "mutation",
            "voie MAPK"
        ],
        "scenario_patient": "Patient de 62 ans, ex-fumeur, hospitalisé pour occlusion colique. Diagnostic d'adénocarcinome du côlon sigmoid stade IV avec métastases pulmonaires bilatérales et carcinomatose péritonéale. NGS confirme mutation BRAF V600E, MSS. Après résection du côlon sigmoïde, traitement par Encorafénib + Cétuximab + Irinotecan initié. Après 4 cycles, imagerie montre réduction de 45% des métastases pulmonaires. Tolérance acceptable avec éruption cutanée grade 2 sous doxycycline, diarrhée grade 1 contrôlée par lopéramide.",
        "reference": "Guide AMFROM 2024, p.62-65",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat()
    },
    # ONC-SYN-028: Cancer du poumon CBNPC avec mutation EGFR exon 19
    {
        "id": "ONC-SYN-028",
        "categorie": "traitement",
        "type_cancer": "poumon",
        "sous_type": "CBNPC EGFR muté",
        "stade": "Stade IV (métastases osseuses + cérébrales)",
        "titre": "Adénocarcinome pulmonaire EGFR-dépendant avec métastases cérébrales - Traitement par Osimertinib avec irradiation cérébrale SRS",
        "contenu": "Les mutations sensibilisantes d'EGFR (délétion exon 19, point mutation L858R) représentent 40-50% des adénocarcinomes pulmonaires non squameux chez les non-fumeurs asiatiques et 15-20% en populations caucasiennes. Les inhibiteurs de tyrosine kinase EGFR de 3ème génération (Osimertinib) franchissent la barrière hémato-encéphalique et sont privilégiés pour les patients avec métastases cérébrales. L'irradiation stéréotaxique (SRS) des foyers cérébraux en parallèle offre un contrôle local optimal et prolonge la survie sans progression.",
        "protocole": {
            "nom": "Osimertinib 80 mg quotidien + SRS cérébral",
            "sequence": [
                {
                    "phase": "Traitement systemique EGFR-ciblé",
                    "medicaments": [
                        {
                            "nom": "Osimertinib",
                            "dose": "80 mg",
                            "voie": "per os",
                            "jour": "Quotidien"
                        }
                    ],
                    "frequence": "Continu",
                    "cycles": "Jusqu'à progression extracérébrale"
                },
                {
                    "phase": "Irradiation stéréotaxique (SRS)",
                    "medicaments": [],
                    "frequence": "Unique ou fractionnée (3-5 fractions selon taille/nombre des lésions)",
                    "cycles": "1 cycle"
                }
            ],
            "duree_totale": "Osimertinib continu ; SRS en 1 semaine",
            "remarques": "Synchronisation : débuter Osimertinib 1-2 semaines après SRS pour minimiser la toxicité cérébrale. IRM cérébrale de suivi chaque 2-3 mois. Gestion des effets cutanés et GI."
        },
        "effets_secondaires": [
            "éruption cutanée acnéiforme (30-40%)",
            "diarrhée chronique (grade 1-2)",
            "toxicité pulmonaire (IPS: 1-3%)",
            "hépatotoxicité transitoire",
            "toxicité cérébrale post-SRS (œdème, nécrose radiaire rare)",
            "onichodystrophie"
        ],
        "mots_cles": [
            "poumon",
            "CBNPC",
            "EGFR muté",
            "exon 19",
            "métastases cérébrales",
            "Osimertinib",
            "SRS",
            "TKI 3ème génération"
        ],
        "scenario_patient": "Femme de 58 ans, non-fumeuse, présentant une dyspnée progressive et migraines frontales. Scanner thoracique montre masse apicale gauche 3 cm avec adénopathies médiastinales. Biopsie : adénocarcinome bronchioloalvéolaire, mutation EGFR délétion exon 19. IRM cérébrale : 4 nodules métastatiques (1,2 à 2,1 cm). Traitement débute par SRS multi-lésionnelle (18 Gy en 3 fractions), puis Osimertinib 80 mg quotidien 1 semaine après. Après 8 semaines : régression de 40% de la masse pulmonaire, stabilité des foyers cérébrales. Tolérance bonne avec éruption grade 1 et diarrhée mineure.",
        "reference": "Guide AMFROM 2024, p.78-82",
        "est_synthetique": True,
        "date_creation": datetime.now().isoformat()
    }
]

# Find and replace the old entries
for new_entry in new_entries:
    entry_id = new_entry["id"]
    idx = next((i for i, e in enumerate(data) if e["id"] == entry_id), None)
    if idx is not None:
        data[idx] = new_entry
        print(f"✓ Replaced {entry_id}")

# Save back
with open('data/raw/dataset_oncologie_FINAL_v6.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n✓ Dataset saved with {len(data)} total entries")
