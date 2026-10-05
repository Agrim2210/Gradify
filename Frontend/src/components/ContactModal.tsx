import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Send, Mail, MessageSquare, CheckCircle2 } from "lucide-react";

interface ContactModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ContactModal: React.FC<ContactModalProps> = ({ isOpen, onClose }) => {
  const [sent, setSent] = useState(false);
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSent(true);
    setTimeout(() => {
      setSent(false);
      onClose();
    }, 2000);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="absolute inset-0 bg-black/80 backdrop-blur-md"
          />

          {/* Dialog Container */}
          <motion.div
            initial={{ scale: 0.95, opacity: 0, y: 20 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.95, opacity: 0, y: 20 }}
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="relative z-10 w-full max-w-lg bg-[#101010] border border-white/10 rounded-2xl p-6 sm:p-8 shadow-2xl overflow-hidden"
          >
            <div className="bg-noise absolute inset-0 opacity-[0.25] mix-blend-overlay pointer-events-none" />

            <div className="relative z-10 flex items-center justify-between mb-6">
              <div>
                <span className="text-[11px] font-mono uppercase tracking-widest text-primary/60">
                  Direct Line // Support & Inquiries
                </span>
                <h3 className="text-xl font-medium mt-1" style={{ color: "#E1E0CC" }}>
                  Contact Gradify Lab
                </h3>
              </div>
              <button
                type="button"
                onClick={onClose}
                className="w-8 h-8 rounded-full bg-white/5 hover:bg-white/10 flex items-center justify-center text-gray-400 hover:text-primary transition-colors cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {sent ? (
              <div className="py-12 text-center relative z-10">
                <CheckCircle2 className="w-12 h-12 text-primary mx-auto mb-4 animate-bounce" />
                <h4 className="text-lg font-medium text-primary">
                  Dispatch Received
                </h4>
                <p className="text-xs text-gray-400 mt-2">
                  Our academic engineering team will respond within 12 hours.
                </p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="relative z-10 space-y-4">
                <div>
                  <label className="block text-xs font-mono uppercase tracking-wider text-primary/80 mb-1">
                    Your Academic Email
                  </label>
                  <div className="relative">
                    <Mail className="w-4 h-4 text-gray-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                    <input
                      type="email"
                      required
                      placeholder="scholar@university.edu"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full bg-[#181818] border border-white/10 rounded-xl py-2.5 pl-10 pr-4 text-xs sm:text-sm text-[#E1E0CC] placeholder-gray-600 focus:outline-none focus:border-primary/60"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-mono uppercase tracking-wider text-primary/80 mb-1">
                    Message or Campus Inquiry
                  </label>
                  <div className="relative">
                    <MessageSquare className="w-4 h-4 text-gray-500 absolute left-3.5 top-3" />
                    <textarea
                      required
                      rows={4}
                      placeholder="Tell us about your university cohort, feature requests, or questions..."
                      value={message}
                      onChange={(e) => setMessage(e.target.value)}
                      className="w-full bg-[#181818] border border-white/10 rounded-xl py-2.5 pl-10 pr-4 text-xs sm:text-sm text-[#E1E0CC] placeholder-gray-600 focus:outline-none focus:border-primary/60 resize-none"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  className="w-full bg-primary text-black font-medium py-3 rounded-xl text-xs sm:text-sm flex items-center justify-center gap-2 hover:brightness-105 active:scale-[0.99] transition-all cursor-pointer shadow-lg"
                >
                  <span>Transmit Transmission</span>
                  <Send className="w-4 h-4" />
                </button>
              </form>
            )}
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
};
