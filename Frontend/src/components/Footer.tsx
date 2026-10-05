import React from "react";
import { ArrowUp } from "lucide-react";

export const Footer: React.FC = () => {
  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <footer id="contact" className="relative z-10 border-t border-white/[0.08] bg-black/90 backdrop-blur-lg py-12 px-6">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex flex-col items-center md:items-start gap-2">
          <div className="text-xl font-bold tracking-tight text-primary flex items-center gap-2">
            <span>Gradify</span>
            <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded-full bg-white/5 border border-white/10 text-primary/70">
              v1.0 Lab
            </span>
          </div>
          <p className="text-gray-500 text-xs sm:text-sm font-light">
            Turn Your College Chaos Into Smarter Academic Workflow.
          </p>
        </div>

        <div className="flex items-center gap-6 text-xs text-primary/70">
          <a
            href="#streak"
            className="hover:text-primary transition-colors"
          >
            Streak Engine
          </a>
          <a
            href="#about"
            className="hover:text-primary transition-colors"
          >
            Philosophy
          </a>
          <a
            href="#auth-section"
            className="hover:text-primary transition-colors"
          >
            Cockpit Access
          </a>
        </div>

        <div className="flex items-center gap-4">
          <span className="text-[11px] font-mono text-gray-500">
            © {new Date().getFullYear()} Gradify Systems Inc.
          </span>
          <button
            onClick={scrollToTop}
            aria-label="Back to top"
            className="w-9 h-9 rounded-full bg-[#181818] border border-white/10 flex items-center justify-center text-primary/80 hover:text-primary hover:border-primary/40 transition-colors cursor-pointer"
          >
            <ArrowUp className="w-4 h-4" />
          </button>
        </div>
      </div>
    </footer>
  );
};
