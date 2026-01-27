'use client';

import { motion } from 'framer-motion';
import { Wifi, WifiOff, Loader2 } from 'lucide-react';

type Status = 'online' | 'offline' | 'checking';

interface StatusIndicatorProps {
  status: Status;
  label: string;
  showLabel?: boolean;
}

export function StatusIndicator({ 
  status, 
  label, 
  showLabel = true 
}: StatusIndicatorProps) {
  const getStatusConfig = (status: Status) => {
    switch (status) {
      case 'online':
        return {
          color: 'bg-green-500',
          textColor: 'text-green-400',
          icon: Wifi,
          text: 'Online',
          shadowColor: 'shadow-green-500/50'
        };
      case 'offline':
        return {
          color: 'bg-red-500',
          textColor: 'text-red-400',
          icon: WifiOff,
          text: 'Offline',
          shadowColor: 'shadow-red-500/50'
        };
      case 'checking':
        return {
          color: 'bg-yellow-500',
          textColor: 'text-yellow-400',
          icon: Loader2,
          text: 'Checking',
          shadowColor: 'shadow-yellow-500/50'
        };
      default:
        return {
          color: 'bg-gray-500',
          textColor: 'text-gray-400',
          icon: WifiOff,
          text: 'Unknown',
          shadowColor: 'shadow-gray-500/50'
        };
    }
  };
  
  const config = getStatusConfig(status);
  const Icon = config.icon;
  
  return (
    <div className="flex items-center space-x-3">
      {/* Status indicator */}
      <div className="relative">
        <motion.div
          className={`
            w-3 h-3 rounded-full ${config.color}
            ${config.shadowColor} shadow-lg
          `}
          animate={{
            scale: status === 'checking' ? [1, 1.2, 1] : 1,
            opacity: status === 'online' ? [1, 0.7, 1] : 1
          }}
          transition={{
            duration: status === 'checking' ? 1.5 : 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        
        {/* Pulse ring for online status */}
        {status === 'online' && (
          <motion.div
            className="absolute inset-0 rounded-full border-2 border-green-400"
            animate={{
              scale: [1, 2.5],
              opacity: [0.8, 0]
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeOut"
            }}
          />
        )}
      </div>
      
      {/* Label and status text */}
      {showLabel && (
        <div className="flex items-center space-x-2">
          <Icon 
            className={`w-4 h-4 ${config.textColor} ${
              status === 'checking' ? 'animate-spin' : ''
            }`} 
          />
          <span className="text-sm text-gray-300">
            {label}: <span className={config.textColor}>{config.text}</span>
          </span>
        </div>
      )}
    </div>
  );
}