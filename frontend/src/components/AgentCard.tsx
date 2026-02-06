'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { LucideIcon } from 'lucide-react';
import { useState } from 'react';

interface Agent {
  id: string;
  name: string;
  description: string;
  icon: LucideIcon;
  color: string;
  command: string;
  examples?: string[];
}

interface AgentCardProps {
  agent: Agent;
  isActive: boolean;
  isDisabled: boolean;
  onExampleClick: (example: string) => void;
  delay?: number;
}

export function AgentCard({
  agent,
  isActive,
  isDisabled,
  onExampleClick,
  delay = 0
}: AgentCardProps) {
  const Icon = agent.icon;
  const [showExamples, setShowExamples] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5 }}
      whileHover={{
        y: isDisabled ? 0 : -8,
        scale: isDisabled ? 1 : 1.02,
        zIndex: isDisabled ? 1 : 10
      }}
      className={`relative group ${isDisabled ? 'opacity-50 cursor-not-allowed' : ''
        }`}
      onMouseEnter={() => !isDisabled && setShowExamples(true)}
      onMouseLeave={() => setShowExamples(false)}
    >
      {/* Background gradient */}
      <div className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${agent.color} opacity-20 group-hover:opacity-30 transition-opacity duration-500`} />

      {/* Glass effect */}
      <div className="relative p-6 rounded-2xl border border-white/20 glass backdrop-blur-lg group-hover:border-white/30 transition-all duration-500">
        {/* Active indicator */}
        {isActive && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="absolute top-3 right-3 w-3 h-3 bg-green-400 rounded-full shadow-lg z-10"
          >
            <div className="absolute inset-0 bg-green-400 rounded-full animate-ping" />
          </motion.div>
        )}

        {/* Icon container */}
        <div className="relative mb-4 pointer-events-none">
          <motion.div
            whileHover={{ rotate: isDisabled ? 0 : 360 }}
            transition={{ duration: 0.6 }}
            className={`w-16 h-16 rounded-xl bg-gradient-to-br ${agent.color} flex items-center justify-center mx-auto shadow-lg group-hover:shadow-xl transition-shadow duration-500`}
          >
            <Icon className="w-8 h-8 text-white" />
          </motion.div>

          {/* Floating particles */}
          <motion.div
            animate={{
              y: [-2, 2, -2],
              opacity: [0.5, 1, 0.5]
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: "easeInOut"
            }}
            className="absolute -top-1 -right-1 w-2 h-2 bg-white/60 rounded-full"
          />
          <motion.div
            animate={{
              y: [2, -2, 2],
              opacity: [0.3, 0.8, 0.3]
            }}
            transition={{
              duration: 4,
              repeat: Infinity,
              ease: "easeInOut",
              delay: 1
            }}
            className="absolute -bottom-1 -left-1 w-1.5 h-1.5 bg-white/40 rounded-full"
          />
        </div>

        {/* Content */}
        <div className="text-center">
          <h3 className="text-xl font-bold text-white mb-2 group-hover:text-blue-100 transition-colors duration-500 pointer-events-none">
            {agent.name}
          </h3>
          <p className="text-gray-300 text-sm leading-relaxed pointer-events-none">
            {agent.description}
          </p>

          {/* Examples - Show below description */}
          <AnimatePresence mode="wait">
            {showExamples && agent.examples && agent.examples.length > 0 && (
              <motion.div
                key="examples"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.3, ease: "easeOut" }}
                className="mt-4 overflow-hidden"
              >
                <div className="text-xs text-blue-400 mb-2 pointer-events-none font-medium">Click to try:</div>
                <div className="space-y-2">
                  {agent.examples.map((example, idx) => (
                    <motion.button
                      key={idx}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.08, duration: 0.2 }}
                      onClick={(e) => {
                        e.stopPropagation();
                        if (!isDisabled) {
                          onExampleClick(example);
                        }
                      }}
                      disabled={isDisabled}
                      className={`w-full text-xs text-left text-blue-300 bg-white/10 hover:bg-white/20 rounded-lg px-3 py-2 transition-all duration-300 border border-white/20 hover:border-blue-400/50 ${isDisabled ? 'cursor-not-allowed' : 'cursor-pointer hover:scale-105'
                        }`}
                    >
                      "{example}"
                    </motion.button>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Hover glow effect */}
        <motion.div
          className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${agent.color} opacity-0 group-hover:opacity-10 transition-opacity duration-500 pointer-events-none`}
        />
      </div>
    </motion.div>
  );
}