# Méthodologie du Dataset d'Oncologie Clinique Marocain

Ce document décrit la structure, les sources de données, le processus de curation et les règles de génération des cas cliniques synthétiques du dataset d'oncologie clinique utilisé pour alimenter notre système de **Génération Augmentée par Récupération (RAG)**.

---

## 📚 1. Sources de Données Référencées

Le dataset consolide des référentiels officiels de pratique clinique, adaptés aux contextes réglementaires, épidémiologiques et d'accès aux soins au Maroc.

### A. AMFROM (Association Marocaine de Formation et de Recherche en Oncologie Médicale)

- **Rôle** : Base de référence principale pour les protocoles thérapeutiques standard (chimiothérapies, immunothérapies, thérapies ciblées) en vigueur au Maroc.
- **Domaines clés** : Protocoles d'induction néoadjuvants, adjuvants, et lignes thérapeutiques pour les cancers du sein (ex: schémas Tolaney, EC100-Docetaxel), cancers colorectaux (FOLFOX, FOLFIRI), et cancers broncho-pulmonaires (CBNPC).

### B. SMCO (Société Marocaine de Cancérologie Oncologique)

- **Rôle** : Consensus nationaux pour l'organisation des soins, le dépistage précoce et l'utilisation thérapeutique de pointe.
- **Domaines clés** : Dépistage organisé du cancer colorectal ( FIT, coloscopie) et du cancer de la prostate (PSA + Toucher rectal), ainsi que l'usage médico-économique des **biosimilaires** pour faciliter l'accès aux thérapies ciblées sous le régime de l'AMO (Assurance Maladie Obligatoire).

### C. FMCGO (Fédération Marocaine de Gynécologie Obstétrique)

- **Rôle** : Référentiel national spécifique à la santé de la femme, à la gynécologie oncologique et à la préservation de la fertilité.
- **Domaines clés** : Directives de dépistage du cancer du col de l'utérus par test HPV de masse, cytoréduction chirurgicale des cancers de l'ovaire (score de Fagotti), surveillance biologique post-môle hydatiforme, et préservation ovarienne/fertilité post-chimiothérapie gonadotoxique (vitrification, analogues de la GnRH).

---

## ⚙️ 2. Processus de Curation et de Structuration

L'extraction et l'intégration des protocoles cliniques dans le dataset suivent un protocole rigoureux en 4 étapes clés :

```mermaid
graph TD
    A["1. Lecture du Protocole"] --> B["2. Extraction des Informations"]
    B --> C["3. Reformulation Clinique"]
    C --> D["4. Structuration JSON & Validation"]
```

### Étape 1 : Lecture du Protocole

- Analyse approfondie des chapitres des guides officiels (AMFROM, SMCO, FMCGO).
- Identification des indications, des dosages, des voies d'administration et des critères d'admissibilité (comorbidités, fonction cardiaque, fonction rénale).

### Étape 2 : Extraction des Informations

- Récupération structurée des composants critiques :
  - **Identifiants** moléculaires et cliniques (mutations BRCA, HER2, drivers EGFR/ALK).
  - **Médicaments** constitutifs, dosages en mg/m² ou selon AUC (formule de Calvert), rythme et cycles.
  - **Effets secondaires** prépondérants (neutropénies, neuropathies, cardiotoxicité).

### Étape 3 : Reformulation Clinique

- Rédaction d'un résumé textuel synthétique (champ `contenu`) décrivant le rationnel thérapeutique.
- Création d'un **scénario patient** (champ `scenario_patient`) illustrant l'application pratique du protocole par un cas concret (présentation, tolérance, issues cliniques).

### Étape 4 : Structuration JSON & Validation

- Traduction en fiches structurées respectant le schéma JSON validé par l'indexeur.
- Validation automatique du type des champs (ID uniques, booléens, listes de mots-clés).

---

## 🧪 3. Méthodologie et Règles de Création des Données Synthétiques

Les cas synthétiques (identifiés par `est_synthetique: true`) ont été créés pour tester la robustesse du système RAG et simuler la diversité de la pratique oncologique quotidienne sans utiliser de données patient réelles (respect strict de la confidentialité).

### Règles Cliniques de Création de Scénarios

Pour garantir la qualité et éviter que les entrées synthétiques ne soient de simples copies paraphrasées des sources cliniques réelles, chaque création/correction doit obligatoirement modifier les variables suivantes :

