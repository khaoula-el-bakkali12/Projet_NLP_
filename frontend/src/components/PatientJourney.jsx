import { useState } from 'react'
import {
  Stethoscope, ScanLine, Users, ClipboardList,
  Syringe, Activity, ShieldCheck, ArrowLeft, ArrowRight,
} from 'lucide-react'

// ── Cancer-specific journey data (AMFROM 2024 guidelines) ─────────────────────

const ICONS = [Stethoscope, ScanLine, Users, ClipboardList, Syringe, Activity, ShieldCheck]

const JOURNEYS = {
  general: {
    label: 'Général',
    subtitle: 'Parcours oncologique type — Guidelines AMFROM 2024',
    steps: [
      {
        phase: 'Phase 1', title: 'Consultation Initiale', date: 'J0',
        description: "Première consultation oncologique. Recueil de l'anamnèse, examen clinique complet et suspicion diagnostique.",
        actions: ['Examen clinique', 'Recueil des symptômes', 'Antécédents médicaux', "Demandes d'examens complémentaires"],
      },
      {
        phase: 'Phase 2', title: "Bilan d'Extension", date: 'J7 – J21',
        description: 'Examens complémentaires pour caractériser et stader la tumeur. Biopsie, imagerie et marqueurs biologiques.',
        actions: ['Scanner thoraco-abdomino-pelvien', 'IRM / TEP-scan', 'Biopsie et anatomopathologie', 'Marqueurs tumoraux'],
      },
      {
        phase: 'Phase 3', title: 'RCP — Concertation Pluridisciplinaire', date: 'J21 – J28',
        description: 'Réunion de Concertation Pluridisciplinaire. Décision collégiale entre oncologues, chirurgiens, radiologues et anatomopathologistes.',
        actions: ['Présentation du dossier', 'Discussion des options thérapeutiques', 'Décision consensuelle', 'Rédaction du compte-rendu RCP'],
      },
      {
        phase: 'Phase 4', title: 'Plan de Traitement Personnalisé', date: 'J28 – J35',
        description: "Annonce du diagnostic et élaboration d'un Programme Personnalisé de Soins (PPS) en accord avec le patient.",
        actions: ["Consultation d'annonce", 'Programme Personnalisé de Soins (PPS)', 'Consentement éclairé', 'Coordination soins de support'],
      },
      {
        phase: 'Phase 5', title: 'Traitement Oncologique', date: 'J35+',
        description: "Mise en œuvre du protocole thérapeutique : chimiothérapie, chirurgie, radiothérapie, immunothérapie ou thérapie ciblée.",
        actions: ['Chimiothérapie néoadjuvante / adjuvante', "Chirurgie d'exérèse", 'Radiothérapie', 'Immunothérapie / Thérapie ciblée'],
      },
      {
        phase: 'Phase 6', title: 'Évaluation de Réponse', date: 'S12 – S16',
        description: 'Réévaluation tumorale à mi-traitement et en fin de traitement pour adapter la stratégie thérapeutique.',
        actions: ['Scanner de réévaluation', 'Évaluation selon critères RECIST', 'Adaptation du protocole si nécessaire', '2ème RCP si changement de stratégie'],
      },
      {
        phase: 'Phase 7', title: 'Surveillance Post-Traitement', date: 'M6 – M60',
        description: 'Suivi régulier après la fin du traitement pour détecter précocement une récidive et gérer les séquelles.',
        actions: ['Consultations semestrielles puis annuelles', 'Examens biologiques (marqueurs)', 'Imagerie de surveillance', 'Soins de support à long terme'],
      },
    ],
  },

  sein: {
    label: 'Sein',
    subtitle: 'Carcinome mammaire — Protocole AC-T / EC-T · AMFROM 2024',
    steps: [
      {
        phase: 'Phase 1', title: 'Consultation Initiale', date: 'J0',
        description: 'Présentation clinique : masse palpable, écoulement mamelonnaire, rétraction cutanée ou douleur mammaire. Évaluation du risque familial (BRCA).',
        actions: ['Examen des seins (inspection + palpation)', 'Aires ganglionnaires axillaires et sus-claviculaires', 'Interrogatoire familial BRCA1/BRCA2', 'Score de risque génétique'],
      },
      {
        phase: 'Phase 2', title: "Bilan Diagnostique", date: 'J7 – J21',
        description: 'Confirmation histologique et caractérisation moléculaire complète : statut hormonal (RE, RP), HER2, Ki-67. Imagerie pour staging.',
        actions: ['Mammographie bilatérale + échographie', 'IRM mammaire (si dense ou HER2+)', 'Biopsie guidée (microbiopsie / macrobiopsie)', 'Récepteurs hormonaux RE/RP · HER2 · Ki-67 · BRCA'],
      },
      {
        phase: 'Phase 3', title: 'RCP Oncologie Sénologique', date: 'J21 – J28',
        description: 'Décision collégiale selon le sous-type moléculaire (Luminal A/B, HER2+, Triple négatif) et le stade TNM. Discussion traitement néoadjuvant vs adjuvant.',
        actions: ['Staging TNM (cT cN cM)', 'Classification sous-type moléculaire', 'Indication néoadjuvance vs adjuvance', 'Discussion chirurgie conservatrice vs mastectomie'],
      },
      {
        phase: 'Phase 4', title: 'Programme Personnalisé de Soins', date: 'J28 – J35',
        description: "Annonce du diagnostic et du plan thérapeutique. Protocole adapté au sous-type : AC-T, EC-T, ou Pertuzumab+Trastuzumab si HER2+.",
        actions: ["Consultation d'annonce (oncologue + infirmière)", 'Choix du protocole : AC-T · EC-T · TCbHP (HER2+)', 'Bilan pré-chimiothérapie (NFS, bilan hépatique, cardiaque)', 'Port-à-cath / PICC-line'],
      },
      {
        phase: 'Phase 5', title: 'Traitement — Chimiothérapie & Chirurgie', date: 'M1 – M6',
        description: 'Chimiothérapie néoadjuvante AC×4 → Taxol×12 (±Trastuzumab si HER2+). Chirurgie après réponse : tumorectomie + curage ou mastectomie. Radiothérapie adjuvante.',
        actions: ['AC×4 (Adriamycine 60 mg/m² + Cyclophosphamide 600 mg/m²) J1=J21', 'Paclitaxel hebdomadaire ×12 (80 mg/m²)', 'Trastuzumab (8→6 mg/kg) si HER2+ · 1 an total', 'Chirurgie + Radiothérapie adjuvante (50 Gy)'],
      },
      {
        phase: 'Phase 6', title: 'Évaluation de Réponse', date: 'S12 & S24',
        description: "Évaluation mi-parcours et en fin de chimiothérapie néoadjuvante. Réponse pathologique complète (RCp) = facteur pronostique majeur. CA 15-3 de suivi.",
        actions: ['IRM mammaire à mi-traitement (S12)', "Critères de réponse RECIST 1.1 / RECIST mammaire", 'CA 15-3 · ACE', 'Adapatation : switch capécitabine si non-RCp (TNBC)'],
      },
      {
        phase: 'Phase 7', title: 'Surveillance Post-Traitement', date: 'M6 – M120',
        description: 'Suivi clinique et radiologique semi-annuel. Hormonothérapie adjuvante (Tamoxifène ou IA) 5–10 ans si RE+. Surveillance cardiaque (Trastuzumab).',
        actions: ['Mammographie annuelle bilatérale', 'Tamoxifène 20 mg/j (pré-ménopause) ou IA (post-ménopause) × 5–10 ans', 'Échocardiographie / an si Trastuzumab', 'Consultation onco semestrielle puis annuelle'],
      },
    ],
  },

  poumon: {
    label: 'Poumon',
    subtitle: 'CBNPC (carcinome bronchique non à petites cellules) — AMFROM 2024',
    steps: [
      {
        phase: 'Phase 1', title: 'Consultation Initiale', date: 'J0',
        description: "Signes d'alerte : toux persistante, hémoptysie, dyspnée d'effort, douleur thoracique, perte de poids ≥10 %. Tabagisme = facteur majeur.",
        actions: ['Anamnèse tabagique (paquets-années)', 'Examen respiratoire complet', 'Saturation O₂ et EFR', 'Radiographie thoracique de face + profil'],
      },
      {
        phase: 'Phase 2', title: 'Bilan Diagnostique & Moléculaire', date: 'J7 – J21',
        description: 'TDM thoracique + TEP-scan pour staging. Biopsie bronchique ou transthoracique. Panel NGS obligatoire : EGFR, ALK, ROS1, KRAS G12C, PD-L1 (TPS%).',
        actions: ['TDM thoraco-abdomino-pelvien avec injection', 'TEP-scan (18F-FDG)', 'Bronchoscopie + biopsie / biopsie transthoracique scanno-guidée', 'NGS : EGFR · ALK · ROS1 · BRAF · KRAS G12C · PD-L1 TPS'],
      },
      {
        phase: 'Phase 3', title: 'RCP Thoracique', date: 'J21 – J28',
        description: "Décision selon staging UICC 8ème édition et profil moléculaire. Opérabilité évaluée (VEMS, DLCO). Identification de la mutation driver = guide thérapeutique.",
        actions: ['Staging UICC 8ème (I–IV)', 'Évaluation fonction respiratoire (VEMS ≥ 50%)', "Score ECOG-PS (0-2 = éligible soins intensifs)", 'Mutation driver → algorithme TKI vs ICI vs chimio'],
      },
      {
        phase: 'Phase 4', title: 'Plan Thérapeutique Adapté', date: 'J28 – J35',
        description: "Plan selon mutation et stade. EGFR+ → Osimertinib. ALK+ → Alectinib. PD-L1 ≥50% → Pembrolizumab. Sans mutation driver stade IV → Platine doublet + ICI.",
        actions: ['EGFR muté → Osimertinib 80 mg/j (1ère ligne)', 'ALK/ROS1 → Alectinib 600 mg × 2/j', 'PD-L1 ≥50% → Pembrolizumab 200 mg J1=J21', "Pas de mutation → Cisplatine/Carboplatine + Pemetrexed (non squameux)"],
      },
      {
        phase: 'Phase 5', title: 'Traitement Systémique', date: 'M1 – M6+',
        description: "Mise en route du protocole selon profil moléculaire. TKI : prise orale continue. Immunothérapie ou chimio-immunothérapie : cycles J1=J21 ou J1=J28.",
        actions: ['TKI oral (Osimertinib / Alectinib) : continu jusqu\'à progression', 'Pembrolizumab 200 mg IV J1=J21 × 35 cycles max', 'Platine + Pemetrexed × 4–6 cycles (non squameux)', 'Platine + Gemcitabine × 4–6 cycles (squameux)'],
      },
      {
        phase: 'Phase 6', title: 'Évaluation de Réponse', date: 'S9 – S12',
        description: "TDM thoracique après 2–3 cycles ou 3 mois de TKI. Critères RECIST 1.1. En cas de progression sous TKI : biopsie liquide ctDNA (T790M pour EGFR).",
        actions: ['TDM TAP ± TEP à S9–S12', 'Critères RECIST 1.1 (RC · RP · SD · PD)', 'Biopsie liquide ctDNA si progression TKI (T790M)', 'Switch 2ème ligne si progression (Osimertinib → chimio)'],
      },
      {
        phase: 'Phase 7', title: 'Surveillance & Soins de Support', date: 'M6 – M36',
        description: "TDM semestriel. Aide au sevrage tabagique. Prise en charge pneumologique. Soins de support (douleur, nutrition, psycho-oncologie).",
        actions: ['TDM thoracique semestriel', 'Consultation pneumologie + aide sevrage tabagique', 'Soins palliatifs précoces si stade IV (OMS)', 'NFS mensuelle sous TKI (hépatotoxicité)'],
      },
    ],
  },

  colorectal: {
    label: 'Colorectal',
    subtitle: 'Cancer colorectal (côlon et rectum) — Protocole FOLFOX/FOLFIRI · AMFROM 2024',
    steps: [
      {
        phase: 'Phase 1', title: 'Consultation Initiale', date: 'J0',
        description: "Symptômes évocateurs : rectorragie, méléna, troubles du transit (diarrhée ou constipation alternants), douleurs abdominales, anémie ferriprive inexpliquée.",
        actions: ['Toucher rectal systématique', 'NFS (anémie ferriprive ?)', 'Dosage ACE (antigène carcino-embryonnaire)', 'Score de risque familial (Lynch, PAF)'],
      },
      {
        phase: 'Phase 2', title: 'Coloscopie & Bilan de Staging', date: 'J7 – J21',
        description: "Coloscopie totale avec biopsie = gold standard diagnostique. TDM TAP pour staging. Statut MSI (instabilité microsatellitaire) et RAS/BRAF obligatoires.",
        actions: ['Coloscopie totale + biopsies multiples', 'TDM thoraco-abdomino-pelvien (TAP) injecté', 'IRM pelvienne si cancer du rectum (marge, envahissement sphinctérien)', 'RAS (KRAS/NRAS) · BRAF V600E · MSI/MMR · HER2'],
      },
      {
        phase: 'Phase 3', title: 'RCP Digestive', date: 'J21 – J28',
        description: "Décision selon localisation (côlon droit/gauche/rectum), stade TNM, résécabilité des métastases hépatiques/pulmonaires. MSI-H = immunothérapie en 1ère ligne.",
        actions: ['Staging TNM (côlon) / TNM + distance à la marge (rectum)', 'Résécabilité hépatique évaluée par chirurgien HPB', 'MSI-H stade IV → Pembrolizumab 1ère ligne', 'Rectum localement avancé → radiochimiothérapie néoadjuvante'],
      },
      {
        phase: 'Phase 4', title: 'Plan Thérapeutique', date: 'J28 – J35',
        description: "Côlon stade II–III : chirurgie première puis FOLFOX adjuvant × 12 cycles. Rectum localement avancé : radiochimiothérapie (45–50 Gy + capécitabine) → chirurgie → adjuvant.",
        actions: ['Côlon : colectomie segmentaire laparoscopique', 'Rectum haut risque : RCT 45 Gy + Capécitabine → TME', 'FOLFOX (Oxaliplatine 85 mg/m² + Leucovorin + 5-FU) J1=J14', 'Bevacizumab ou Cetuximab (RAS sauvage) si métastatique'],
      },
      {
        phase: 'Phase 5', title: 'Traitement — Chirurgie & Chimiothérapie', date: 'M1 – M6',
        description: "Chirurgie carcinologique (résection R0) puis chimiothérapie adjuvante ou traitement de la maladie métastatique selon statut RAS/BRAF/MSI.",
        actions: ['Résection colique + curage ganglionnaire D3', 'FOLFOX4 × 12 cycles (stade III adjuvant)', "FOLFIRI + Bevacizumab (RAS muté, 1ère ligne métastatique)", 'FOLFOXIRI + Bevacizumab (si performant, haut risque)'],
      },
      {
        phase: 'Phase 6', title: 'Évaluation de Réponse', date: 'S12 – S18',
        description: "TDM après 3–4 cycles de chimiothérapie. Suivi ACE. Réévaluation résécabilité des métastases hépatiques (down-staging). Critères RECIST 1.1.",
        actions: ['TDM TAP après 4 cycles (RECIST 1.1)', 'Dosage ACE · CA 19-9', 'Réévaluation résécabilité hépatique par chirurgien HPB', 'Coloscopie de contrôle à 1 an (polypes)'],
      },
      {
        phase: 'Phase 7', title: 'Surveillance Post-Traitement', date: 'M6 – M60',
        description: "Suivi clinique et biologique semi-annuel 5 ans. Coloscopie de contrôle à 1 an puis 3 ans. Dépistage familial si Lynch ou âge < 50 ans.",
        actions: ['Consultation onco semestrielle × 3 ans puis annuelle', 'ACE + NFS semestriel', 'TDM TAP annuel × 5 ans', 'Coloscopie : 1 an, 3 ans, 5 ans'],
      },
    ],
  },

  ovaire: {
    label: 'Ovaire',
    subtitle: 'Carcinome ovarien — Carboplatine + Paclitaxel · AMFROM 2024',
    steps: [
      {
        phase: 'Phase 1', title: 'Consultation Initiale', date: 'J0',
        description: "Présentation souvent tardive (stade III–IV) : distension abdominale, douleurs pelviennes, dyspepsie, pollakiurie. CA-125 élevé = signal d'alerte.",
        actions: ['Examen gynécologique + toucher vaginal', 'Dosage CA-125 et HE4 (ROMA score)', 'Échographie pelvienne endovaginale', 'Évaluation nutritionnelle (albumine, poids)'],
      },
      {
        phase: 'Phase 2', title: 'Bilan Diagnostique', date: 'J7 – J21',
        description: "TDM TAP ± TEP pour évaluer la carcinose péritonéale et les métastases. Test BRCA1/2 germinal obligatoire (impacte le traitement de maintenance).",
        actions: ['TDM thoraco-abdomino-pelvien (carcinose péritonéale ?)', 'Score de résécabilité Fagotti / Bristow', 'BRCA1/2 germinal + somatic (NGS tumoral)', 'CA-125, HE4, CA 19-9, ACE, NFS, bilan hépatique'],
      },
      {
        phase: 'Phase 3', title: 'RCP Gynécologie Oncologique', date: 'J21 – J28',
        description: "Évaluation de la résécabilité optimale (résidu tumoral R0 = objectif). Chirurgie première vs chimiothérapie néoadjuvante (NACT) selon score Fagotti.",
        actions: ['Staging FIGO (I–IV)', 'Score Fagotti ≥ 8 → NACT × 3 avant chirurgie', 'Chirurgie d\'intervalle après NACT × 3 cycles', 'Chimiothérapie IP/IV si résidu nul (option)'],
      },
      {
        phase: 'Phase 4', title: 'Plan Thérapeutique', date: 'J28 – J35',
        description: "Carboplatine AUC5–6 + Paclitaxel 175 mg/m² × 6 cycles J1=J21. Bevacizumab ajouté si stade IIIB–IV. Olaparib (PARP inhibiteur) en maintenance si BRCA+.",
        actions: ['Carboplatine AUC5 + Paclitaxel 175 mg/m² J1=J21 × 6 cycles', 'Bevacizumab 15 mg/kg si stade avancé (ICON7)', 'BRCA1/2+ : Olaparib 300 mg × 2/j maintenance × 2 ans', 'BRCA sauvage : Niraparib ou Rucaparib (maintenance)'],
      },
      {
        phase: 'Phase 5', title: 'Chirurgie & Chimiothérapie', date: 'M1 – M5',
        description: "Cytoreduction maximale (R0 = survie ×2 vs R1/R2). Chimiothérapie adjuvante Carboplatine+Paclitaxel × 6 cycles. Maintenance PARP si BRCA+.",
        actions: ['Chirurgie cytoréductrice : hystérectomie + annexectomie + omentectomie + curage', 'Carboplatine AUC 5-6 + Paclitaxel × 6 cycles', 'Chimio intrapéritonéale IP (option stade III R0)', 'Début Olaparib maintenance 4–8 sem après dernier cycle'],
      },
      {
        phase: 'Phase 6', title: 'Évaluation de Réponse', date: 'S18 – S24',
        description: "CA-125 après chaque cycle. TDM en fin de traitement. Réponse complète = CA-125 normalisé + TDM normal. Récidive précoce (< 6 mois) = platine-résistante.",
        actions: ['CA-125 + HE4 après chaque cycle', 'TDM TAP en fin de chimio (cycle 6)', 'Critères Gynecologic Cancer InterGroup (GCIG)', 'Platine-sensible (> 6 mois) vs platine-résistante (< 6 mois)'],
      },
      {
        phase: 'Phase 7', title: 'Surveillance & Maintenance', date: 'M6 – M48',
        description: "Suivi CA-125 semestriel. Olaparib maintenance 2 ans (BRCA+). Bevacizumab maintenance jusqu\'à progression. TDM annuel. Dépistage familial BRCA.",
        actions: ['CA-125 + examen clinique tous les 3 mois × 2 ans', 'TDM TAP semestriel × 2 ans puis annuel', 'Poursuite Olaparib 2 ans ou jusqu\'à progression', 'Conseil génétique famille (BRCA1/2 germinal)'],
      },
    ],
  },

  prostate: {
    label: 'Prostate',
    subtitle: 'Cancer de la prostate — Protocole ADT ± Enzalutamide · AMFROM 2024',
    steps: [
      {
        phase: 'Phase 1', title: 'Consultation Initiale', date: 'J0',
        description: "Dépistage par PSA chez homme ≥ 50 ans (ou ≥ 45 ans si antécédent familial). Symptômes tardifs : troubles mictionnels (LUTS), nycturie, dysurie.",
        actions: ['Dosage PSA total + PSA libre (ratio)', 'Toucher rectal', 'Score IPSS (troubles mictionnels)', 'Antécédents familiaux prostate / BRCA2'],
      },
      {
        phase: 'Phase 2', title: 'Bilan Diagnostique', date: 'J7 – J21',
        description: "IRM multiparamétrique (mpMRI) prostatique avant biopsie (score PI-RADS). Biopsies écho-guidées fusionnées (12 carottes + ciblées). Score de Gleason / Groupe ISUP.",
        actions: ['IRM prostatique multiparamétrique (PI-RADS 1–5)', 'Biopsies prostatiques écho-guidées avec fusion IRM (12+)', 'Score de Gleason → Groupe ISUP (1–5)', 'Scintigraphie osseuse + TDM TAP si PSA > 20 ou Gleason ≥ 8'],
      },
      {
        phase: 'Phase 3', title: 'RCP Urologique', date: 'J21 – J28',
        description: "Stratification selon risque D'Amico (faible / intermédiaire / haut) ou classification NCCN. Évaluation de l'âge physiologique et des comorbidités.",
        actions: ["Groupe de risque D'Amico (PSA · Gleason · stade T)", 'Espérance de vie estimée (> 10 ans = traitement curatif)', 'Discussion surveillance active (faible risque) vs traitement', 'TEP-Choline ou PSMA si haut risque ou rechute'],
      },
      {
        phase: 'Phase 4', title: 'Plan Thérapeutique', date: 'J28 – J35',
        description: "Faible risque : surveillance active ou RT/prostatectomie. Haut risque localisé : prostatectomie totale ou RT + hormonothérapie longue durée (2–3 ans). Métastatique : ADT + Enzalutamide/Apalutamide.",
        actions: ['Faible risque : surveillance active (PSA + biopsies/2 ans)', 'Risque intermédiaire/haut : prostatectomie robot-assistée ou RT (76–80 Gy)', 'RT + ADT (LHRH agoniste) 2–3 ans si haut risque', 'Métastatique : ADT + Enzalutamide 160 mg/j ou Docétaxel × 6'],
      },
      {
        phase: 'Phase 5', title: 'Traitement', date: 'M1 – M6+',
        description: "Prostatectomie totale robot-assistée ou radiothérapie externe conformationnelle 3D / IMRT. Hormonothérapie (ADT) par LHRH agoniste. Enzalutamide en mCRPC.",
        actions: ['Prostatectomie totale laparoscopique robot-assistée (Da Vinci)', 'RT conformationnelle IMRT 76–80 Gy ± boost HDR-brachy', 'ADT : Leuproréline 3,75 mg/M IM ou Goséréline 3,6 mg SC', 'Enzalutamide 160 mg/j (mCRPC) ou Apalutamide (nmCRPC)'],
      },
      {
        phase: 'Phase 6', title: 'Évaluation de Réponse', date: 'S12 & M6',
        description: "PSA nadir après prostatectomie (< 0,1 ng/mL) ou après RT (< 0,5 ng/mL). Rechute biochimique = PSA ≥ 0,2 après prostatectomie ou > nadir+2 après RT.",
        actions: ['PSA à 6 sem, 3 mois, 6 mois post-traitement', 'Définition rechute biochimique (PSA > 0,2)', 'TEP-PSMA si rechute (très sensible)', 'Testostéronémie sous ADT (castration < 50 ng/dL)'],
      },
      {
        phase: 'Phase 7', title: 'Surveillance Long Terme', date: 'M6 – M120',
        description: "Suivi PSA semestriel × 5 ans puis annuel. Gestion des effets secondaires de l'hormonothérapie (ostéoporose, risque cardiovasculaire). Densitométrie osseuse.",
        actions: ['PSA + testostérone semestriel × 5 ans', 'DEXA (densitométrie) si ADT > 6 mois', 'Acide zolédronique / Dénosumab si ostéoporose', 'Rééducation pelvi-périnéale (incontinence post-prostatectomie)'],
      },
    ],
  },

  col_uterin: {
    label: 'Col Utérin',
    subtitle: 'Carcinome du col utérin — RCT + Cisplatine · AMFROM 2024',
    steps: [
      {
        phase: 'Phase 1', title: 'Consultation Initiale', date: 'J0',
        description: "Symptômes : métrorragies post-coïtales ou intermenstruelles, leucorrhées malodorantes, douleurs pelviennes. Dépistage par frottis cervico-vaginal (FCV) recommandé.",
        actions: ['Examen au spéculum + colposcopie', 'Frottis cervico-vaginal (FCV) et tests HPV HR', 'Bilan gynécologique complet', 'Génotypage HPV (16, 18 = haut risque)'],
      },
      {
        phase: 'Phase 2', title: 'Bilan Diagnostique', date: 'J7 – J21',
        description: "Biopsie cervicale (punch ou conisation) pour confirmation histologique. IRM pelvienne = examen de référence pour staging local. SCC (antigène).",
        actions: ['Biopsie cervicale dirigée / conisation diagnostique', 'IRM pelvienne (paramètres, vagin, ganglions)', 'TDM thoraco-abdomino-pelvien (ganglions para-aortiques ?)', 'SCC (squamous cell carcinoma antigen) · CA 125'],
      },
      {
        phase: 'Phase 3', title: 'RCP Gynécologie Oncologique', date: 'J21 – J28',
        description: "Staging FIGO 2018 (IB1–IVB). Décision opérabilité : chirurgie si stade IB1–IIA1, radiochirurgie ou radiochimiothérapie si stade ≥ IB2.",
        actions: ['Staging FIGO 2018 (basé IRM + TDM)', 'Stade IB1-IIA1 : chirurgie (Wertheim)', 'Stade IB2–IVA : radiochimiothérapie concomitante (RCT)', 'Ganglions para-aortiques → curiethérapie étendue'],
      },
      {
        phase: 'Phase 4', title: 'Plan Thérapeutique', date: 'J28 – J35',
        description: "Stade IB1–IIA1 : hystérectomie radicale (Wertheim-Meigs) + curage ganglionnaire. Stade IB2–IVA : RCT (45–50 Gy + Cisplatine hebdomadaire) puis curiethérapie.",
        actions: ['Chirurgie : hystérectomie radicale type C (Wertheim) + curage pelvien', 'RCT : RT externe 45–50 Gy + Cisplatine 40 mg/m² hebdo × 5', 'Curiethérapie de haut débit de dose (HDR) après RCT', 'Brachythérapie utérovaginale (applicateur Ring+Tandem)'],
      },
      {
        phase: 'Phase 5', title: 'Radiochimio & Curiethérapie', date: 'M1 – M2',
        description: "Radiochimiothérapie concomitante : RT pelvienne 45 Gy en 25 fractions + Cisplatine 40 mg/m² × 5 semaines. Curiethérapie HDR (5 × 5,5 Gy) pour boost cervical.",
        actions: ['RT pelvienne IMRT 45 Gy / 25 fractions (5 sem)', 'Cisplatine 40 mg/m² J1 · J8 · J15 · J22 · J29', 'Curiethérapie HDR : 5 fractions × 5,5 Gy (Ring+Tandem)', 'Hydratation IV pré/post-Cisplatine (néphroprotection)'],
      },
      {
        phase: 'Phase 6', title: 'Évaluation de Réponse', date: 'S8 – S12',
        description: "IRM pelvienne 3 mois après fin du traitement = gold standard. SCC doit se normaliser. TEP-scan si doute sur récidive ganglionnaire ou métastase.",
        actions: ['IRM pelvienne à 3 mois post-traitement', 'Dosage SCC · CA 125', 'TEP-scan si IRM non concluante', 'Consultation gynécologique (tolérance, compliance)'],
      },
      {
        phase: 'Phase 7', title: 'Surveillance Post-Traitement', date: 'M6 – M60',
        description: "Suivi gynécologique trimestriel × 2 ans puis semestriel. Prise en charge des effets secondaires tardifs : fistules, sténose vaginale, cystite radique.",
        actions: ['Examen gynécologique + frottis vaginal / 3 mois × 2 ans', 'IRM pelvienne annuelle × 5 ans', 'Dilatateur vaginal (prévention sténose)', 'Prise en charge cystite radique / rectite (effets tardifs)'],
      },
    ],
  },
}

