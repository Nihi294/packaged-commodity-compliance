import { CircleCheck, TriangleAlert, CircleX, Link2, ScrollText } from "lucide-react";

const DECLARATIONS = [
  { label: "Manufacturer details", status: "found" },
  { label: "Net quantity", status: "found" },
  { label: "MRP", status: "found" },
  { label: "Packing date", status: "review" },
  { label: "Consumer care", status: "missing" },
];

function StatusIcon({ status }) {
  if (status === "found") return <CircleCheck className="w-4 h-4 text-teal-dark shrink-0" />;
  if (status === "review") return <TriangleAlert className="w-4 h-4 text-gold-dark shrink-0" />;
  return <CircleX className="w-4 h-4 text-red-500/80 shrink-0" />;
}

function statusWord(status) {
  if (status === "found") return "FOUND";
  if (status === "review") return "NEEDS REVIEW";
  return "MISSING";
}

function PackageWithEvidence() {
  return (
    <div className="relative w-full max-w-[280px] mx-auto">
      <svg viewBox="0 0 240 340" className="w-full h-full">
        <defs>
          <linearGradient id="oilGrad2" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#F6C84A" />
            <stop offset="100%" stopColor="#DDAE2E" />
          </linearGradient>
        </defs>
        <rect x="94" y="14" width="52" height="24" rx="3" fill="#3D6F6B" />
        <path d="M106 38 L134 38 L138 66 L102 66 Z" fill="url(#oilGrad2)" />
        <path
          d="M84 66 H156 C163 66 168 71 168 78 V294 C168 304 160 312 150 312 H90 C80 312 72 304 72 294 V78 C72 71 77 66 84 66 Z"
          fill="url(#oilGrad2)"
        />
        <rect x="80" y="118" width="80" height="120" rx="3" fill="#10223B" />
        <text x="120" y="140" textAnchor="middle" fontFamily="Space Grotesk, sans-serif" fontSize="10.5" fontWeight="700" fill="#F6C84A">
          SAHIPACK
        </text>
        <text x="120" y="164" textAnchor="middle" fontFamily="Space Grotesk, sans-serif" fontSize="11" fontWeight="600" fill="#F5F1E7">
          MUSTARD OIL
        </text>
        <text x="120" y="182" textAnchor="middle" fontFamily="IBM Plex Mono, monospace" fontSize="8.5" fill="#8D9BAA">
          1 L
        </text>
        <line x1="90" y1="196" x2="150" y2="196" stroke="#4F8C87" strokeWidth="1" opacity="0.5" />
        <text x="120" y="214" textAnchor="middle" fontFamily="IBM Plex Mono, monospace" fontSize="7.5" fill="#8D9BAA">
          MRP ₹120 · NET QTY 1L
        </text>
      </svg>

      {/* highlighted evidence region - consumer care missing area near bottom of label */}
      <div className="absolute left-[33%] bottom-[19%] w-[34%] h-[9%] border-2 border-gold rounded-sm animate-pulse motion-reduce:animate-none">
        <span className="absolute -top-6 left-1/2 -translate-x-1/2 whitespace-nowrap font-mono text-[9px] tracking-wide uppercase bg-gold text-navy px-2 py-1 rounded">
          Evidence region
        </span>
      </div>
    </div>
  );
}

export default function InspectionPreview() {
  return (
    <section className="bg-cream py-24 lg:py-32">
      <div className="max-w-content mx-auto px-6 lg:px-10">
        <div className="eyebrow text-teal-dark mb-6">
          <span className="w-1.5 h-1.5 rounded-full bg-teal" />
          Inspection preview
        </div>
        <h2 className="font-display font-semibold text-[32px] sm:text-[42px] lg:text-[48px] text-ink max-w-xl leading-tight">
          See what an officer sees.
        </h2>

        <div className="mt-16 rounded-xl border border-ink/15 bg-white shadow-[0_20px_60px_-24px_rgba(20,41,67,0.25)] overflow-hidden">
          <div className="flex items-center justify-between px-6 py-4 border-b border-ink/10 bg-cream-dim/60">
            <div className="flex items-center gap-2 font-mono text-xs text-ink/50">
              <span className="w-2 h-2 rounded-full bg-teal animate-blink motion-reduce:animate-none" />
              INSPECTION SC-2291 · LIVE
            </div>
            <div className="font-mono text-xs text-ink/40 hidden sm:block">
              SahiPack Console
            </div>
          </div>

          <div className="grid lg:grid-cols-[1fr_1.1fr]">
            {/* Left: image */}
            <div className="p-8 lg:p-12 bg-navy/[0.03] flex items-center justify-center border-b lg:border-b-0 lg:border-r border-ink/10">
              <PackageWithEvidence />
            </div>

            {/* Right: results */}
            <div className="p-8 lg:p-10">
              <div className="flex items-start justify-between">
                <div>
                  <div className="font-mono text-xs text-ink/40">INSPECTION ID</div>
                  <div className="font-display font-semibold text-ink text-lg">SC-2291</div>
                </div>
                <span className="inline-flex items-center gap-1.5 font-mono text-[11px] tracking-wide uppercase bg-gold/20 text-gold-dark px-3 py-1.5 rounded-full">
                  <TriangleAlert className="w-3.5 h-3.5" /> Needs review
                </span>
              </div>

              <div className="mt-2 text-sm text-ink/60">
                Rajdhani Mustard Oil, 1L
              </div>

              <div className="mt-7 font-mono text-xs tracking-[0.14em] uppercase text-ink/40">
                Declarations
              </div>
              <ul className="mt-3 divide-y divide-ink/10 border border-ink/10 rounded-lg overflow-hidden">
                {DECLARATIONS.map((d) => (
                  <li key={d.label} className="flex items-center justify-between px-4 py-3 bg-white">
                    <span className="flex items-center gap-2.5 text-sm text-ink/80">
                      <StatusIcon status={d.status} />
                      {d.label}
                    </span>
                    <span
                      className={`font-mono text-[10px] tracking-wide uppercase ${
                        d.status === "found"
                          ? "text-teal-dark"
                          : d.status === "review"
                          ? "text-gold-dark"
                          : "text-red-500/80"
                      }`}
                    >
                      {statusWord(d.status)}
                    </span>
                  </li>
                ))}
              </ul>

              <div className="mt-6 rounded-lg border border-red-200 bg-red-50/60 p-4">
                <div className="font-mono text-[11px] tracking-[0.12em] uppercase text-red-600/80">
                  Violation
                </div>
                <p className="mt-1.5 text-sm text-ink/80">
                  Consumer care declaration not detected.
                </p>

                <div className="mt-4 flex flex-col gap-2 text-xs">
                  <div className="flex items-center gap-2 text-ink/60">
                    <Link2 className="w-3.5 h-3.5" />
                    <span className="font-mono">EVIDENCE LINKED — frame_0184.jpg</span>
                  </div>
                  <div className="flex items-center gap-2 text-ink/60">
                    <ScrollText className="w-3.5 h-3.5" />
                    <span>
                      Applicable requirement: Legal Metrology packaged
                      commodity requirement
                    </span>
                  </div>
                </div>
              </div>

              <div className="mt-7 flex flex-col sm:flex-row gap-3">
                <button className="font-mono text-xs tracking-wide uppercase border border-ink/20 text-ink px-5 py-3 rounded-md hover:border-teal hover:text-teal-dark transition-colors">
                  Verify finding
                </button>
                <button className="font-mono text-xs tracking-wide uppercase bg-navy text-cream px-5 py-3 rounded-md hover:bg-navy-light transition-colors">
                  Generate report →
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
