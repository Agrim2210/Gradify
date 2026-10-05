import React from "react";
import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";
import { WordsPullUp } from "./WordsPullUp";
import { Navbar } from "./Navbar";
import { CinematicVideo } from "./CinematicVideo";

interface HeroProps {
  onJoinLabClick?: () => void;
  onSelectAuthTab?: (tab: "signup" | "signin") => void;
  onOpenContact?: () => void;
  onOpenWorkspace?: () => void;
}

export const Hero: React.FC<HeroProps> = ({
  onJoinLabClick,
  onSelectAuthTab,
  onOpenContact,
  onOpenWorkspace,
}) => {
  const VIDEO_URL =
    "https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260405_170732_8a9ccda6-5cff-4628-b164-059c500a2b41.mp4";

  const handleJoinClick = () => {
    if (onJoinLabClick) {
      onJoinLabClick();
    } else {
      const el = document.getElementById("auth-section");
      if (el) {
        el.scrollIntoView({ behavior: "smooth" });
      }
    }
  };

  return (
    <section className="h-screen w-full p-4 md:p-6 box-border relative z-10">
      {/* Inset Container */}
      <div className="relative h-full w-full rounded-2xl md:rounded-[2rem] overflow-hidden bg-black border border-white/[0.08] shadow-2xl">
        {/* Robust Background Video with Auto-retry */}
        <CinematicVideo
          src={VIDEO_URL}
          className="absolute inset-0 w-full h-full object-cover"
        />

        {/* Noise overlay */}
        <div className="noise-overlay absolute inset-0 opacity-[0.7] mix-blend-overlay pointer-events-none" />

        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-b from-black/30 via-transparent to-black/60 pointer-events-none" />

        {/* Navbar */}
        <Navbar
          onSelectAuthTab={onSelectAuthTab}
          onOpenContact={onOpenContact}
          onOpenWorkspace={onOpenWorkspace}
        />

        {/* Hero Content (Bottom Aligned) */}
        <div className="absolute bottom-0 left-0 right-0 p-5 sm:p-8 md:p-10 lg:p-12 z-20">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8 items-end">
            {/* Left 7-8 Columns: Heading (refined slightly smaller as requested) */}
            <div className="lg:col-span-7 xl:col-span-8 overflow-hidden select-none">
              <WordsPullUp
                text="Gradify"
                className="text-[17vw] sm:text-[15.5vw] md:text-[14vw] lg:text-[12.5vw] xl:text-[11.5vw] 2xl:text-[11vw] font-medium leading-[0.85] tracking-[-0.07em] select-none block"
              />
            </div>

            {/* Right 4-5 Columns: Bigger Description + CTA Button */}
            <div className="lg:col-span-5 xl:col-span-4 flex flex-col justify-end gap-5 sm:gap-6 pb-2 md:pb-4 lg:pb-6">
              {/* Description paragraph (made noticeably bigger as requested) */}
              <motion.p
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{
                  duration: 0.8,
                  delay: 0.5,
                  ease: [0.16, 1, 0.3, 1],
                }}
                className="text-primary/90 text-sm sm:text-base md:text-lg lg:text-xl xl:text-2xl leading-[1.3] max-w-xl font-normal tracking-tight"
              >
                Turn Your College Chaos Into Smarter Academic Workflow
              </motion.p>

              {/* CTA Button "Join the lab" */}
              <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{
                  duration: 0.8,
                  delay: 0.7,
                  ease: [0.16, 1, 0.3, 1],
                }}
              >
                <button
                  type="button"
                  onClick={handleJoinClick}
                  className="group inline-flex items-center gap-2 hover:gap-3 bg-primary text-black font-medium text-sm sm:text-base rounded-full pl-5 pr-1.5 py-1.5 transition-all duration-300 shadow-lg hover:shadow-primary/20 hover:brightness-105 active:scale-[0.98] cursor-pointer"
                >
                  <span>Join the lab</span>
                  <div className="bg-black rounded-full w-9 h-9 sm:w-10 sm:h-10 flex items-center justify-center transition-transform duration-300 group-hover:scale-110">
                    <ArrowRight className="w-4 h-4 sm:w-5 sm:h-5 text-primary" />
                  </div>
                </button>
              </motion.div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
