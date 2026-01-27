'use client';

import { motion } from 'framer-motion';
import { X, CheckCircle, AlertCircle, Clock, Users, Zap } from 'lucide-react';
import { CrewAIResult } from '../hooks/useCrewAI';
import { useEffect } from 'react';

interface ResultDisplayProps {
  result: CrewAIResult;
  onClose: () => void;
}

export function ResultDisplay({ result, onClose }: ResultDisplayProps) {
  const isSuccess = result.success;
  
  // Handle keyboard events
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        console.log('⌨️ Escape key pressed, closing modal');
        onClose();
      }
    };
    
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [onClose]);
  
  const formatExecutionTime = (seconds: number) => {
    if (seconds < 1) return `${Math.round(seconds * 1000)}ms`;
    return `${seconds.toFixed(2)}s`;
  };
  
  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };
  
  const handleClose = (e?: React.MouseEvent) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    console.log('🚪 Closing ResultDisplay modal - close button clicked');
    onClose();
  };
  
  const handleBackdropClick = (e: React.MouseEvent) => {
    // Only close if clicking directly on the backdrop, not on child elements
    if (e.target === e.currentTarget) {
      e.preventDefault();
      e.stopPropagation();
      console.log('🖱️ Backdrop clicked directly, closing modal');
      onClose();
    }
  };
  
  const handleContentClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };
  
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
      onClick={handleBackdropClick}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0, y: 20 }}
        animate={{ scale: 1, opacity: 1, y: 0 }}
        exit={{ scale: 0.9, opacity: 0, y: 20 }}
        transition={{ type: "spring", duration: 0.5 }}
        className="w-full max-w-2xl max-h-[80vh] overflow-hidden"
        onClick={handleContentClick}
      >
        {/* Main container with glassmorphism */}
        <div className="glass-strong rounded-2xl border border-white/20 shadow-2xl">
          {/* Header */}
          <div className={`
            p-6 border-b border-white/10
            ${isSuccess 
              ? 'bg-gradient-to-r from-green-500/20 to-emerald-500/20' 
              : 'bg-gradient-to-r from-red-500/20 to-orange-500/20'
            }
          `}>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                {isSuccess ? (
                  <CheckCircle className="w-8 h-8 text-green-400" />
                ) : (
                  <AlertCircle className="w-8 h-8 text-red-400" />
                )}
                <div>
                  <h3 className="text-xl font-bold text-white">
                    {isSuccess ? 'Task Completed' : 'Task Failed'}
                  </h3>
                  <p className="text-gray-300 text-sm">
                    Workflow ID: {result.workflow_id}
                  </p>
                </div>
              </div>
              
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={handleClose}
                className="p-2 rounded-lg hover:bg-white/10 transition-colors"
                aria-label="Close modal"
              >
                <X className="w-6 h-6 text-gray-300" />
              </motion.button>
            </div>
          </div>
          
          {/* Content */}
          <div className="p-6 space-y-6 max-h-96 overflow-y-auto">
            {/* Main message */}
            <div className="space-y-3">
              <h4 className="text-lg font-semibold text-white">Result</h4>
              <div className="
                p-4 rounded-xl border border-white/10
                bg-white/5 backdrop-blur-sm
              ">
                <p className="text-gray-200 leading-relaxed whitespace-pre-wrap">
                  {result.message}
                </p>
              </div>
            </div>
            
            {/* Metadata */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Crew Used */}
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <Zap className="w-4 h-4 text-blue-400" />
                  <span className="text-sm font-medium text-gray-300">Crew</span>
                </div>
                <p className="text-white font-medium">{result.agent_used}</p>
              </div>
              
              {/* Execution Time */}
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <Clock className="w-4 h-4 text-green-400" />
                  <span className="text-sm font-medium text-gray-300">Duration</span>
                </div>
                <p className="text-white font-medium">
                  {formatExecutionTime(result.execution_time)}
                </p>
              </div>
              
              {/* Timestamp */}
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <Clock className="w-4 h-4 text-purple-400" />
                  <span className="text-sm font-medium text-gray-300">Time</span>
                </div>
                <p className="text-white font-medium">
                  {formatTimestamp(result.timestamp)}
                </p>
              </div>
            </div>
            
            {/* Agents Involved */}
            {result.agents_involved && result.agents_involved.length > 0 && (
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <Users className="w-5 h-5 text-blue-400" />
                  <h4 className="text-lg font-semibold text-white">Agents Involved</h4>
                </div>
                <div className="flex flex-wrap gap-2">
                  {result.agents_involved.map((agent, index) => (
                    <motion.span
                      key={agent}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: index * 0.1 }}
                      className="
                        px-3 py-1 rounded-full text-sm font-medium
                        bg-blue-500/20 text-blue-300 border border-blue-500/30
                      "
                    >
                      {agent}
                    </motion.span>
                  ))}
                </div>
              </div>
            )}
            
            {/* Additional Results */}
            {result.results && Object.keys(result.results).length > 0 && (
              <div className="space-y-3">
                <h4 className="text-lg font-semibold text-white">Additional Details</h4>
                <div className="
                  p-4 rounded-xl border border-white/10
                  bg-white/5 backdrop-blur-sm
                  max-h-40 overflow-y-auto
                ">
                  <pre className="text-sm text-gray-300 whitespace-pre-wrap">
                    {JSON.stringify(result.results, null, 2)}
                  </pre>
                </div>
              </div>
            )}
          </div>
          
          {/* Footer */}
          <div className="px-6 py-4 border-t border-white/10">
            <div className="flex justify-end space-x-3">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleClose}
                className="
                  px-6 py-2 rounded-lg
                  bg-white/10 border border-white/20
                  text-white font-medium
                  hover:bg-white/20 transition-all duration-300
                "
              >
                Close
              </motion.button>
            </div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}