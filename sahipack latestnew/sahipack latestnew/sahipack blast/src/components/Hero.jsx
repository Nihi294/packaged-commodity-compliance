import { ShieldCheck, ArrowRight, CircleCheck, TriangleAlert } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function Hero() {
  const navigate = useNavigate();

  return (
    <section
      id="product"
      className="relative bg-navy-dark overflow-hidden pt-32 pb-28 lg:pt-40 lg:pb-36 min-h-screen flex items-center"
    >
      {/* background texture */}
      <div className="absolute inset-0 grid-overlay-navy opacity-40" aria-hidden="true" />
      <div
        className="absolute top-1/2 right-[-10%] -translate-y-1/2 w-[700px] h-[700px] rounded-full bg-gold/10 blur-[140px]"
        aria-hidden="true"
      />
      <span
        className="hidden lg:block absolute top-24 right-10 font-display font-bold text-[220px] leading-none text-white/[0.03] select-none whitespace-nowrap"
        aria-hidden="true"
      >
        
      </span>

      <div className="relative max-w-content mx-auto px-6 lg:px-10 w-full">
        <div className="max-w-3xl">
          {/* stat pill */}
          <div className="inline-flex items-center gap-2 bg-cream text-ink rounded-full pl-1.5 pr-4 py-1.5 mb-8">
            <span className="w-6 h-6 rounded-full bg-teal flex items-center justify-center">
              <ShieldCheck className="w-3.5 h-3.5 text-white" />
            </span>
            <span className="text-sm font-medium">12,480+ Labels Verified</span>
          </div>

          {/* headline */}
          <h1 className="font-display font-bold text-cream text-[46px] leading-[1.05] sm:text-[64px] lg:text-[84px] tracking-tight">
            SEE THE PACK.
            <br />
            <span className="text-gold">KNOW THE FINDING.</span>
          </h1>

          <p className="mt-7 text-cream/60 text-lg sm:text-xl leading-relaxed max-w-[52ch]">
            Scan packages with AI, check them against Legal Metrology rules, and get evidence-backed results in seconds..
          </p>

          {/* buttons */}
          <div className="mt-10 flex flex-col sm:flex-row gap-4">
            <button
              onClick={() => navigate("/inspection")}
              className="inline-flex items-center justify-center gap-2 bg-cream text-ink px-7 py-4 rounded-full font-semibold hover:bg-white transition-colors"
            >
              Start a Free Inspection
            </button>
            <button
              onClick={() =>
                document.getElementById("workflow")?.scrollIntoView({ behavior: "smooth" })
              }
              className="inline-flex items-center justify-center gap-2 bg-gold text-navy px-7 py-4 rounded-full font-semibold hover:bg-gold-dark transition-colors"
            >
              Explore the Platform <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* floating console cards */}
        <div className="hidden lg:block absolute top-16 right-6 xl:right-14 w-[420px]" aria-hidden="true">
          <div className="relative">
            {/* back card: declarations panel, rotated */}
            <div className="rotate-[4deg] bg-navy-light border border-white/10 rounded-2xl shadow-2xl p-6 w-[380px]">
              <div className="flex items-center justify-between mb-5">
                <span className="font-mono text-[10px] tracking-[0.14em] uppercase text-cream/40">
                  Inspection SC-2291
                </span>
                <span className="w-2 h-2 rounded-full bg-teal animate-blink motion-reduce:animate-none" />
              </div>
              {[
                { label: "Manufacturer details", ok: true },
                { label: "Net quantity", ok: true },
                { label: "MRP", ok: true },
                { label: "Consumer care", ok: false },
              ].map((row) => (
                <div
                  key={row.label}
                  className="flex items-center justify-between py-2.5 border-b border-white/5 last:border-0"
                >
                  <span className="flex items-center gap-2 text-sm text-cream/80">
                    {row.ok ? (
                      <CircleCheck className="w-4 h-4 text-teal" />
                    ) : (
                      <TriangleAlert className="w-4 h-4 text-gold" />
                    )}
                    {row.label}
                  </span>
                  <span className="font-mono text-[10px] uppercase text-cream/30">
                    {row.ok ? "Found" : "Review"}
                  </span>
                </div>
              ))}
            </div>

            {/* front card: score, rotated other way, overlapping */}
            <div className="absolute -bottom-10 -left-10 -rotate-[6deg] bg-cream rounded-2xl shadow-2xl p-6 w-[220px]">
              <div className="font-mono text-[10px] tracking-[0.14em] uppercase text-ink/40">
                Compliance score
              </div>
              <div className="font-display font-bold text-4xl text-ink mt-1">82%</div>
              <div className="mt-3 h-2 w-full bg-ink/10 rounded-full overflow-hidden">
                <div className="h-full w-[82%] bg-teal rounded-full" />
              </div>
              <div className="mt-3 font-mono text-[10px] uppercase text-gold-dark">
                1 flag needs review
              </div>
            </div>

            {/* small floating badge icon */}
            <div className="absolute -top-8 -left-6 w-16 h-16 rounded-2xl bg-gold flex items-center justify-center rotate-[-8deg] shadow-xl">
              <ShieldCheck className="w-7 h-7 text-navy" />
            </div>
          </div>

          {/* identity chip */}
          <div className="absolute -bottom-16 right-0 bg-navy-light border border-white/10 rounded-full pl-2 pr-4 py-2 flex items-center gap-3 shadow-xl">
            <span className="w-8 h-8 rounded-full bg-teal flex items-center justify-center text-xs font-semibold text-white">
              PS
            </span>
            <div className="leading-tight">
              <div className="text-cream text-xs font-medium">Priya Sharma</div>
              <div className="font-mono text-[9px] uppercase text-cream/40">
                Verified officer
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
