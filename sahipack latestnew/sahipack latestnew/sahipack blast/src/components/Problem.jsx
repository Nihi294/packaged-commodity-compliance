import { ArrowRight, FileSearch, Scale, ClipboardX, FileWarning, Camera, ScanEye, ShieldCheck, FileCheck2 } from "lucide-react";

const MANUAL_STEPS = [
  { n: "01", title: "Read package", icon: FileSearch },
  { n: "02", title: "Compare requirements", icon: Scale },
  { n: "03", title: "Record violation", icon: ClipboardX },
  { n: "04", title: "Prepare report", icon: FileWarning },
];

const SAHIPACK_STEPS = [
  { n: "01", title: "Capture", icon: Camera },
  { n: "02", title: "AI-assisted extraction", icon: ScanEye },
  { n: "03", title: "Rule validation", icon: ShieldCheck },
  { n: "04", title: "Evidence + report", icon: FileCheck2 },
];

export default function Problem() {
  return (
    <section className="relative bg-cream py-24 lg:py-32 overflow-hidden">
      <div className="absolute inset-0 grid-overlay-cream opacity-60" aria-hidden="true" />
      <div className="relative max-w-content mx-auto px-6 lg:px-10">
        <div className="eyebrow text-teal-dark mb-6">
          <span className="w-1.5 h-1.5 rounded-full bg-teal" />
          The problem
        </div>

        <h2 className="font-display font-semibold text-[32px] leading-tight sm:text-[42px] lg:text-[48px] max-w-2xl text-ink">
          Every package carries a promise. Inspecting every promise manually
         isn't possible.
        </h2>

        <p className="mt-6 text-ink/70 text-lg max-w-[62ch] leading-relaxed">
          Enforcement officers deal with a huge variety of packaged
          commodities. Checking declarations, readability and compliance
          manually is time-consuming, difficult to handle each report.
        </p>

        <div className="mt-16 grid lg:grid-cols-[1fr_auto_1fr] gap-8 lg:gap-6 items-stretch">
          {/* Manual */}
          <div className="border border-ink/15 rounded-lg p-8 bg-cream-dim/40">
            <div className="font-mono text-xs tracking-[0.14em] uppercase text-ink/50">
              Manual inspection
            </div>
            <ul className="mt-6 space-y-5">
              {MANUAL_STEPS.map((s) => (
                <li key={s.n} className="flex items-center gap-4">
                  <span className="font-mono text-xs text-ink/40 w-6">{s.n}</span>
                  <s.icon className="w-4 h-4 text-ink/40 shrink-0" />
                  <span className="text-ink/80">{s.title}</span>
                </li>
              ))}
            </ul>
            <div className="mt-8 pt-6 border-t border-ink/10 font-mono text-[11px] tracking-[0.12em] uppercase text-ink/40">
              Time &middot; Paperwork &middot; Inconsistency
            </div>
          </div>

          {/* Arrow */}
          <div className="hidden lg:flex items-center justify-center">
            <div className="w-12 h-12 rounded-full border border-ink/15 flex items-center justify-center bg-cream">
              <ArrowRight className="w-5 h-5 text-teal" />
            </div>
          </div>
          <div className="flex lg:hidden justify-center -my-2">
            <div className="w-10 h-10 rounded-full border border-ink/15 flex items-center justify-center bg-cream rotate-90">
              <ArrowRight className="w-4 h-4 text-teal" />
            </div>
          </div>

          {/* SahiPack */}
          <div className="border border-teal/30 rounded-lg p-8 bg-navy relative">
            <div className="font-mono text-xs tracking-[0.14em] uppercase text-gold">
              With SahiPack
            </div>
            <ul className="mt-6 space-y-5">
              {SAHIPACK_STEPS.map((s) => (
                <li key={s.n} className="flex items-center gap-4">
                  <span className="font-mono text-xs text-cream/40 w-6">{s.n}</span>
                  <s.icon className="w-4 h-4 text-teal shrink-0" />
                  <span className="text-cream/90">{s.title}</span>
                </li>
              ))}
            </ul>
            <div className="mt-8 pt-6 border-t border-white/10 font-mono text-[11px] tracking-[0.12em] uppercase text-teal">
              Faster &middot; Traceable &middot; Reviewable
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
