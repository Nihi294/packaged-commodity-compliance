import { Zap, ScanEye, UserCheck } from "lucide-react";

const PRINCIPLES = [
  {
    n: "01",
    title: "Assisted",
    desc: "AI accelerates inspection.",
    icon: Zap,
  },
  {
    n: "02",
    title: "Explainable",
    desc: "Findings remain connected to evidence.",
    icon: ScanEye,
  },
  {
    n: "03",
    title: "Human verified",
    desc: "Final decisions remain with authorized officers.",
    icon: UserCheck,
  },
];

export default function TrustSection() {
  return (
    <section id="trust" className="bg-navy py-24 lg:py-32">
      <div className="max-w-content mx-auto px-6 lg:px-10">
        <div className="grid lg:grid-cols-[1.1fr_1fr] gap-16 items-start">
          <div>
            <h2 className="font-display font-semibold text-[32px] sm:text-[42px] lg:text-[46px] text-cream leading-tight">
              AI can read the label.
              <br />
              <span className="text-gold">But the officer makes the call.</span>
            </h2>
            <p className="mt-6 text-cream/65 text-lg leading-relaxed max-w-[52ch]">
              SahiPack is designed as an inspection-assistance system. AI
              surfaces potential findings; officers review, verify and
              finalize them.
            </p>
          </div>

          <div className="flex flex-col gap-6">
            {PRINCIPLES.map((p) => (
              <div
                key={p.n}
                className="flex items-start gap-5 pb-6 border-b border-white/10 last:border-b-0 last:pb-0"
              >
                <span className="w-11 h-11 rounded-md bg-white/5 border border-white/10 flex items-center justify-center shrink-0">
                  <p.icon className="w-5 h-5 text-teal" />
                </span>
                <div>
                  <div className="font-mono text-xs text-cream/40 mb-1">{p.n}</div>
                  <h3 className="font-display font-semibold text-cream text-lg">
                    {p.title}
                  </h3>
                  <p className="mt-1 text-sm text-cream/60">{p.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
