'use client';

import { motion } from 'framer-motion';
import {
  Github,
  Heart,
  ExternalLink,
  ChevronUp,
} from 'lucide-react';

const techStack = [
  { label: 'CrewAI', href: 'https://www.crewai.com/' },
  { label: 'LangChain', href: 'https://www.langchain.com/' },
  { label: 'Groq LLM', href: 'https://groq.com/' },
  { label: 'FastAPI', href: 'https://fastapi.tiangolo.com/' },
  { label: 'Next.js', href: 'https://nextjs.org/' },
];

const features = [
  'Voice Assistant',
  'AI Agents',
  'System Control',
  'App Launcher',
  'Web Search',
  'File Manager',
];

export function Footer() {
  const currentYear = new Date().getFullYear();

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <footer className="relative mt-20 border-t border-white/[0.06]">
      {/* Decorative top glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-1/3 h-px bg-gradient-to-r from-transparent via-indigo-500/40 to-transparent" />

      {/* Scroll to top */}
      <div className="flex justify-center -mt-5">
        <motion.button
          onClick={scrollToTop}
          whileHover={{ y: -3, scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
          className="w-10 h-10 rounded-full bg-white/[0.07] backdrop-blur-sm border border-white/10 flex items-center justify-center text-gray-400 hover:text-white hover:bg-white/[0.12] transition-colors cursor-pointer"
          aria-label="Scroll to top"
        >
          <ChevronUp className="w-5 h-5" />
        </motion.button>
      </div>

      <div className="max-w-7xl mx-auto px-8 pt-16 pb-12">
        {/* Top section — Brand + Columns */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-20 mb-16">
          {/* Brand */}
          <div className="flex flex-col items-center md:items-start text-center md:text-left">
            <div className="flex items-center gap-3 mb-6">
              <motion.div
                whileHover={{ scale: 1.05 }}
                className="w-14 h-14 rounded-2xl bg-white/10 backdrop-blur-sm flex items-center justify-center overflow-hidden p-1.5"
              >
                <img
                  src="/swarai_logo.png"
                  alt="SwarAI Logo"
                  className="w-full h-full object-contain rounded-xl"
                />
              </motion.div>
              <div>
                <h3 className="text-xl font-bold text-white tracking-tight">SwarAI</h3>
                <p className="text-xs text-gray-500 font-medium tracking-wider uppercase">Multi-Agent AI System</p>
              </div>
            </div>
            <p className="text-[15px] text-gray-400 leading-relaxed mb-7 max-w-sm">
              An advanced multi-agent AI assistant powered by CrewAI, LangChain, and Groq LLM with voice recognition and intelligent automation.
            </p>
            <motion.a
              href="https://github.com/shashankpc7746/SwarAI"
              target="_blank"
              rel="noopener noreferrer"
              whileHover={{ y: -2, scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-white/[0.05] border border-white/[0.1] text-gray-400 hover:text-white hover:bg-white/[0.1] hover:border-white/[0.18] transition-all duration-200 text-[15px]"
            >
              <Github className="w-4 h-4" />
              View on GitHub
              <ExternalLink className="w-3.5 h-3.5 opacity-60" />
            </motion.a>
          </div>

          {/* Features */}
          <div className="flex flex-col items-center md:items-start">
            <h4 className="text-sm font-semibold text-gray-300 uppercase tracking-widest mb-6 text-center md:text-left">
              Features
            </h4>
            <ul className="space-y-3.5 text-center md:text-left">
              {features.map((feature) => (
                <li key={feature} className="text-[15px] text-gray-500">
                  {feature}
                </li>
              ))}
            </ul>
          </div>

          {/* Tech Stack */}
          <div className="flex flex-col items-center md:items-start">
            <h4 className="text-sm font-semibold text-gray-300 uppercase tracking-widest mb-6 text-center md:text-left">
              Technology
            </h4>
            <ul className="space-y-3.5 text-center md:text-left">
              {techStack.map((tech) => (
                <li key={tech.label}>
                  <a
                    href={tech.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[15px] text-gray-500 hover:text-white transition-colors duration-200 inline-flex items-center gap-1.5 group"
                  >
                    {tech.label}
                    <ExternalLink className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Divider */}
        <div className="h-px bg-gradient-to-r from-transparent via-white/[0.08] to-transparent mb-8" />

        {/* Bottom bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-sm text-gray-600 flex items-center gap-1.5">
            &copy; {currentYear} SwarAI. Crafted with
            <motion.span
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ repeat: Infinity, duration: 1.5, ease: 'easeInOut' }}
            >
              <Heart className="w-3.5 h-3.5 text-red-500 fill-red-500 inline" />
            </motion.span>
            by the SwarAI Team
          </p>

          <div className="flex items-center gap-4 text-xs text-gray-600">
            <span className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
              All systems operational
            </span>
            <span className="hidden sm:inline text-white/[0.08]">|</span>
            <span>v2.0</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
