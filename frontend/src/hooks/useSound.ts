'use client';

import { useCallback } from 'react';
import useSoundHook from 'use-sound';

type SoundType = 'start' | 'success' | 'error' | 'processing' | 'notification';

export function useSound() {
  // In a real implementation, you would load actual sound files
  // For now, we'll use Web Audio API for simple beeps
  
  const playBeep = useCallback((frequency: number, duration: number = 200) => {
    try {
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();
      
      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);
      
      oscillator.frequency.value = frequency;
      oscillator.type = 'sine';
      
      gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration / 1000);
      
      oscillator.start(audioContext.currentTime);
      oscillator.stop(audioContext.currentTime + duration / 1000);
    } catch (error) {
      console.warn('Audio playback failed:', error);
    }
  }, []);
  
  const playSound = useCallback((type: SoundType) => {
    switch (type) {
      case 'start':
        playBeep(800, 150);
        break;
      case 'success':
        // Play a success chord
        playBeep(523, 100); // C
        setTimeout(() => playBeep(659, 100), 100); // E
        setTimeout(() => playBeep(784, 200), 200); // G
        break;
      case 'error':
        playBeep(300, 300);
        break;
      case 'processing':
        playBeep(600, 100);
        break;
      case 'notification':
        playBeep(440, 150);
        setTimeout(() => playBeep(554, 150), 150);
        break;
      default:
        playBeep(440, 100);
    }
  }, [playBeep]);
  
  // Web Speech API TTS for Vaani to actually speak
  const speak = useCallback((text: string, options: {
    rate?: number;
    pitch?: number;
    volume?: number;
    voice?: string;
  } = {}) => {
    try {
      // Check if speech synthesis is supported
      if (!('speechSynthesis' in window)) {
        console.warn('Speech synthesis not supported');
        return false;
      }

      // Stop any current speech
      window.speechSynthesis.cancel();

      const utterance = new SpeechSynthesisUtterance(text);
      
      // Configure voice settings
      utterance.rate = options.rate || 0.9; // Slightly slower for clarity
      utterance.pitch = options.pitch || 1.0;
      utterance.volume = options.volume || 0.8;
      
      // Try to use a good English voice
      const voices = window.speechSynthesis.getVoices();
      const englishVoice = voices.find(voice => 
        voice.lang.startsWith('en-') && 
        (voice.name.includes('Female') || voice.name.includes('Samantha') || voice.name.includes('Karen'))
      ) || voices.find(voice => voice.lang.startsWith('en-'));
      
      if (englishVoice) {
        utterance.voice = englishVoice;
      }

      // Add event listeners for debugging
      utterance.onstart = () => console.log('🔊 Vaani started speaking:', text.substring(0, 50) + '...');
      utterance.onend = () => console.log('🔊 Vaani finished speaking');
      utterance.onerror = (event) => console.error('🔊 Speech error:', event.error);
      
      // Speak the text
      window.speechSynthesis.speak(utterance);
      return true;
      
    } catch (error) {
      console.error('TTS error:', error);
      return false;
    }
  }, []);

  const stopSpeaking = useCallback(() => {
    try {
      window.speechSynthesis.cancel();
      console.log('🔊 Stopped Vaani speech');
    } catch (error) {
      console.error('Error stopping speech:', error);
    }
  }, []);

  // Legacy backend TTS (keeping for compatibility)
  const playTTS = useCallback(async (text: string, language: string = 'en') => {
    try {
      const response = await fetch('http://localhost:8000/text-to-speech', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          text,
          language,
          voice_speed: 1.0
        }),
        cache: 'no-cache'
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('🔊 Backend TTS result:', result);
        return result;
      }
    } catch (error) {
      console.warn('Backend TTS failed:', error);
    }
    
    return null;
  }, []);
  
  return {
    playSound,
    speak,        // New Web Speech API TTS
    stopSpeaking, // Stop current speech
    playTTS,      // Legacy backend TTS
    playBeep
  };
}