const CANCER_LIST = [
  { key: 'general',    label: 'Général' },
  { key: 'sein',       label: 'Sein' },
  { key: 'poumon',     label: 'Poumon' },
  { key: 'colorectal', label: 'Colorectal' },
  { key: 'ovaire',     label: 'Ovaire' },
  { key: 'prostate',   label: 'Prostate' },
  { key: 'col_uterin', label: 'Col Utérin' },
]

export default function PatientJourney() {
  const [cancerKey, setCancerKey] = useState('general')
  const [selected,  setSelected]  = useState(1)

  const journey = JOURNEYS[cancerKey]
  const steps   = journey.steps.map((s, i) => ({ ...s, id: i + 1, icon: ICONS[i] }))
  const step    = steps.find(s => s.id === selected)
  const Icon    = step?.icon

  function switchCancer(key) {
    setCancerKey(key)
    setSelected(1)
  }

  return (
    <div className="space-y-6">

      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-medical-600 flex items-center justify-center">
          <Activity className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="font-bold text-2xl text-slate-900 font-display tracking-tight">Parcours Patient Type</h2>
          <p className="text-slate-400 mt-0.5 text-sm">{journey.subtitle}</p>
        </div>
      </div>

      {/* Cancer selector */}
      <div className="flex flex-wrap gap-2">
        {CANCER_LIST.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => switchCancer(key)}
            className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all
              ${cancerKey === key
                ? 'bg-medical-600 text-white shadow-sm'
                : 'bg-slate-100 text-slate-500 hover:bg-slate-200 hover:text-slate-700'}`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Progress dots */}
      <div className="flex items-center gap-1.5">
        {steps.map(s => (
          <button key={s.id} onClick={() => setSelected(s.id)}
            className={`h-1.5 rounded-full transition-all duration-300 ${
              s.id === selected ? 'w-8 bg-medical-600' : 'w-4 bg-slate-200 hover:bg-slate-300'
            }`}
          />
        ))}
        <span className="ml-3 text-xs text-slate-400 font-medium">{selected} / {steps.length}</span>
      </div>

      {/* Main grid */}
      <div className="grid lg:grid-cols-[300px_1fr] gap-5 items-start">

        {/* ── Sidebar timeline ── */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          {steps.map((s) => {
            const SIcon    = s.icon
            const isActive = s.id === selected
            return (
              <button key={s.id} onClick={() => setSelected(s.id)}
                className={`w-full flex items-center gap-3 px-5 py-4 text-left transition-all border-b border-slate-100 last:border-0 relative
                  ${isActive ? 'bg-medical-600' : 'hover:bg-slate-50'}`}>
                {isActive && <div className="absolute left-0 top-0 bottom-0 w-1 bg-white/30 rounded-r" />}

                <div className={`w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 transition-colors
                  ${isActive ? 'bg-white/20' : 'bg-slate-100'}`}>
                  <SIcon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                </div>

                <div className="flex-1 min-w-0">
                  <p className={`text-[11px] font-bold uppercase tracking-widest mb-0.5
                    ${isActive ? 'text-white/60' : 'text-slate-400'}`}>
                    {s.phase}
                  </p>
                  <p className={`text-sm font-semibold leading-tight truncate
                    ${isActive ? 'text-white' : 'text-slate-700'}`}>
                    {s.title}
                  </p>
                  <p className={`text-xs mt-0.5 ${isActive ? 'text-white/50' : 'text-slate-400'}`}>
                    {s.date}
                  </p>
                </div>
              </button>
            )
          })}
        </div>

        {/* ── Detail panel ── */}
        {step && (
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="h-1 bg-medical-600 w-full" />

            <div className="p-8">
              {/* Step header */}
              <div className="flex items-start gap-5 mb-8">
                <div className="w-14 h-14 rounded-2xl bg-medical-600 flex items-center justify-center flex-shrink-0 shadow-md shadow-medical-600/20">
                  <Icon className="w-7 h-7 text-white" />
                </div>
                <div className="flex-1 pt-1">
                  <div className="flex items-center gap-2 mb-1.5">
                    <span className="text-xs font-bold text-medical-600 uppercase tracking-widest">{step.phase}</span>
                    <span className="text-slate-200">·</span>
                    <span className="text-xs text-slate-400 font-medium">{step.date}</span>
                  </div>
                  <h3 className="text-2xl font-bold text-slate-900 tracking-tight">{step.title}</h3>
                </div>
              </div>

              {/* Description */}
              <p className="text-slate-500 leading-relaxed mb-8 text-[15px] border-l-2 border-slate-100 pl-4">
                {step.description}
              </p>

              {/* Actions */}
              <div className="mb-8">
                <p className="text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-3">Actions clés</p>
                <div className="grid sm:grid-cols-2 gap-2.5">
                  {step.actions.map((action, i) => (
                    <div key={i} className="flex items-center gap-3 p-4 rounded-xl bg-slate-50 border border-slate-100 hover:border-slate-200 transition-colors">
                      <div className="w-6 h-6 rounded-full bg-medical-600 flex items-center justify-center flex-shrink-0">
                        <span className="text-[10px] font-bold text-white">{i + 1}</span>
                      </div>
                      <span className="text-sm text-slate-700 font-medium leading-tight">{action}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Navigation */}
              <div className="flex items-center justify-between pt-6 border-t border-slate-100">
                <button
                  onClick={() => setSelected(s => Math.max(1, s - 1))}
                  disabled={selected === 1}
                  className="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-slate-500 hover:text-slate-900 hover:bg-slate-50 rounded-lg disabled:opacity-30 transition-all"
                >
                  <ArrowLeft className="w-4 h-4" /> Précédente
                </button>

                <div className="flex gap-1">
                  {steps.map(s => (
                    <div key={s.id}
                      className={`w-1.5 h-1.5 rounded-full transition-colors ${s.id === selected ? 'bg-medical-600' : 'bg-slate-200'}`}
                    />
                  ))}
                </div>

                <button
                  onClick={() => setSelected(s => Math.min(steps.length, s + 1))}
                  disabled={selected === steps.length}
                  className="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-slate-500 hover:text-slate-900 hover:bg-slate-50 rounded-lg disabled:opacity-30 transition-all"
                >
                  Suivante <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
