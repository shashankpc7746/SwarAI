'use client';

import { useState } from 'react';
import { Mic, Bot } from 'lucide-react';

interface VoiceButtonProps {
  isListening: boolean;
  isProcessing: boolean;
  backendStatus: 'online' | 'offline' | 'checking';
  onStartListening: () => void;
}

export default function VoiceButton({ 
  isListening, 
  isProcessing, 
  backendStatus, 
  onStartListening 
}: VoiceButtonProps) {
  return (
    <div className="mb-12">
      <button
        onClick={onStartListening}
        disabled={backendStatus !== 'online' || isListening || isProcessing}
        className={`group relative w-48 h-48 rounded-full transition-all duration-300 transform hover:scale-110 ${
          isListening 
            ? 'bg-red-500 shadow-2xl animate-pulse scale-110' 
            : isProcessing
            ? 'bg-yellow-500 shadow-xl animate-bounce'
            : 'bg-blue-500 hover:bg-blue-600 shadow-xl hover:shadow-2xl'
        } disabled:opacity-50 disabled:cursor-not-allowed`}
      >
        <div className="absolute inset-4 rounded-full bg-white bg-opacity-20 flex items-center justify-center">
          {isListening ? (
            <div className="flex flex-col items-center">
              <Mic className="w-16 h-16 text-white animate-pulse" />
              <span className="text-white text-sm font-bold mt-2">Listening...</span>
            </div>
          ) : isProcessing ? (
            <div className="flex flex-col items-center">
              <Bot className="w-16 h-16 text-white animate-spin" />
              <span className="text-white text-sm font-bold mt-2">Processing...</span>
            </div>
          ) : (
            <div className="flex flex-col items-center">
              <Mic className="w-16 h-16 text-white group-hover:scale-110 transition-transform" />
              <span className="text-white text-lg font-bold mt-2">TAP TO SPEAK</span>
            </div>
          )}
        </div>
        
        {/* Ripple effect */}
        {(isListening || isProcessing) && (
          <div className="absolute inset-0 rounded-full border-4 border-white animate-ping opacity-30" />
        )}
      </button>
    </div>
  );
}