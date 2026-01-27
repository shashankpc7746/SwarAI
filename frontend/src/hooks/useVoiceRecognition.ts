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
    recognition.interimResults = true; // Changed to true to see interim results
    recognition.lang = 'en-US';
    recognition.maxAlternatives = 3;

    recognition.onstart = () => {
      console.log('🎤 Voice recognition started - Speak now!');
      setIsListening(true);
      onAudioFeedback('🎤 Listening... Please speak now!');
    };

    recognition.onresult = (event: any) => {
      console.log('🎤 Raw recognition event:', event);
      console.log('🎤 Results length:', event.results.length);

      // Get the final result
      const last = event.results.length - 1;
      const transcript = event.results[last][0].transcript;
      const confidence = event.results[last][0].confidence;
      const isFinal = event.results[last].isFinal;

      console.log('🎤 Transcript:', transcript);
      console.log('🎤 Confidence:', confidence);
      console.log('🎤 Is Final:', isFinal);

      // Only process final results
      if (isFinal) {
        console.log('✅ Final transcript:', transcript);
        onAudioFeedback('✅ Got it! Processing your command...');
        onResult(transcript);
      } else {
        console.log('⏳ Interim result:', transcript);
      }
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