import { useNavigate } from "react-router-dom";

export default function CTA() {
  const navigate = useNavigate();

  return (
    <section className="relative bg-navy-dark py-24 lg:py-32 overflow-hidden">
      <div className="absolute inset-0 grid-overlay-navy opacity-60" aria-hidden="true" />
      <div className="relative max-w-content mx-auto px-6 lg:px-10 text-center">
        <h2 className="font-display font-semibold text-[36px] sm:text-[48px] lg:text-[56px] leading-tight">
          <span className="text-cream block">Inspect faster.</span>
          <span className="text-gold block">Decide with evidence.</span>
        </h2>
        <p className="mt-6 text-cream/65 text-lg max-w-[52ch] mx-auto leading-relaxed">
          Turn every product scan into a structured, reviewable compliance
          record.
        </p>

        <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={() => navigate("/inspection")}
            className="font-mono text-sm tracking-wide uppercase bg-gold text-navy px-7 py-4 rounded-md font-medium hover:bg-gold-dark transition-colors"
          >
            Start an inspection →
          </button>
          <button
            onClick={() =>
              document.getElementById("workflow")?.scrollIntoView({ behavior: "smooth" })
            }
            className="font-mono text-sm tracking-wide uppercase border border-white/20 text-cream px-7 py-4 rounded-md hover:border-gold hover:text-gold transition-colors"
          >
            Explore the workflow
          </button>
        </div>

        <p className="mt-8 font-mono text-[11px] tracking-wide uppercase text-cream/35">
          AI-assisted findings are subject to officer verification.
        </p>
      </div>
    </section>
  );
}
