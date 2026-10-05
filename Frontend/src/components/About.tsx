import React from "react";
import { motion } from "framer-motion";
import { Flame, Brain, Clock, ArrowUpRight, Target, CheckCircle2 } from "lucide-react";
import { CinematicVideo } from "./CinematicVideo";

export const About: React.FC = () => {
  const ABOUT_VIDEO_URL =
    "https://videotourl.com/videos/1789409924747-67b073f2-1c31-4786-a3b8-5e47d8a6f793.mp4";

  const features = [
    {
      id: "streak-feat",
      title: "The Streak & Momentum Engine",
      tag: "HABIT INTELLIGENCE",
      icon: Flame,
      description:
        "Consistency is the single biggest predictor of GPA. Gradify gamifies your daily academic output with streak recovery, exam-week pacing, and anti-burnout metrics.",
      metric: "94.2% streak retention",
      highlight: "47 Days Unbroken",
    },
    {
      id: "syllabus",
      title: "Syllabus-to-Task Decomposition",
      tag: "AUTONOMOUS PARSER",
      icon: Brain,
      description:
        "Upload convoluted syllabi, lecture slides, and assignment rubrics. Our system reconstructs an actionable master calendar with micro-milestones.",
      metric: "Zero missed deadlines",
      highlight: "Auto-calibrated",
    },
    {
      id: "focus-lab",
      title: "The Deep Work Sanctuary",
      tag: "COGNITIVE FLOW",
      icon: Clock,
      description:
        "An austere, distraction-free cockpit. Synced pomodoro telemetry, soundscapes calibrated for memory retention, and session task gating.",
      metric: "2.4x deeper retention",
      highlight: "Binaural & Scrims",
    },
    {
      id: "mastery",
      title: "Mastery & Grade Forecasting",
      tag: "PREDICTIVE METRICS",
      icon: Target,
      description:
        "Know your standing before midterm week arrives. Real-time sensitivity analysis highlights which assignment requires your urgent focus.",
      metric: "±0.12 GPA accuracy",
      highlight: "Real-time Projections",
    },
  ];

  return (
    <div id="about" className="relative z-10">
      {/* 
        About Cinematic Video Section 
        Matches the exact size and inset frame of the landing page Hero section (min-h-screen, p-4 md:p-6),
        with the second video as full background covering "Where discipline meets..." down to "...build momentum".
      */}
      <section className="min-h-screen w-full p-4 md:p-6 box-border relative z-10 flex flex-col">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-50px" }}
          transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
          className="relative min-h-[calc(100vh-2rem)] md:min-h-[calc(100vh-3rem)] w-full rounded-2xl md:rounded-[2rem] overflow-hidden bg-black border border-white/[0.08] shadow-2xl flex flex-col justify-between p-6 sm:p-10 md:p-12 lg:p-16"
        >
          {/* Second Background Video covering entire card */}
          <CinematicVideo
            src={ABOUT_VIDEO_URL}
            className="absolute inset-0 w-full h-full object-cover"
          />

          {/* Noise overlay matching hero */}
          <div className="noise-overlay absolute inset-0 opacity-[0.7] mix-blend-overlay pointer-events-none" />

          {/* Cinematic gradient overlay ensuring text above video is crisp & legible */}
          <div className="absolute inset-0 bg-gradient-to-b from-black/80 via-black/55 to-black/90 pointer-events-none" />

          {/* Top / Main Narrative Block (All text appearing above video) */}
          <div className="relative z-10 max-w-5xl">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-primary/20 bg-black/60 backdrop-blur-md text-primary text-xs tracking-widest uppercase mb-6 sm:mb-8">
              <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
              The Academic Operating System
            </div>

            <h2
              className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-normal tracking-tight leading-[1.1] mb-6 drop-shadow-lg"
              style={{ color: "#E1E0CC" }}
            >
              Where discipline meets{" "}
              <span className="font-serif italic font-normal text-primary">
                effortless intelligence
              </span>
              . Engineered for students who demand{" "}
              <span className="font-serif italic font-normal text-primary">
                mastery
              </span>{" "}
              over collegiate chaos.
            </h2>

            <p className="text-primary/80 text-base sm:text-lg md:text-xl font-light leading-relaxed max-w-3xl drop-shadow">
              College shouldn&apos;t feel like a perpetual state of emergency. Gradify consolidates scattered course portals, disjointed flashcards, and unread reading lists into a single, cinematic command center. Built for relentless focus.
            </p>
          </div>

          {/* Bottom Momentum & Streak Banner (Above video) */}
          <div id="streak" className="relative z-10 pt-10 sm:pt-14 scroll-mt-24">
            <div className="bg-black/60 backdrop-blur-md border border-primary/25 rounded-xl md:rounded-2xl p-5 sm:p-7 flex flex-col md:flex-row items-start md:items-center justify-between gap-6 shadow-2xl">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-black/70 border border-primary/30 flex items-center justify-center text-primary shadow-lg flex-shrink-0">
                  <Flame className="w-6 h-6 animate-pulse" />
                </div>
                <div>
                  <div className="text-xs uppercase tracking-wider text-primary/70 font-medium font-mono">
                    Core Mechanism // Daily Streak & Focus
                  </div>
                  <div
                    className="text-lg sm:text-xl md:text-2xl font-medium"
                    style={{ color: "#E1E0CC" }}
                  >
                    Build momentum that makes studying second nature.
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2.5 bg-black/80 border border-white/10 px-4 py-2 rounded-xl">
                  <div className="flex -space-x-1.5">
                    {[...Array(5)].map((_, i) => (
                      <span
                        key={i}
                        className="w-2.5 h-2.5 rounded-full bg-primary inline-block shadow-[0_0_8px_rgba(222,219,200,0.6)]"
                      />
                    ))}
                  </div>
                  <span className="text-xs sm:text-sm font-semibold text-primary whitespace-nowrap">
                    Streak Protection Active
                  </span>
                </div>
                <span className="hidden sm:inline-block text-xs text-primary/80 font-mono bg-black/80 px-3.5 py-2 rounded-xl border border-white/10 whitespace-nowrap">
                  47 Days Continuous
                </span>
              </div>
            </div>
          </div>
        </motion.div>
      </section>

      {/* Feature Cards Section (#212121 with .bg-noise) */}
      <section className="relative z-10 py-12 md:py-20 px-4 md:px-6 max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 sm:gap-6">
          {features.map((feature, idx) => {
            const IconComp = feature.icon;
            return (
              <motion.div
                key={feature.id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{
                  duration: 0.6,
                  delay: idx * 0.1,
                  ease: [0.16, 1, 0.3, 1],
                }}
                className="group relative bg-[#212121] rounded-xl sm:rounded-2xl p-6 sm:p-8 border border-white/[0.06] hover:border-primary/40 transition-all duration-300 overflow-hidden"
              >
                {/* Subtle background noise */}
                <div className="bg-noise absolute inset-0 opacity-[0.35] mix-blend-overlay pointer-events-none" />

                {/* Top row */}
                <div className="relative z-10 flex items-center justify-between mb-5">
                  <div className="w-10 h-10 rounded-lg bg-black/40 border border-white/10 flex items-center justify-center text-primary group-hover:border-primary/40 transition-colors">
                    <IconComp className="w-5 h-5" />
                  </div>
                  <span className="text-[11px] font-mono tracking-widest text-primary/50 uppercase">
                    {feature.tag}
                  </span>
                </div>

                {/* Title & Description */}
                <h3
                  className="relative z-10 text-lg sm:text-xl font-medium mb-2.5 transition-colors group-hover:text-primary"
                  style={{ color: "#E1E0CC" }}
                >
                  {feature.title}
                </h3>

                <p className="relative z-10 text-gray-400 text-xs sm:text-sm leading-relaxed mb-6 font-light">
                  {feature.description}
                </p>

                {/* Card Footer Metric */}
                <div className="relative z-10 pt-4 border-t border-white/[0.06] flex items-center justify-between text-xs">
                  <span className="text-gray-500 font-mono flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-primary/70" />
                    {feature.metric}
                  </span>
                  <span className="text-primary/90 font-medium group-hover:translate-x-0.5 transition-transform flex items-center gap-1">
                    {feature.highlight}
                    <ArrowUpRight className="w-3.5 h-3.5 opacity-60" />
                  </span>
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Editorial Philosophy Quote */}
        <div className="mt-14 sm:mt-18 pt-10 border-t border-white/[0.08] flex flex-col md:flex-row items-baseline justify-between gap-6">
          <div className="text-xl sm:text-2xl font-serif italic text-primary/90 max-w-xl">
            &ldquo;The quiet mind studies once; the scattered mind studies five times and retains none.&rdquo;
          </div>
          <div className="text-xs tracking-wider text-gray-500 uppercase font-mono">
            Engineered in the Gradify Collective
          </div>
        </div>
      </section>
    </div>
  );
};
