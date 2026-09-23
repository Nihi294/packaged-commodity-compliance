import {
  ScanSearch,
  GitBranch,
  ImageIcon,
  Type,
  LineChart,
  FileOutput,
} from "lucide-react";

const CAPABILITIES = [
  {
    n: "01",
    title: "Declaration extraction",
    desc: "Detect MRP, net quantity, manufacturer details, dates and consumer-care information.",
    icon: ScanSearch,
  },
  {
    n: "02",
    title: "Rule-driven validation",
    desc: "Apply configurable compliance rules instead of relying on an LLM to make legal decisions.",
    icon: GitBranch,
  },
  {
    n: "03",
    title: "Visual evidence",
    desc: "Keep every finding connected to the product image and detected region.",
    icon: ImageIcon,
  },
  {
    n: "04",
    title: "Readability checks",
    desc: "Surface potential readability and formatting issues for officer review.",
    icon: Type,
  },
  {
    n: "05",
    title: "Inspection intelligence",
    desc: "Track inspections, violations, pending reviews and compliance trends.",
    icon: LineChart,
  },
  {
    n: "06",
    title: "Automated reports",
    desc: "Convert findings and supporting evidence into structured reports.",
    icon: FileOutput,
  },
];

export default function Capabilities() {
  return (
    <section id="capabilities" className="bg-navy py-24 lg:py-32 relative overflow-hidden">
      <div className="absolute inset-0 grid-overlay-navy opacity-70" aria-hidden="true" />
      <div className="relative max-w-content mx-auto px-6 lg:px-10">
        <div className="eyebrow text-gold mb-6">
          <span className="w-1.5 h-1.5 rounded-full bg-gold" />
          Built for evidence-led inspection
        </div>
        <h2 className="font-display font-semibold text-[32px] sm:text-[42px] lg:text-[48px] text-cream max-w-xl leading-tight">
          More than OCR.
        </h2>

        <div className="mt-16 grid sm:grid-cols-2 lg:grid-cols-3 gap-px bg-white/10 border border-white/10 rounded-lg overflow-hidden">
          {CAPABILITIES.map((c) => (
            <div
              key={c.n}
              className="bg-navy p-8 hover:bg-navy-light transition-colors duration-300"
            >
              <div className="flex items-center justify-between mb-6">
                <span className="w-11 h-11 rounded-md bg-white/5 border border-white/10 flex items-center justify-center">
                  <c.icon className="w-5 h-5 text-teal" />
                </span>
                <span className="font-mono text-xs text-cream/30">{c.n}</span>
              </div>
              <h3 className="font-display font-semibold text-cream text-lg">
                {c.title}
              </h3>
              <p className="mt-3 text-sm text-cream/60 leading-relaxed">
                {c.desc}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