1. **Données Démographiques distinctes** :
   - Varier systématiquement l'**âge** du patient (ex. modifier de plus de 10 ans par rapport au cas source).
   - Modifier le **sexe** du patient lorsque médicalement possible (ex: introduire le cancer du sein chez l'homme pour illustrer la désescalade de Tolaney, afin de tester l'adaptabilité du modèle).
2. **Contextes Cliniques et Comorbidités Réelles** :
   - Intégrer des pathologies sous-jacentes courantes qui complexifient le traitement :
     - **Diabète** : Adaptation de la corticothérapie pré-médicamenteuse (dexaméthasone) et gestion de la neuropathie diabétique préexistante sous Oxaliplatine.
     - **Insuffisance rénale** : Calcul posologique selon Cockcroft-Gault / Calvert (Carboplatine) et contre-indications formelles (Cisplatine, Pemetrexed).
     - **HTA** : Gestion des pics de pression artérielle et de la protéinurie induits par les molécules anti-angiogéniques (Bevacizumab, Ramucirumab) ou les ITK multi-cibles.
     - **Fragilité Gériatrique** : Évaluation par score G8 <= 14 et désescalade active (monothérapie par Capecitabine ou schémas hebdomadaires allégés).
     - **Métastases Multiples** : Association de traitements de support (acide zolédronique, dénosumab pour métastases osseuses) et adaptation systémique.
3. **Formulation Textuelle Autonome** :
   - Éviter le plagiat de structure. Le vocabulaire clinique, l'ordre de présentation des symptômes, et la description des complications doivent être entièrement réécrits avec des formulations distinctes.

### Mise à jour Tâche A1 : Correction des Entrées Synthétiques Identiques

Les trois premières entrées synthétiques (ONC-SYN-026, ONC-SYN-027, ONC-SYN-028) ont été entièrement remplacées pour respecter les règles de création :

- **ONC-SYN-026** : Changé de "désescalade Tolaney sein femme 48 ans" vers "triple négatif métastatique femme 35 ans, traitement FOLEC palliatif"
- **ONC-SYN-027** : Changé de "cancer sein inflammatoire HER2+ femme 58 ans" vers "carcinome colique BRAF-muté stade IV homme 62 ans, traitement Encorafénib+Cétuximab+Irinotecan"
- **ONC-SYN-028** : Changé de "cancer sein BRCA1 femme 45 ans" vers "adénocarcinome pulmonaire EGFR-dépendant avec métastases cérébrales femme 58 ans, traitement Osimertinib+SRS"

Ces modifications incluent : changement de type cancer, modification des patients (âge, sexe), contextes cliniques différents, protocoles thérapeutiques distincts, et scénarios patients entièrement réécrit.

### Mise à jour Tâche A2 : Ajout de 25 Cas Complexes Manquants

Conformément à l'audit, 25 nouvelles entrées synthétiques ont été ajoutées pour couvrir les comorbidités manquantes :

**Groupe 1 - Cancer + Diabète (5 entrées : ONC-SYN-106 à ONC-SYN-110)**

- Pancréas stade II (HbA1c 7.8%, type II)
- Côlon stade III (diabète type I insulino-dépendant)
- Prostate métastatique (diabète mal équilibré HbA1c 9.4%)
- Estomac stade II-III (diabète type II fragile, malnutrition)
- Foie hépatocarcinome BCLC B (VHC+, diabète)

**Groupe 2 - Cancer + Insuffisance Rénale (5 entrées : ONC-SYN-111 à ONC-SYN-115)**

- Sein triple positif stade III (IR stade 3b DFG 38)
- Rein métastatique stade IV (IR controlatérale DFG 32)
- Lymphome DLBCL stade IV (IR stade 4 DFG 22)
- Vessie stade III (IR obstructive bilatérale)
- Ovaire stade IV (IR modérée DFG 35)

**Groupe 3 - Cancer + HTA (5 entrées : ONC-SYN-116 à ONC-SYN-120)**

- Sein HER2+ stade III (HTA sévère non-contrôlée PA 165/105)
- Rein stade II-III (HTA tumorale + Sunitinib)
- Poumon CBNPC stade III (HTAP modérée secondaire)
- Côlon métastatique (HTA réfractaire + Bevacizumab)
- Lymphome Hodgkin stade IV (HTAP + anthracyclines)

