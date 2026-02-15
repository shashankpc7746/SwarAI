'use client';

import { motion } from 'framer-motion';
import {
  Bot,
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

      <div className="max-w-7xl mx-auto px-8 pt-16 pb-10">
        {/* Top section — Brand + Columns */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-16 mb-14">
          {/* Brand */}
          <div>
            <div className="flex items-center gap-3 mb-5">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white tracking-tight">SwarAI</h3>
                <p className="text-[11px] text-gray-500 font-medium tracking-wider uppercase">Multi-Agent AI System</p>
              </div>
            </div>
            <p className="text-sm text-gray-400 leading-relaxed mb-6">
              An advanced multi-agent AI assistant powered by CrewAI, LangChain, and Groq LLM with voice recognition and intelligent automation.
            </p>
            <motion.a
              href="https://github.com/shashankpc7746/SwarAI"
              target="_blank"
              rel="noopener noreferrer"
              whileHover={{ y: -2, scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-white/[0.05] border border-white/[0.1] text-gray-400 hover:text-white hover:bg-white/[0.1] hover:border-white/[0.18] transition-all duration-200 text-sm"
            >
              <Github className="w-4 h-4" />
              View on GitHub
              <ExternalLink className="w-3 h-3 opacity-60" />
            </motion.a>
          </div>

          {/* Features */}
          <div>
            <h4 className="text-xs font-semibold text-gray-300 uppercase tracking-widest mb-5">
              Features
            </h4>
            <ul className="space-y-3">
              {features.map((feature) => (
                <li key={feature} className="text-sm text-gray-500">
                  {feature}
                </li>
              ))}
            </ul>
          </div>

          {/* Tech Stack */}
          <div>
            <h4 className="text-xs font-semibold text-gray-300 uppercase tracking-widest mb-5">
              Technology
            </h4>
            <ul className="space-y-3">
              {techStack.map((tech) => (
                <li key={tech.label}>
                  <a
                    href={tech.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-gray-500 hover:text-white transition-colors duration-200 inline-flex items-center gap-1.5 group"
                  >
                    {tech.label}
                    <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
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
          <p className="text-xs text-gray-600 flex items-center gap-1.5">
            &copy; {currentYear} SwarAI. Crafted with
            <motion.span
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ repeat: Infinity, duration: 1.5, ease: 'easeInOut' }}
            >
              <Heart className="w-3 h-3 text-red-500 fill-red-500 inline" />
            </motion.span>
            by the SwarAI Team
          </p>

          <div className="flex items-center gap-4 text-[11px] text-gray-600">
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
