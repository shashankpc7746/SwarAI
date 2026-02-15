'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Bot,
  Github,
  Linkedin,
  Twitter,
  Mail,
  Heart,
  ExternalLink,
  ChevronUp,
  Sparkles,
  Cpu,
  Globe,
  Shield,
  Zap,
  MessageCircle,
} from 'lucide-react';

const footerLinks = {
  product: [
    { label: 'Voice Assistant', href: '#voice' },
    { label: 'AI Agents', href: '#agents' },
    { label: 'System Control', href: '#system' },
    { label: 'App Launcher', href: '#launcher' },
  ],
  technology: [
    { label: 'CrewAI', href: 'https://www.crewai.com/', external: true },
    { label: 'LangChain', href: 'https://www.langchain.com/', external: true },
    { label: 'Groq LLM', href: 'https://groq.com/', external: true },
    { label: 'Next.js', href: 'https://nextjs.org/', external: true },
  ],
  resources: [
    { label: 'Documentation', href: '#docs' },
    { label: 'Quick Start', href: '#quickstart' },
    { label: 'API Reference', href: '#api' },
    { label: 'GitHub', href: 'https://github.com/shashankpc7746/SwarAI', external: true },
  ],
};

const techBadges = [
  { name: 'Python', icon: Cpu, color: 'text-yellow-400' },
  { name: 'FastAPI', icon: Zap, color: 'text-teal-400' },
  { name: 'Next.js', icon: Globe, color: 'text-white' },
  { name: 'WebSocket', icon: MessageCircle, color: 'text-blue-400' },
  { name: 'JWT Auth', icon: Shield, color: 'text-green-400' },
  { name: 'Groq AI', icon: Sparkles, color: 'text-purple-400' },
];

export function Footer() {
  const [hoveredTech, setHoveredTech] = useState<string | null>(null);
  const currentYear = new Date().getFullYear();

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <footer className="relative mt-16 border-t border-white/[0.06] bg-gradient-to-b from-transparent via-white/[0.01] to-white/[0.03]">
      {/* Decorative top glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-1/2 h-px bg-gradient-to-r from-transparent via-indigo-500/50 to-transparent" />

      {/* Scroll to top button */}
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

      <div className="max-w-6xl mx-auto px-6 py-12">
        {/* Main footer grid */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-10 mb-12">
          {/* Brand column */}
          <div className="md:col-span-4">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white tracking-tight">SwarAI</h3>
                <p className="text-[11px] text-gray-500 font-medium tracking-wider uppercase">Multi-Agent AI System</p>
              </div>
            </div>
            <p className="text-sm text-gray-400 leading-relaxed mb-5 max-w-xs">
              Advanced AI assistant powered by CrewAI and Groq LLM. Voice-controlled automation with 13+ specialized agents.
            </p>

            {/* Social links */}
            <div className="flex items-center gap-2">
              {[
                { icon: Github, href: 'https://github.com/shashankpc7746/SwarAI', label: 'GitHub' },
                { icon: Linkedin, href: '#', label: 'LinkedIn' },
                { icon: Twitter, href: '#', label: 'Twitter' },
                { icon: Mail, href: 'mailto:contact@swarai.dev', label: 'Email' },
              ].map((social) => (
                <motion.a
                  key={social.label}
                  href={social.href}
                  target={social.href.startsWith('http') ? '_blank' : undefined}
                  rel={social.href.startsWith('http') ? 'noopener noreferrer' : undefined}
                  whileHover={{ y: -2, scale: 1.1 }}
                  whileTap={{ scale: 0.95 }}
                  className="w-9 h-9 rounded-lg bg-white/[0.05] border border-white/[0.08] flex items-center justify-center text-gray-500 hover:text-white hover:bg-white/[0.1] hover:border-white/[0.15] transition-all duration-200"
                  aria-label={social.label}
                >
                  <social.icon className="w-4 h-4" />
                </motion.a>
              ))}
            </div>
          </div>

          {/* Links columns */}
          {Object.entries(footerLinks).map(([category, links]) => (
            <div key={category} className="md:col-span-2">
              <h4 className="text-xs font-semibold text-gray-300 uppercase tracking-widest mb-4">
                {category}
              </h4>
              <ul className="space-y-2.5">
                {links.map((link) => (
                  <li key={link.label}>
                    <a
                      href={link.href}
                      target={(link as any).external ? '_blank' : undefined}
                      rel={(link as any).external ? 'noopener noreferrer' : undefined}
                      className="text-sm text-gray-500 hover:text-white transition-colors duration-200 flex items-center gap-1.5 group"
                    >
                      {link.label}
                      {(link as any).external && (
                        <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                      )}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}

          {/* Tech badges column */}
          <div className="md:col-span-2">
            <h4 className="text-xs font-semibold text-gray-300 uppercase tracking-widest mb-4">
              Built With
            </h4>
            <div className="flex flex-wrap gap-2">
              {techBadges.map((tech) => (
                <motion.div
                  key={tech.name}
                  onMouseEnter={() => setHoveredTech(tech.name)}
                  onMouseLeave={() => setHoveredTech(null)}
                  whileHover={{ scale: 1.08 }}
                  className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border transition-all duration-200 cursor-default ${
                    hoveredTech === tech.name
                      ? 'bg-white/[0.08] border-white/[0.15]'
                      : 'bg-white/[0.03] border-white/[0.06]'
                  }`}
                >
                  <tech.icon className={`w-3 h-3 ${tech.color}`} />
                  <span className="text-[11px] font-medium text-gray-400">{tech.name}</span>
                </motion.div>
              ))}
            </div>
          </div>
        </div>

        {/* Divider */}
        <div className="h-px bg-gradient-to-r from-transparent via-white/[0.08] to-transparent mb-6" />

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
            by{' '}
            <a
              href="https://github.com/shashankpc7746"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-white transition-colors font-medium"
            >
              SwarAI Team
            </a>
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