**Groupe 4 - Métastases Multiples (5 entrées : ONC-SYN-121 à ONC-SYN-125)**

- Sein, poumon, foie, côlon, ovaire stade IV avec métastases hépatiques/pulmonaires/osseuses multiples

**Groupe 5 - Patient Âgé Fragile (5 entrées : ONC-SYN-126 à ONC-SYN-130)**

- Sein HER2+, prostate, côlon, poumon, lymphome chez patients >75 ans avec fragilité gériatrique

---

## 🌍 4. Sources Marocaines Additionnelles (Tâche A3)

### D. RORMA (Registry Oncology Radiotherapy Maghreb Africa)

- **Rôle** : Référentiel régional de radiothérapie oncologique pour l'Afrique du Nord.
- **Domaines clés** : Radiothérapie conformationnelle 3D et IMRT pour CBNPC stade III, radiothérapie néoadjuvante cancer rectum stade III (50 Gy + 5-FU), radiothérapie intensité-modulée (IMRT) cancer tête-cou stade III avec réduction toxicités tardives (xérostomie).

### Entrées Synthétiques SMCO/FMCGO/RORMA (11 entrées)

**SMCO (4 entrées)** :

- Dépistage cancer colorectal FIT (homme 58 ans, stade I)
- Dépistage cancer prostate PSA+TR (homme 60 ans, stade I)
- Chimiothérapie intensive triple négatif accès AMO (femme 44 ans, stade IIIB)
- Cancer gastrique métastatique approche palliative (homme 62 ans, stade IV)

**FMCGO (4 entrées)** :

- Dépistage cancer col utérin HPV (femme 35 ans, stade I CIN2)
- Cytoréduction chirurgicale cancer ovaire score Fagotti (femme 58 ans, stade IIIC)
- Préservation fertilité cancer sein HER2+ (femme 28 ans, stade II)
- Suivi post-môle hydatiforme et maladie trophoblastique gestationnelle (femme 32 ans)

**RORMA (3 entrées)** :

- Radiothérapie 3D conformationnelle CBNPC stade III + chimiothérapie concurrent (homme 65 ans)
- Radiothérapie néoadjuvante cancer rectum stade III (homme 58 ans)
- IMRT cancer tête-cou stade III larynge (homme 52 ans)

---

## 📊 5. Structure Actuelle du Dataset

**Total entries : 291 (depuis le lancement du projet)**

- **Entrées non-synthétiques (sources réelles)** : ~160 (AMFROM 2024)
- **Entrées synthétiques correctes** : 131 (ONC-SYN-001 à ONC-SYN-130)
  - ONC-SYN-026 à ONC-SYN-130 : 105 nouvelles entrées (groupe initial + corrections A1, A2, A3)
  - SMC-SYN-001 à SMC-SYN-005 : 5 entrées (santé maternelle) - archive
  - EXT-SYN-001 à EXT-SYN-012 : 12 entrées (extensions diagnostiques) - archive

---

## 🔐 6. Conformité et Qualité des Données

### Principes de Confidentialité

- **Tous les cas synthétiques sont complètement fictifs** : Aucune donnée patient réelle n'est utilisée.
- **Variété clinique maximale** : Les scénarios couvrent comorbidités courantes et cas complexes rares pour tester la robustesse du RAG.
- **Validation médicale** : Chaque entrée a été vérifiée pour conformité médicale par rapport aux guides AMFROM 2024, SMCO 2024, FMCGO 2024, RORMA 2024.

### Métriques de Qualité

- **Absence de doublons** : Validation par ID unique et hash contenu.
- **Complétude des champs obligatoires** : ID, categorie, type_cancer, titre, contenu, scenario_patient, reference.
- **Cohérence logique** : Stade vs métastases, âge vs traitement, comorbidités vs dosages adaptés.

---

## 📋 7. Utilisation du Dataset dans le RAG

Le dataset alimente le système RAG selon deux modes :

1. **Récupération Hybride** : Combine recherche sémantique (embedding vectoriel du contenu) et recherche par métadonnées (type_cancer, stade, reference).
2. **Génération Contextuelle** : Utilise les scénarios patients pour générer réponses personnalisées à des requêtes cliniques spécifiques.
