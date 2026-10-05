import React, { useState } from "react";
import { motion } from "framer-motion";

interface NavbarProps {
  onSelectAuthTab?: (tab: "signup" | "signin") => void;
  onOpenContact?: () => void;
  onOpenWorkspace?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  onSelectAuthTab,
  onOpenContact,
  onOpenWorkspace,
}) => {
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);

  const handleNavClick = (
    e: React.MouseEvent,
    target: string,
    action?: "signup" | "signin" | "contact" | "workspace"
  ) => {
    e.preventDefault();
    if (action === "workspace") {
      onOpenWorkspace?.();
      return;
    }

    if (action === "signup" || action === "signin") {
      onSelectAuthTab?.(action);
      const el = document.getElementById("auth-section");
      if (el) {
        el.scrollIntoView({ behavior: "smooth" });
      }
      return;
    }

    if (action === "contact") {
      if (onOpenContact) {
        onOpenContact();
      } else {
        const el = document.getElementById("contact");
        if (el) {
          el.scrollIntoView({ behavior: "smooth" });
        }
      }
      return;
    }

    const el = document.getElementById(target);
    if (el) {
      el.scrollIntoView({ behavior: "smooth" });
    }
  };

  const navItems = [
    { label: "Streak", target: "streak" },
    { label: "About", target: "about" },
    { label: "Workspace", target: "workspace", action: "workspace" as const },
    { label: "Contact us", target: "contact", action: "contact" as const },
    { label: "Sign Up", target: "auth-section", action: "signup" as const },
    { label: "Sign In", target: "auth-section", action: "signin" as const },
  ];

  return (
    <motion.header
      initial={{ y: -40, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
      className="absolute top-0 left-1/2 -translate-x-1/2 z-30"
    >
      <nav className="bg-black border-b border-x border-white/10 shadow-2xl rounded-b-2xl md:rounded-b-3xl px-3 sm:px-5 md:px-8 py-2 flex items-center gap-2.5 sm:gap-5 md:gap-9 lg:gap-11">
        {navItems.map((item, index) => {
          const isHovered = hoveredIdx === index;
          return (
            <a
              key={item.label}
              href={`#${item.target}`}
              onClick={(e) => handleNavClick(e, item.target, item.action)}
              onMouseEnter={() => setHoveredIdx(index)}
              onMouseLeave={() => setHoveredIdx(null)}
              className="text-[10px] sm:text-xs md:text-sm font-medium tracking-wide transition-colors duration-200 cursor-pointer whitespace-nowrap relative py-1"
              style={{
                color: isHovered ? "#E1E0CC" : "rgba(225, 224, 204, 0.8)",
              }}
            >
              {item.label === "Workspace" ? (
                <span className="inline-flex items-center gap-1.5 text-primary">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
                  Workspace
                </span>
              ) : (
                item.label
              )}
              {isHovered && (
                <motion.span
                  layoutId="nav-underline"
                  className="absolute bottom-0 left-0 right-0 h-[1px] bg-primary/60"
                  transition={{ type: "spring", stiffness: 350, damping: 30 }}
                />
              )}
            </a>
          );
        })}
      </nav>
    </motion.header>
  );
};
