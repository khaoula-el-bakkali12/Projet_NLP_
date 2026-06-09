import { useState } from 'react'
import {
  Stethoscope, ScanLine, Users, ClipboardList,
  Syringe, Activity, ShieldCheck, ArrowLeft, ArrowRight,
} from 'lucide-react'

const STEPS = [
  {
    id: 1, icon: Stethoscope, phase: 'Phase 1', title: 'Consultation Initiale', date: 'J0',
    description: "Première consultation oncologique. Recueil de l'anamnèse, examen clinique complet et suspicion diagnostique.",
    actions: ['Examen clinique', 'Recueil des symptômes', 'Antécédents médicaux', "Demandes d'examens"],
  },
  {
    id: 2, icon: ScanLine, phase: 'Phase 2', title: "Bilan d'Extension", date: 'J7 – J21',
    description: 'Examens complémentaires pour caractériser et stader la tumeur. Biopsie, imagerie et marqueurs biologiques.',
    actions: ['Scanner thoraco-abdomino-pelvien', 'IRM / TEP-scan', 'Biopsie et anatomopathologie', 'Marqueurs tumoraux (HER2, BRCA…)'],
  },
  {
    id: 3, icon: Users, phase: 'Phase 3', title: 'RCP — Concertation Pluridisciplinaire', date: 'J21 – J28',
    description: 'Réunion de Concertation Pluridisciplinaire. Décision collégiale entre oncologues, chirurgiens, radiologues et anatomopathologistes.',
    actions: ['Présentation du dossier', 'Discussion des options thérapeutiques', 'Décision consensuelle', 'Rédaction du compte-rendu RCP'],
  },
  {
    id: 4, icon: ClipboardList, phase: 'Phase 4', title: 'Plan de Traitement Personnalisé', date: 'J28 – J35',
    description: "Annonce du diagnostic et élaboration d'un Programme Personnalisé de Soins (PPS) en accord avec le patient.",
    actions: ["Consultation d'annonce", 'Programme Personnalisé de Soins', 'Consentement éclairé', 'Coordination soins de support'],
  },
  {
    id: 5, icon: Syringe, phase: 'Phase 5', title: 'Traitement Oncologique', date: 'J35+',
    description: "Mise en œuvre du protocole thérapeutique : chimiothérapie, chirurgie, radiothérapie, immunothérapie ou thérapie ciblée.",
    actions: ['Chimiothérapie néoadjuvante / adjuvante', "Chirurgie d'exérèse", 'Radiothérapie', 'Immunothérapie / Thérapie ciblée'],
  },
  {
    id: 6, icon: Activity, phase: 'Phase 6', title: 'Évaluation de Réponse', date: 'S12 – S16',
    description: 'Réévaluation tumorale à mi-traitement et en fin de traitement pour adapter la stratégie thérapeutique.',
    actions: ['Scanner de réévaluation', 'Évaluation selon critères RECIST', 'Adaptation du protocole si nécessaire', '2ème RCP si changement de stratégie'],
  },
  {
    id: 7, icon: ShieldCheck, phase: 'Phase 7', title: 'Surveillance Post-Traitement', date: 'M6 – M60',
    description: 'Suivi régulier après la fin du traitement pour détecter précocement une récidive et gérer les séquelles.',
    actions: ['Consultations semestrielles puis annuelles', 'Examens biologiques (marqueurs)', 'Imagerie de surveillance', 'Soins de support à long terme'],
  },
]

export default function PatientJourney() {
  const [selected, setSelected] = useState(1)
  const step = STEPS.find(s => s.id === selected)
  const Icon = step?.icon

  return (
    <div className="space-y-8">

      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-medical-600 flex items-center justify-center">
          <Activity className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="font-bold text-2xl text-slate-900 font-display tracking-tight">Parcours Patient Type</h2>
          <p className="text-slate-400 mt-0.5 text-sm">Protocole oncologique de référence — Guidelines AMFROM 2024</p>
        </div>
      </div>

      {/* Progress dots */}
      <div className="flex items-center gap-1.5">
        {STEPS.map(s => (
          <button key={s.id} onClick={() => setSelected(s.id)}
            className={`h-1.5 rounded-full transition-all duration-300 ${
              s.id === selected ? 'w-8 bg-medical-600' : 'w-4 bg-slate-200 hover:bg-slate-300'
            }`}
          />
        ))}
        <span className="ml-3 text-xs text-slate-400 font-medium">{selected} / {STEPS.length}</span>
      </div>

      {/* Main grid */}
      <div className="grid lg:grid-cols-[300px_1fr] gap-5 items-start">

        {/* ── Sidebar timeline ── */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          {STEPS.map((s) => {
            const SIcon = s.icon
            const isActive = s.id === selected
            return (
              <button key={s.id} onClick={() => setSelected(s.id)}
                className={`w-full flex items-center gap-3 px-5 py-4 text-left transition-all border-b border-slate-100 last:border-0 relative
                  ${isActive ? 'bg-medical-600' : 'hover:bg-slate-50'}`}>
                {/* Left accent bar */}
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
            {/* Top accent stripe */}
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
                  {STEPS.map(s => (
                    <div key={s.id}
                      className={`w-1.5 h-1.5 rounded-full transition-colors ${s.id === selected ? 'bg-medical-600' : 'bg-slate-200'}`}
                    />
                  ))}
                </div>

                <button
                  onClick={() => setSelected(s => Math.min(STEPS.length, s + 1))}
                  disabled={selected === STEPS.length}
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
