'use client';

import { useState, useCallback } from 'react';

export default function useVoiceRecognition() {
  const [isListening, setIsListening] = useState(false);

  const startVoiceRecognition = useCallback((
    onResult: (transcript: string) => void,
    onAudioFeedback: (message: string) => void
  ) => {
    if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
      alert('Speech recognition not supported. Please use Chrome or Edge.');
      return;
    }

    const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
    const recognition = new SpeechRecognition();
    
    // Enhanced settings for better recognition
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';
    recognition.maxAlternatives = 3;
    
    recognition.onstart = () => {
      console.log('Voice recognition started');
      setIsListening(true);
      onAudioFeedback('🎤 Listening... Please speak now!');
    };
    
    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      console.log('Voice recognition result:', transcript);
      onAudioFeedback('✅ Got it! Processing your command...');
      onResult(transcript);
    };
    
    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);
      onAudioFeedback('❌ Sorry, I could not understand. Please try again.');
    };
    
    recognition.onend = () => {
      console.log('Voice recognition ended');
      setIsListening(false);
    };
    
    try {
      recognition.start();
    } catch (error) {
      console.error('Failed to start voice recognition:', error);
      setIsListening(false);
      onAudioFeedback('❌ Voice recognition failed to start');
    }
  }, []);

  return {
    isListening,
    startVoiceRecognition
  };
}