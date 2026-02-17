'use client';

import { useCallback, useEffect, useRef } from 'react';
import useSoundHook from 'use-sound';

type SoundType = 'start' | 'success' | 'error' | 'processing' | 'notification';

// Global force stop function that works even after component unmounts
if (typeof window !== 'undefined') {
  (window as any).__forceSpeechStop = () => {
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
      setTimeout(() => window.speechSynthesis?.cancel(), 10);
      setTimeout(() => window.speechSynthesis?.cancel(), 50);
      setTimeout(() => window.speechSynthesis?.cancel(), 100);
      console.log('🔊 Global force speech stop executed');
    }
  };
}

export function useSound() {
  // Pre-cache voices so they're ready when speak() is called
  const cachedVoiceRef = useRef<SpeechSynthesisVoice | null>(null);
  const voicesLoadedRef = useRef(false);

  useEffect(() => {
    const loadVoices = () => {
      const voices = window.speechSynthesis?.getVoices() || [];
      if (voices.length > 0) {
        cachedVoiceRef.current = voices.find(v =>
          v.lang.startsWith('en-') &&
          (v.name.includes('Female') || v.name.includes('Samantha') || v.name.includes('Karen'))
        ) || voices.find(v => v.lang.startsWith('en-')) || null;
        voicesLoadedRef.current = true;
      }
    };
    loadVoices();
    window.speechSynthesis?.addEventListener('voiceschanged', loadVoices);
    return () => window.speechSynthesis?.removeEventListener('voiceschanged', loadVoices);
  }, []);

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

  // Web Speech API TTS for SwarAI to actually speak
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

      // FORCE stop any current speech - multiple cancels for reliability
      window.speechSynthesis.cancel();
      setTimeout(() => window.speechSynthesis.cancel(), 10);

      const utterance = new SpeechSynthesisUtterance(text);

      // Configure voice settings
      utterance.rate = options.rate || 0.9; // Slightly slower for clarity
      utterance.pitch = options.pitch || 1.0;
      utterance.volume = options.volume || 0.8;

      // Use pre-cached voice for instant playback
      if (cachedVoiceRef.current) {
        utterance.voice = cachedVoiceRef.current;
      }

      // Add event listeners for debugging
      utterance.onstart = () => console.log('🔊 SwarAI started speaking:', text.substring(0, 50) + '...');
      utterance.onend = () => console.log('🔊 SwarAI finished speaking');
      utterance.onerror = (event) => {
        // Only log critical errors, ignore interruptions
        if (event.error !== 'interrupted' && event.error !== 'canceled') {
          console.error('🔊 Speech error:', event.error);
        }
      };

      // Speak with minimal delay — use setTimeout(50) for better cancellation timing
      setTimeout(() => {
        // Double-check it wasn't cancelled in the meantime
        if (window.speechSynthesis && !window.speechSynthesis.speaking) {
          window.speechSynthesis.speak(utterance);
        }
      }, 50);
      return true;

    } catch (error) {
      console.error('TTS error:', error);
      return false;
    }
  }, []);

  const stopSpeaking = useCallback(() => {
    try {
      // AGGRESSIVE cancellation - multiple attempts to ensure it stops
      if (window.speechSynthesis) {
        // Cancel immediately
        window.speechSynthesis.cancel();
        
        // Force multiple cancels with delays (some browsers need this)
        setTimeout(() => window.speechSynthesis.cancel(), 10);
        setTimeout(() => window.speechSynthesis.cancel(), 50);
        setTimeout(() => window.speechSynthesis.cancel(), 100);
        
        console.log('🔊 Stopped SwarAI speech (forced multi-cancel)');
      }
    } catch (error) {
      console.error('Error stopping speech:', error);
    }
  }, []);

  // Global cleanup - works even after component unmounts
  useEffect(() => {
    const forceStopSpeech = () => {
      // Use global force stop if available
      if ((window as any).__forceSpeechStop) {
        (window as any).__forceSpeechStop();
      } else if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
        setTimeout(() => window.speechSynthesis?.cancel(), 0);
      }
    };

    // Stop speech on page unload/refresh
    window.addEventListener('beforeunload', forceStopSpeech);
    window.addEventListener('pagehide', forceStopSpeech);
    
    // Cleanup on unmount
    return () => {
      forceStopSpeech();
      window.removeEventListener('beforeunload', forceStopSpeech);
      window.removeEventListener('pagehide', forceStopSpeech);
    };
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