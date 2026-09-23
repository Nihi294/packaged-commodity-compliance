import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Camera, CircleCheck, TriangleAlert, CircleX, Square } from "lucide-react";

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

export default function Inspection() {
  const navigate = useNavigate();
  const [scanned, setScanned] = useState(false);
  const [scanning, setScanning] = useState(false);

  const runScan = () => {
    setScanning(true);
    setScanned(false);
    setTimeout(() => {
      setScanning(false);
      setScanned(true);
    }, 1400);
  };

  return (
    <div className="min-h-screen bg-cream">
      <header className="sticky top-0 z-40 bg-navy border-b border-white/10">
        <div className="max-w-content mx-auto px-6 lg:px-10 h-20 flex items-center justify-between">
          <button
            onClick={() => navigate("/")}
            className="flex items-center gap-2 text-cream/70 hover:text-gold transition-colors text-sm"
          >
            <ArrowLeft className="w-4 h-4" /> Back to site
          </button>
          <div className="flex items-center gap-3">
            <span className="w-8 h-8 rounded-md bg-gold flex items-center justify-center">
              <Square className="w-3.5 h-3.5 text-navy" strokeWidth={2.5} />
            </span>
            <span className="font-display font-semibold text-cream">SahiPack</span>
          </div>
        </div>
      </header>

      <main className="max-w-content mx-auto px-6 lg:px-10 py-14 lg:py-20">
        <div className="eyebrow text-teal-dark mb-4">
          <span className="w-1.5 h-1.5 rounded-full bg-teal" />
          New inspection
        </div>
        <h1 className="font-display font-semibold text-[32px] sm:text-[40px] text-ink leading-tight max-w-xl">
          Upload a product photo to begin.
        </h1>
        <p className="mt-4 text-ink/65 max-w-[56ch]">
          This is a frontend prototype. Uploads are simulated with sample data
          — no image is processed or stored.
        </p>

        <div className="mt-12 grid lg:grid-cols-[1fr_1.1fr] gap-8">
          {/* Upload card */}
          <div className="rounded-xl border border-ink/15 bg-white p-8 flex flex-col items-center justify-center text-center min-h-[360px]">
            <div className="w-16 h-16 rounded-full border border-dashed border-ink/25 flex items-center justify-center mb-5">
              <Camera className="w-6 h-6 text-ink/40" />
            </div>
            <p className="text-ink/70 max-w-[32ch]">
              Drag a package photo here, or use the sample image to preview a
              finding.
            </p>
            <button
              onClick={runScan}
              disabled={scanning}
              className="mt-7 font-mono text-xs tracking-wide uppercase bg-navy text-cream px-6 py-3.5 rounded-md hover:bg-navy-light transition-colors disabled:opacity-60"
            >
              {scanning ? "Analyzing sample…" : scanned ? "Re-run sample scan" : "Use sample image"}
            </button>
            <div className="mt-5 font-mono text-[11px] text-ink/35">
              frame_0184.jpg &middot; SC-2291
            </div>
          </div>

          {/* Result card */}
          <div className="rounded-xl border border-ink/15 bg-white p-8">
            {!scanned && !scanning && (
              <div className="h-full flex flex-col items-center justify-center text-center text-ink/40 min-h-[280px]">
                <p className="max-w-[30ch]">
                  Inspection results will appear here once a scan runs.
                </p>
              </div>
            )}

            {scanning && (
              <div className="h-full flex flex-col items-center justify-center text-center min-h-[280px]">
                <div className="w-10 h-10 rounded-full border-2 border-teal/30 border-t-teal animate-spin motion-reduce:animate-none" />
                <p className="mt-5 font-mono text-xs tracking-wide uppercase text-ink/50">
                  Running AI analysis…
                </p>
              </div>
            )}

            {scanned && !scanning && (
              <div>
                <div className="flex items-start justify-between">
                  <div>
                    <div className="font-mono text-xs text-ink/40">INSPECTION ID</div>
                    <div className="font-display font-semibold text-ink text-lg">SC-2291</div>
                  </div>
                  <span className="inline-flex items-center gap-1.5 font-mono text-[11px] tracking-wide uppercase bg-gold/20 text-gold-dark px-3 py-1.5 rounded-full">
                    <TriangleAlert className="w-3.5 h-3.5" /> Needs review
                  </span>
                </div>
                <div className="mt-2 text-sm text-ink/60">Rajdhani Mustard Oil, 1L</div>

                <ul className="mt-6 divide-y divide-ink/10 border border-ink/10 rounded-lg overflow-hidden">
                  {DECLARATIONS.map((d) => (
                    <li key={d.label} className="flex items-center justify-between px-4 py-3">
                      <span className="flex items-center gap-2.5 text-sm text-ink/80">
                        <StatusIcon status={d.status} />
                        {d.label}
                      </span>
                      <span className="font-mono text-[10px] tracking-wide uppercase text-ink/40">
                        {d.status === "found" ? "FOUND" : d.status === "review" ? "NEEDS REVIEW" : "MISSING"}
                      </span>
                    </li>
                  ))}
                </ul>

                <div className="mt-6 flex flex-col sm:flex-row gap-3">
                  <button className="font-mono text-xs tracking-wide uppercase border border-ink/20 text-ink px-5 py-3 rounded-md hover:border-teal hover:text-teal-dark transition-colors">
                    Verify finding
                  </button>
                  <button className="font-mono text-xs tracking-wide uppercase bg-navy text-cream px-5 py-3 rounded-md hover:bg-navy-light transition-colors">
                    Generate report →
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
