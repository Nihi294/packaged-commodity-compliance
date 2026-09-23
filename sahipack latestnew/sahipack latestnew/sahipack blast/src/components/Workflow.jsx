import { Camera, ScanText, ShieldCheck, Eye, FileText } from "lucide-react";

const STEPS = [
  {
    n: "01",
    title: "Capture",
    desc: "Upload or capture the product label.",
    icon: Camera,
  },
  {
    n: "02",
    title: "Read",
    desc: "OCR and computer vision extract declarations from the packaging.",
    icon: ScanText,
  },
  {
    n: "03",
    title: "Check",
    desc: "A rule engine validates extracted information against configured Legal Metrology requirements.",
    icon: ShieldCheck,
  },
  {
    n: "04",
    title: "Review",
    desc: "Potential violations are linked to visual evidence for officer verification.",
    icon: Eye,
  },
  {
    n: "05",
    title: "Report",
    desc: "Generate a structured inspection and compliance report.",
    icon: FileText,
  },
];

export default function Workflow() {
  return (
    <section id="workflow" className="bg-cream py-24 lg:py-32">
      <div className="max-w-content mx-auto px-6 lg:px-10">
        <div className="eyebrow text-teal-dark mb-6">
          <span className="w-1.5 h-1.5 rounded-full bg-teal" />
          The operating principle
        </div>
        <h2 className="font-display font-semibold text-[32px] sm:text-[42px] lg:text-[48px] text-ink max-w-2xl leading-tight">
          From package photo to defensible finding.
        </h2>
        <p className="mt-6 text-ink/70 text-lg max-w-[58ch] leading-relaxed">
          AI assists the inspection. Rules structure the decision. Evidence
          keeps the finding reviewable.
        </p>

        <div className="mt-16 relative">
          {/* connecting line desktop */}
          <div
            className="hidden lg:block absolute top-[26px] left-[10%] right-[10%] h-px bg-ink/15"
            aria-hidden="true"
          />
          <div className="grid lg:grid-cols-5 gap-10 lg:gap-6">
            {STEPS.map((s, i) => (
              <div key={s.n} className="relative">
                <div className="hidden lg:flex w-[52px] h-[52px] rounded-full bg-cream border border-ink/15 items-center justify-center relative z-10">
                  <s.icon className="w-5 h-5 text-teal-dark" />
                </div>
                <div className="lg:hidden flex items-center gap-4 mb-3">
                  <div className="w-[44px] h-[44px] rounded-full bg-cream border border-ink/15 flex items-center justify-center shrink-0">
                    <s.icon className="w-4.5 h-4.5 text-teal-dark" />
                  </div>
                  <span className="font-mono text-xs text-ink/40">STEP {s.n}</span>
                </div>

                <div className="mt-5 lg:mt-6">
                  <div className="hidden lg:block font-mono text-xs text-ink/40 mb-2">
                    STEP {s.n}
                  </div>
                  <h3 className="font-display font-semibold text-lg text-ink">
                    {s.title}
                  </h3>
                  <p className="mt-2 text-sm text-ink/65 leading-relaxed max-w-[26ch]">
                    {s.desc}
                  </p>
                </div>

                {i < STEPS.length - 1 && (
                  <div className="lg:hidden w-px h-8 bg-ink/15 ml-[22px] mt-6" aria-hidden="true" />
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
