import { Square } from "lucide-react";

const LINKS = ["Product", "How it works", "Capabilities", "About", "Privacy", "Contact"];

export default function Footer() {
  return (
    <footer className="bg-navy-dark border-t border-white/10 py-14">
      <div className="max-w-content mx-auto px-6 lg:px-10">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-8">
          <div className="flex items-center gap-3">
            <span className="w-9 h-9 rounded-md bg-gold flex items-center justify-center">
              <Square className="w-4 h-4 text-navy" strokeWidth={2.5} />
            </span>
            <div className="leading-none">
              <div className="font-display font-semibold text-cream text-lg">SahiPack</div>
              <div className="font-mono text-[10px] tracking-[0.16em] uppercase text-muted mt-1">
                Legal Metrology Intelligence
              </div>
            </div>
          </div>

          <nav className="flex flex-wrap gap-x-7 gap-y-3">
            {LINKS.map((link) => (
              <a
                key={link}
                href="#"
                className="text-sm text-cream/60 hover:text-gold transition-colors"
              >
                {link}
              </a>
            ))}
          </nav>
        </div>

        <div className="mt-10 pt-8 border-t border-white/10 font-mono text-xs text-cream/35">
          SahiPack — AI-assisted compliance inspection
        </div>
      </div>
    </footer>
  );
}
