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
      // Only log critical errors, ignore common ones like 'no-speech'
      if (event.error !== 'no-speech' && event.error !== 'aborted') {
        console.error('Speech recognition error:', event.error);
      }
      setIsListening(false);

      // Provide user-friendly feedback based on error type
      if (event.error === 'no-speech') {
        onAudioFeedback('🎤 No speech detected. Tap to try again.');
      } else if (event.error === 'audio-capture') {
        onAudioFeedback('❌ Microphone not accessible. Please check permissions.');
      } else if (event.error === 'not-allowed') {
        onAudioFeedback('❌ Microphone permission denied. Please enable it in settings.');
      } else if (event.error !== 'aborted') {
        onAudioFeedback('❌ Sorry, I could not understand. Please try again.');
      }
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