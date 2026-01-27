'use client';

import { useState, useCallback, useRef } from 'react';

export interface CommandResult {
  success: boolean;
  message: string;
  intent: string;
  agent_used: string;
  timestamp: string;
  details?: any;
}

export default function useBackendApi() {
  const [backendStatus, setBackendStatus] = useState<'online' | 'offline' | 'checking'>('checking');
  const [isProcessing, setIsProcessing] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  const checkBackendStatus = useCallback(async () => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const response = await fetch('http://localhost:8000/health', {
        method: 'GET',
        signal: controller.signal,
        cache: 'no-cache'
      });
      
      clearTimeout(timeoutId);
      
      if (response.ok) {
        setBackendStatus('online');
        return true;
      } else {
        setBackendStatus('offline');
        return false;
      }
    } catch (error: any) {
      console.warn('Backend health check failed:', error.message);
      setBackendStatus('offline');
      return false;
    }
  }, []);

  const sendCommand = useCallback(async (command: string): Promise<CommandResult | null> => {
    if (!command.trim()) return null;
    
    // Cancel any ongoing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    setIsProcessing(true);
    
    try {
      // Create new abort controller for this request
      const controller = new AbortController();
      abortControllerRef.current = controller;
      
      // Set timeout
      const timeoutId = setTimeout(() => {
        controller.abort();
      }, 30000); // 30 second timeout
      
      console.log('Sending command:', command);
      
      const response = await fetch('http://localhost:8000/process-command', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ command }),
        signal: controller.signal,
        cache: 'no-cache'
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const result: CommandResult = await response.json();
      console.log('Command result received:', result);
      
      // Reset abort controller
      abortControllerRef.current = null;
      
      return result;
      
    } catch (error: any) {
      console.error('Command sending error:', error);
      
      let errorMessage = 'Unknown error occurred';
      if (error.name === 'AbortError') {
        errorMessage = 'Request timed out after 30 seconds';
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      // Check backend status after error
      setTimeout(checkBackendStatus, 1000);
      
      return {
        success: false,
        message: `❌ Error: ${errorMessage}`,
        intent: 'error',
        agent_used: 'none',
        timestamp: new Date().toISOString(),
        details: { error: errorMessage }
      };
      
    } finally {
      setIsProcessing(false);
      abortControllerRef.current = null;
    }
  }, [checkBackendStatus]);

  const playAudioFeedback = useCallback(async (text: string) => {
    try {
      const response = await fetch('http://localhost:8000/text-to-speech', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          text: text,
          language: 'en' 
        }),
        cache: 'no-cache'
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('Audio feedback played:', result.message);
      } else {
        console.warn('Audio feedback failed:', response.statusText);
      }
    } catch (error) {
      console.warn('Audio feedback error:', error);
    }
  }, []);

  return {
    backendStatus,
    isProcessing,
    checkBackendStatus,
    sendCommand,
    playAudioFeedback
  };
}