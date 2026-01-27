'use client';

import { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';

interface VoiceVisualizationProps {
  isActive: boolean;
}

export function VoiceVisualization({ isActive }: VoiceVisualizationProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number | null>(null);
  
  useEffect(() => {
    if (!isActive) {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      return;
    }
    
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    const width = canvas.width;
    const height = canvas.height;
    const centerY = height / 2;
    
    // Create animated waveform
    const animate = (timestamp: number) => {
      ctx.clearRect(0, 0, width, height);
      
      // Create gradient
      const gradient = ctx.createLinearGradient(0, 0, width, 0);
      gradient.addColorStop(0, 'rgba(59, 130, 246, 0.8)');
      gradient.addColorStop(0.5, 'rgba(147, 51, 234, 0.8)');
      gradient.addColorStop(1, 'rgba(59, 130, 246, 0.8)');
      
      ctx.strokeStyle = gradient;
      ctx.lineWidth = 3;
      ctx.lineCap = 'round';
      
      // Draw animated waveform
      ctx.beginPath();
      
      for (let x = 0; x < width; x += 2) {
        const frequency = 0.02;
        const amplitude = 20 + Math.sin(timestamp * 0.005 + x * 0.01) * 15;
        const y = centerY + Math.sin(x * frequency + timestamp * 0.01) * amplitude;
        
        if (x === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      }
      
      ctx.stroke();
      
      // Draw particles
      const particleCount = 8;
      for (let i = 0; i < particleCount; i++) {
        const angle = (timestamp * 0.002 + i * (Math.PI * 2 / particleCount));
        const radius = 40 + Math.sin(timestamp * 0.003 + i) * 20;
        const x = width / 2 + Math.cos(angle) * radius;
        const y = height / 2 + Math.sin(angle) * radius;
        
        const particleGradient = ctx.createRadialGradient(x, y, 0, x, y, 8);
        particleGradient.addColorStop(0, 'rgba(255, 255, 255, 0.8)');
        particleGradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
        
        ctx.fillStyle = particleGradient;
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fill();
      }
      
      animationRef.current = requestAnimationFrame(animate);
    };
    
    animationRef.current = requestAnimationFrame(animate);
    
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isActive]);
  
  if (!isActive) return null;
  
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.8 }}
      className="absolute -inset-24 flex items-center justify-center pointer-events-none"
    >
      <canvas
        ref={canvasRef}
        width={400}
        height={200}
        className="w-full h-full"
      />
    </motion.div>
  );
}