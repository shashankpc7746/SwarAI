'use client';

import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Mic,
  Bot,
  MessageCircle,
  FileText,
  Calendar,
  Zap,
  Sparkles,
  Settings,
  Wifi,
  WifiOff,
  History,
  X,
  User,
  Phone,
  CreditCard,
  AppWindow,
  Globe,
  ListTodo,
  Camera,
  Monitor,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import useVoiceRecognition from '@/hooks/useVoiceRecognition';
import { useCrewAI } from '@/hooks/useCrewAI';
import { useSound } from '@/hooks/useSound';
import { VoiceVisualization } from '@/components/VoiceVisualization';
import { AgentCard } from '@/components/AgentCard';
import { ResultDisplay } from '@/components/ResultDisplay';
import { StatusIndicator } from '@/components/StatusIndicator';
import ProtectedRoute from '@/components/ProtectedRoute';
import { ProfileSettings } from '@/components/ProfileSettings';
import { useAuth } from '@/context/AuthContext';

// === Cursor-following glow component ===
function CursorGlow() {
  const glowRef = useRef<HTMLDivElement>(null);
  const trailRef = useRef<HTMLDivElement>(null);
  const mousePos = useRef({ x: 0, y: 0 });
  const currentPos = useRef({ x: 0, y: 0 });
  const trailPos = useRef({ x: 0, y: 0 });
  const rafId = useRef<number>(0);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      mousePos.current = { x: e.clientX, y: e.clientY };
    };

    const animate = () => {
      // Smooth interpolation for main glow
      currentPos.current.x += (mousePos.current.x - currentPos.current.x) * 0.08;
      currentPos.current.y += (mousePos.current.y - currentPos.current.y) * 0.08;

      // Even slower trailing glow
      trailPos.current.x += (mousePos.current.x - trailPos.current.x) * 0.03;
      trailPos.current.y += (mousePos.current.y - trailPos.current.y) * 0.03;

      if (glowRef.current) {
        glowRef.current.style.transform = `translate(${currentPos.current.x - 200}px, ${currentPos.current.y - 200}px)`;
      }
      if (trailRef.current) {
        trailRef.current.style.transform = `translate(${trailPos.current.x - 300}px, ${trailPos.current.y - 300}px)`;
      }

      rafId.current = requestAnimationFrame(animate);
    };

    window.addEventListener('mousemove', handleMouseMove);
    rafId.current = requestAnimationFrame(animate);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      cancelAnimationFrame(rafId.current);
    };
  }, []);

  return (
    <>
      {/* Primary cursor glow */}
      <div
        ref={glowRef}
        className="fixed pointer-events-none -z-10"
        style={{
          width: 500,
          height: 500,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(99, 102, 241, 0.18) 0%, rgba(99, 102, 241, 0.06) 40%, transparent 70%)',
          willChange: 'transform',
        }}
      />
      {/* Trailing secondary glow */}
      <div
        ref={trailRef}
        className="fixed pointer-events-none -z-10"
        style={{
          width: 700,
          height: 700,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(168, 85, 247, 0.10) 0%, rgba(168, 85, 247, 0.03) 40%, transparent 70%)',
          willChange: 'transform',
        }}
      />
    </>
  );
}

export default function CrewAIPage() {
  const [currentAgent, setCurrentAgent] = useState<string | null>(null);
  const [showResults, setShowResults] = useState(false);
  const [showWhatsAppPopup, setShowWhatsAppPopup] = useState(false);
  const [isManuallyClosing, setIsManuallyClosing] = useState(false);
  const [conversationHistory, setConversationHistory] = useState<Array<{
    timestamp: Date;
    type: 'user' | 'SwarAI';
    message: string;
    result?: any;
  }>>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [isMounted, setIsMounted] = useState(false);
  const [showProfileSettings, setShowProfileSettings] = useState(false);
  const [dynamicStats, setDynamicStats] = useState({
    agentCount: 0,
    appLaunchers: 65,
    quickSites: 15,
    systemControls: 11,
  });
  const swiperRef = useRef<HTMLDivElement>(null);

  // Pre-compute particle random values once — prevents recalculation on every render
  const particleData = useMemo(() =>
    Array.from({ length: 25 }, (_, i) => ({
      size: Math.random() * 3 + 1.5,
      startX: Math.random() * 100,
      startY: Math.random() * 100,
      duration: Math.random() * 20 + 12,
      delay: Math.random() * 8,
      yRange: -(60 + Math.random() * 80),
      xRange: Math.sin(i) * 40,
      colorIndex: i % 4,
      glowIndex: i % 3,
    })),
    []
  );

  const { user } = useAuth();

  const {
    backendStatus,
    isProcessing,
    lastResult,
    executeCommand,
    executeWorkflow,
    checkStatus,
    clearResult
  } = useCrewAI();

  const { playSound, speak, stopSpeaking } = useSound();
  const { isListening: voiceListening, startVoiceRecognition } = useVoiceRecognition();

  // Set mounted state for client-side rendering
  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Stop speech on page refresh or unmount
  useEffect(() => {
    const handleBeforeUnload = () => {
      stopSpeaking();
    };

    window.addEventListener('beforeunload', handleBeforeUnload);

    // Cleanup on unmount
    return () => {
      stopSpeaking();
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [stopSpeaking]);

  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  // Fetch dynamic stats from backend
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch('http://localhost:8000/agents');
        if (res.ok) {
          const data = await res.json();
          setDynamicStats(prev => ({
            ...prev,
            agentCount: data.count || prev.agentCount,
          }));
        }
      } catch {
        // Silently fail - keep defaults
      }
    };
    fetchStats();
  }, [backendStatus]);

  // Handle WebSocket results with natural conversation flow
  useEffect(() => {
    if (lastResult && !isProcessing && !isManuallyClosing) {
      console.log('🔄 Processing result naturally:', lastResult);

      // Handle result naturally without intrusive popups
      handleNaturalResult(lastResult);
    }

    // Reset manual closing flag after processing
    if (isManuallyClosing) {
      const timer = setTimeout(() => {
        setIsManuallyClosing(false);
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [lastResult, isProcessing, isManuallyClosing]);

  // Add conversation entry to history
  const addToHistory = (type: 'user' | 'SwarAI', message: string, result?: any) => {
    setConversationHistory(prev => [...prev, {
      timestamp: new Date(),
      type,
      message,
      result
    }]);
  };

  // Handle results with natural conversation flow
  const handleNaturalResult = async (result: any, userCommand?: string) => {
    if (!result) return;

    console.log('🗣️ Natural conversation handling:', result);
    console.log('🔍 Checking WhatsApp conditions:');
    console.log('- result.success:', result.success);
    console.log('- result.agent_used:', result.agent_used);
    console.log('- result.intent:', result.intent);
    console.log('- result.message contains whatsapp:', result.message?.toLowerCase().includes('whatsapp'));
    console.log('- result.whatsapp_url:', result.whatsapp_url);
    console.log('- result.results?.whatsapp_url:', result.results?.whatsapp_url);

    // Add user command to history if provided
    if (userCommand) {
      addToHistory('user', userCommand);
    }

    // Add SwarAI's response to history
    const cleanMessage = result.message
      ?.replace(/[📱📁🔄✅❌🔍💬📄🎤💡]/g, '') // Remove emojis
      ?.replace(/\n/g, ' ') // Replace newlines with spaces
      ?.replace(/\s+/g, ' ') // Normalize whitespace
      ?.trim();

    if (cleanMessage) {
      addToHistory('SwarAI', cleanMessage, result);

      // Create speech-friendly version of the message
      let speechText = cleanMessage;

      // Remove URLs (they sound terrible when spoken)
      speechText = speechText.replace(/https?:\/\/[^\s]+/g, '');

      // Remove file paths (C:\Users\... or /home/... etc.)
      speechText = speechText.replace(/[A-Z]:\\[^\s]+/g, ''); // Windows paths
      speechText = speechText.replace(/\/[^\s]+\/[^\s]+/g, ''); // Unix paths  
      speechText = speechText.replace(/Path: [^\s]+/gi, ''); // "Path: ..." patterns
      speechText = speechText.replace(/� [^\s]+/g, ''); // Remove � symbols with paths

      // Remove technical patterns
      speechText = speechText.replace(/wa\.me\/[^\s]+/g, '');
      speechText = speechText.replace(/\+\d{10,}/g, ''); // Remove phone numbers

      // Remove "Click the link to send:" type instructions
      speechText = speechText.replace(/Click the link to send:/gi, '');
      speechText = speechText.replace(/Click here to/gi, '');
      speechText = speechText.replace(/Open the link/gi, '');

      // For WhatsApp messages, simplify to just the confirmation
      if (result.agent_used === 'whatsapp' && speechText.toLowerCase().includes('whatsapp')) {
        // Extract just the essential part
        const recipientMatch = speechText.match(/ready for (\w+)/i);
        if (recipientMatch) {
          speechText = `WhatsApp message ready for ${recipientMatch[1]}. Opening WhatsApp now.`;
        } else {
          speechText = 'WhatsApp message is ready. Opening WhatsApp now.';
        }
      }

      // For file operations, keep it concise and remove paths
      if (result.agent_used === 'filesearch') {
        // Handle successful file opening
        if (speechText.toLowerCase().includes('successfully opened')) {
          const fileMatch = speechText.match(/Successfully opened: ([^�\s]+)/i);
          if (fileMatch) {
            // Extract just the filename without path
            const fileName = fileMatch[1].split('\\').pop()?.split('/').pop() || fileMatch[1];
            speechText = `Opened ${fileName}`;
          }
        }
        // Handle file not found errors - remove paths
        else if (speechText.toLowerCase().includes('no files found') ||
          speechText.toLowerCase().includes('not found')) {
          speechText = 'File not found. Please try a different search.';
        }
      }

      // Clean up extra whitespace
      speechText = speechText.replace(/\s+/g, ' ').trim();

      // Only speak if there's meaningful content left
      if (speechText && speechText.length > 3) {
        // Smart length limiting based on content type
        let maxLength = 500; // Default: allow longer speeches

        // For technical/action confirmations, keep it short
        if (result.agent_used === 'whatsapp' ||
          result.agent_used === 'filesearch' ||
          result.agent_used === 'email' ||
          result.agent_used === 'payment' ||
          result.agent_used === 'screenshot') {
          maxLength = 100; // Brief confirmations
        }
        // For conversations and information, allow full speech
        else if (result.agent_used === 'conversation' ||
          result.agent_used === 'websearch') {
          maxLength = 2000; // Increased limit for full responses
        }

        const finalSpeech = speechText.length > maxLength
          ? speechText.substring(0, speechText.lastIndexOf('.', maxLength) || maxLength) + '.'
          : speechText;
        speak(finalSpeech);
      }
    }

    // Handle WhatsApp actions naturally (backend already spoke)
    const isRealWhatsAppAction = result.success && (
      (result.agent_used?.toLowerCase().includes('whatsapp') && result.agent_used !== 'conversation') ||
      (result.intent?.toLowerCase().includes('whatsapp') && result.intent !== 'conversation') ||
      result.whatsapp_url ||
      result.results?.whatsapp_url ||
      result.results?.agent_response?.whatsapp_url ||
      (result.message?.toLowerCase().includes('whatsapp') && (
        result.message.includes('wa.me') ||
        result.message.includes('whatsapp.com') ||
        result.message.includes('message prepared') ||
        result.message.includes('ready to send')
      ))
    );

    if (isRealWhatsAppAction) {
      console.log('📱 Genuine WhatsApp action detected! Setting up automatic opening...');
      // Direct WhatsApp opening without popup interruption
      setTimeout(() => {
        console.log('🚀 Executing WhatsApp opening after 1.5s delay...');
        shareToWhatsApp();
      }, 1500); // Brief delay to let SwarAI finish speaking
    } else {
      console.log('⚠️ No genuine WhatsApp action detected. Result type:', result.intent, 'Agent:', result.agent_used);
    }

    // For file operations and other tasks, just add to history
    // Backend TTS already handles speaking

    console.log(`📝 Added to conversation history: "${cleanMessage}"`);
  };

  const handleVoiceStart = async () => {
    if (backendStatus !== 'online') return;

    // Force stop any current speech immediately
    stopSpeaking();
    // Small delay to ensure speech is stopped before starting new recognition
    await new Promise(resolve => setTimeout(resolve, 100));
    playSound('start');

    // Use real voice recognition
    startVoiceRecognition(
      async (transcript: string) => {
        console.log('🎤 Voice transcript received:', transcript);
        addToHistory('user', transcript);

        // Skip "Got it!" for greetings - let the actual response speak
        const isGreeting = /^(hi|hello|hey|good morning|good afternoon|good evening|greetings)/i.test(transcript.trim());
        if (!isGreeting) {
          speak("Got it!");
        }

        playSound('processing');

        // Process the voice command immediately
        console.log('✅ Processing natural command:', transcript);
        await executeCommand(transcript);
      },
      (message: string) => {
        console.log('🎤 Voice system:', message);
        // Voice system feedback - keep minimal
      }
    );
  };

  const handleExampleClick = async (command: string) => {
    // Add to history (no speech - let backend handle it)
    addToHistory('user', command);

    // Execute the command naturally
    console.log('✅ Executing example command:', command);
    await executeCommand(command);
  };

  const shareToWhatsApp = async () => {
    if (!lastResult) return;

    console.log('📱 Attempting to open WhatsApp link from result:', lastResult);

    let whatsappUrl = null;

    // Priority 1: Check direct whatsapp_url field
    if (lastResult.whatsapp_url) {
      whatsappUrl = lastResult.whatsapp_url;
      console.log('✅ Found WhatsApp URL in whatsapp_url field:', whatsappUrl);
    }
    // Priority 2: Check results.whatsapp_url
    else if (lastResult.results?.whatsapp_url) {
      whatsappUrl = lastResult.results.whatsapp_url;
      console.log('✅ Found WhatsApp URL in results.whatsapp_url:', whatsappUrl);
    }
    // Priority 3: Check results.agent_response.whatsapp_url
    else if (lastResult.results?.agent_response?.whatsapp_url) {
      whatsappUrl = lastResult.results.agent_response.whatsapp_url;
      console.log('✅ Found WhatsApp URL in agent_response:', whatsappUrl);
    }
    // Priority 4: Extract from message text
    else if (lastResult.message) {
      const whatsappLinkMatch = lastResult.message.match(/https:\/\/(api\.whatsapp\.com\/send|wa\.me)\/[^\s]+/i);
      if (whatsappLinkMatch) {
        whatsappUrl = whatsappLinkMatch[0];
        console.log('✅ Extracted WhatsApp URL from message:', whatsappUrl);
      }
    }

    // If we found a WhatsApp URL, open it directly
    if (whatsappUrl) {
      console.log('🚀 Opening WhatsApp URL:', whatsappUrl);
      setShowWhatsAppPopup(false);
      window.open(whatsappUrl, '_blank');
      return;
    }

    // Fallback: Try to construct URL from phone and text patterns
    const phoneMatch = lastResult.message?.match(/wa\.me\/([+]?[0-9]+)/);
    const textMatch = lastResult.message?.match(/text=([^&\s]+)/);

    if (phoneMatch && textMatch) {
      const phoneNumber = phoneMatch[1];
      const messageText = decodeURIComponent(textMatch[1]);
      const encodedPhone = encodeURIComponent(phoneNumber.startsWith('+') ? phoneNumber : '+' + phoneNumber);
      const encodedMessage = encodeURIComponent(messageText);
      whatsappUrl = `https://api.whatsapp.com/send/?phone=${encodedPhone}&text=${encodedMessage}&type=phone_number&app_absent=0`;
      console.log('🔧 Constructed WhatsApp URL from parts:', whatsappUrl);
      setShowWhatsAppPopup(false);
      window.open(whatsappUrl, '_blank');
      return;
    }

    // Last resort: Ask backend to extract/generate link - but only if we have a clear WhatsApp message
    if (lastResult.message && (
      lastResult.message.toLowerCase().includes('wa.me') ||
      lastResult.message.toLowerCase().includes('whatsapp.com') ||
      lastResult.message.includes('+') // Likely contains a phone number
    )) {
      console.log('⚠️ No WhatsApp URL found, asking backend for help with potential WhatsApp content');
      try {
        const response = await fetch('http://localhost:8000/process-command', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            command: `Extract WhatsApp link from: ${lastResult.message.substring(0, 200)}` // Limit length
          })
        });

        if (response.ok) {
          const linkResult = await response.json();
          if (linkResult.success && linkResult.results?.whatsapp_url) {
            console.log('✅ Backend provided WhatsApp URL:', linkResult.results.whatsapp_url);
            window.open(linkResult.results.whatsapp_url, '_blank');
          } else {
            console.log('❌ Backend could not extract WhatsApp URL from message');
          }
        }
      } catch (error) {
        console.error('❌ Error asking backend for WhatsApp link:', error);
      }
    } else {
      console.log('❌ No WhatsApp-related content found in message - skipping backend fallback');
    }

    setShowWhatsAppPopup(false);
  };

  const agents = useMemo(() => [
    {
      id: 'whatsapp',
      name: 'WhatsApp Agent',
      description: 'Send messages and create shareable links',
      icon: MessageCircle,
      color: 'from-green-500 to-emerald-600',
      command: 'Try me!',
      examples: [
        'Send WhatsApp to Mom saying hello',
        'Message Jay about the meeting',
        'WhatsApp Sarah good morning'
      ]
    },
    {
      id: 'file_management',
      name: 'File Manager',
      description: 'Search, open, and organize your files',
      icon: FileText,
      color: 'from-blue-500 to-cyan-600',
      command: 'Try me!',
      examples: [
        'Open the latest PDF',
        'Find my project files',
        'Search for resume'
      ]
    },
    {
      id: 'email',
      name: 'Email Agent',
      description: 'Draft and send professional emails',
      icon: Calendar,
      color: 'from-purple-500 to-violet-600',
      command: 'Try me!',
      examples: [
        'Draft email to boss about meeting',
        'Compose email to HR',
        'Email Jay regarding project update'
      ]
    },
    {
      id: 'conversation',
      name: 'Chat Agent',
      description: 'Have natural conversations and get answers',
      icon: Sparkles,
      color: 'from-orange-500 to-red-600',
      command: 'Try me!',
      examples: [
        'Who are you?',
        'Tell me about AI',
        'What can you do?'
      ]
    },
    {
      id: 'phone',
      name: 'Phone Agent',
      description: 'Make calls and dial contacts instantly',
      icon: Phone,
      color: 'from-teal-500 to-green-600',
      command: 'Try me!',
      examples: [
        'Call Mom',
        'Phone Jay',
        'Dial +1234567890'
      ]
    },
    {
      id: 'payment',
      name: 'Payment Agent',
      description: 'Send money via PayPal, UPI or Google Pay',
      icon: CreditCard,
      color: 'from-yellow-500 to-orange-600',
      command: 'Try me!',
      examples: [
        'Pay $50 to John via PayPal',
        'Send 100 rupees via GPay',
        'Transfer money to Jay'
      ]
    },
    {
      id: 'app_launcher',
      name: 'App Launcher',
      description: 'Open any application or program',
      icon: AppWindow,
      color: 'from-indigo-500 to-blue-600',
      command: 'Try me!',
      examples: [
        'Open Chrome',
        'Launch Calculator',
        'Start VS Code'
      ]
    },
    {
      id: 'websearch',
      name: 'Web Search',
      description: 'Search Google, YouTube and the web',
      icon: Globe,
      color: 'from-sky-500 to-blue-600',
      command: 'Try me!',
      examples: [
        'Search for Python tutorials',
        'Google best restaurants near me',
        'YouTube funny cats'
      ]
    },
    {
      id: 'task',
      name: 'Task Manager',
      description: 'Manage to-do lists and reminders',
      icon: ListTodo,
      color: 'from-pink-500 to-rose-600',
      command: 'Try me!',
      examples: [
        'Add task: buy groceries',
        'List my tasks',
        'Complete task 1'
      ]
    },
    {
      id: 'screenshot',
      name: 'Screenshot Agent',
      description: 'Capture and analyze your screen',
      icon: Camera,
      color: 'from-fuchsia-500 to-purple-600',
      command: 'Try me!',
      examples: [
        'Take a screenshot',
        'Capture my screen',
        'Screenshot this'
      ]
    },
    {
      id: 'system_control',
      name: 'System Control',
      description: 'Volume, brightness, battery & power controls',
      icon: Monitor,
      color: 'from-slate-500 to-gray-600',
      command: 'Try me!',
      examples: [
        'Increase volume',
        'Set brightness to 50%',
        'Check battery status'
      ]
    },
  ], []);

  // Swiper scroll handlers
  const scrollSwiper = useCallback((direction: 'left' | 'right') => {
    if (swiperRef.current) {
      // Scroll by one card width (container / 5) + gap
      const containerWidth = swiperRef.current.clientWidth;
      const scrollAmount = Math.round(containerWidth / 5) + 16;
      swiperRef.current.scrollBy({
        left: direction === 'right' ? scrollAmount : -scrollAmount,
        behavior: 'smooth',
      });
    }
  }, []);

  return (
    <ProtectedRoute>
      <div className="min-h-screen p-4 md:p-8 relative overflow-hidden">
        {/* === ENHANCED PROFESSIONAL BACKGROUND === */}
        {/* Base dark gradient */}
        <div className="fixed inset-0 -z-20 bg-[#050508]" />

        {/* Aurora gradient orbs - smooth, slow-moving color blobs */}
        <div className="fixed inset-0 -z-10 overflow-hidden">
          {/* Primary orb - blue/indigo */}
          <div
            className="absolute w-[600px] h-[600px] rounded-full opacity-[0.12] blur-[120px]"
            style={{
              background: 'radial-gradient(circle, #6366f1 0%, #4f46e5 40%, transparent 70%)',
              top: '-10%',
              left: '10%',
              animation: 'aurora 20s ease-in-out infinite',
              willChange: 'transform',
              transform: 'translateZ(0)',
            }}
          />
          {/* Secondary orb - purple/violet */}
          <div
            className="absolute w-[500px] h-[500px] rounded-full opacity-[0.10] blur-[100px]"
            style={{
              background: 'radial-gradient(circle, #a855f7 0%, #7c3aed 40%, transparent 70%)',
              bottom: '0%',
              right: '5%',
              animation: 'aurora2 25s ease-in-out infinite',
              willChange: 'transform',
              transform: 'translateZ(0)',
            }}
          />
          {/* Tertiary orb - cyan/teal subtle accent */}
          <div
            className="absolute w-[400px] h-[400px] rounded-full opacity-[0.06] blur-[80px]"
            style={{
              background: 'radial-gradient(circle, #06b6d4 0%, #0891b2 40%, transparent 70%)',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%) translateZ(0)',
              animation: 'aurora3 18s ease-in-out infinite',
              willChange: 'transform',
            }}
          />

          {/* Extra orb 1 - rose/pink, bottom-left */}
          <div
            className="absolute w-[450px] h-[450px] rounded-full opacity-[0.09] blur-[110px]"
            style={{
              background: 'radial-gradient(circle, #f43f5e 0%, #e11d48 40%, transparent 70%)',
              bottom: '20%',
              left: '-5%',
              animation: 'aurora4 22s ease-in-out infinite',
              willChange: 'transform',
              transform: 'translateZ(0)',
            }}
          />
          {/* Extra orb 2 - emerald/green, top-right */}
          <div
            className="absolute w-[350px] h-[350px] rounded-full opacity-[0.07] blur-[90px]"
            style={{
              background: 'radial-gradient(circle, #10b981 0%, #059669 40%, transparent 70%)',
              top: '10%',
              right: '20%',
              animation: 'aurora5 28s ease-in-out infinite',
              willChange: 'transform',
              transform: 'translateZ(0)',
            }}
          />
          {/* Extra orb 3 - amber/warm, center-right */}
          <div
            className="absolute w-[500px] h-[500px] rounded-full opacity-[0.06] blur-[100px]"
            style={{
              background: 'radial-gradient(circle, #f59e0b 0%, #d97706 40%, transparent 70%)',
              top: '60%',
              right: '-10%',
              animation: 'aurora6 24s ease-in-out infinite',
              willChange: 'transform',
              transform: 'translateZ(0)',
            }}
          />
          {/* Extra orb 4 - sky/blue, bottom-center */}
          <div
            className="absolute w-[550px] h-[550px] rounded-full opacity-[0.08] blur-[130px]"
            style={{
              background: 'radial-gradient(circle, #38bdf8 0%, #0284c7 40%, transparent 70%)',
              bottom: '-15%',
              left: '35%',
              animation: 'aurora7 30s ease-in-out infinite',
              willChange: 'transform',
              transform: 'translateZ(0)',
            }}
          />
        </div>

        {/* Noise texture */}
        <div className="noise-overlay" />

        {/* Cursor-following glow effect */}
        {isMounted && (
          <CursorGlow />
        )}

        {/* Floating particles - pre-computed for performance */}
        <div className="fixed inset-0 overflow-hidden -z-10">
          {isMounted && particleData.map((p, i) => (
            <motion.div
              key={i}
              className="absolute rounded-full"
              style={{
                width: p.size,
                height: p.size,
                left: `${p.startX}%`,
                top: `${p.startY}%`,
                background: p.colorIndex === 0
                  ? 'rgba(99, 102, 241, 0.6)'
                  : p.colorIndex === 1
                    ? 'rgba(168, 85, 247, 0.5)'
                    : p.colorIndex === 2
                      ? 'rgba(6, 182, 212, 0.4)'
                      : 'rgba(255, 255, 255, 0.35)',
                boxShadow: p.glowIndex === 0 ? `0 0 ${p.size * 3}px rgba(99, 102, 241, 0.3)` : 'none',
                willChange: 'transform, opacity',
              }}
              animate={{
                y: [0, p.yRange, 0],
                x: [0, p.xRange, 0],
                opacity: [0, 0.9, 0],
                scale: [0.5, 1.2, 0.5],
              }}
              transition={{
                duration: p.duration,
                repeat: Infinity,
                delay: p.delay,
                ease: 'easeInOut',
              }}
            />
          ))}
        </div>

      {/* Header */}
      <motion.header
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex justify-between items-center mb-6"
      >
        <div className="flex items-center space-x-4">
          <motion.div
            whileHover={{ scale: 1.05 }}
            transition={{ duration: 0.3 }}
            className="w-32 h-32 flex items-center justify-center overflow-hidden"
          >
            <img
              src="/swarai_logo.png"
              alt="SwarAI Logo"
              className="w-full h-full object-contain"
            />
          </motion.div>

          <div>
            <h1 className="text-3xl font-bold text-white">SwarAI</h1>
            <p className="text-gray-400 text-sm tracking-wider">Multi-Agent AI System</p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <StatusIndicator
            status={backendStatus}
            label="Backend"
          />
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setShowHistory(true)}
            className="glass p-3 rounded-xl text-white hover:bg-white/20 transition-all relative cursor-pointer"
            title="View conversation history"
          >
            <History className="w-6 h-6" />
            {conversationHistory.length > 0 && (
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-blue-500 rounded-full" />
            )}
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setShowProfileSettings(true)}
            className="glass p-3 rounded-xl hover:bg-white/20 transition-all cursor-pointer"
            title="Profile & Settings"
          >
            <div className="w-6 h-6 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
              {user?.profilePicture ? (
                <img
                  src={user.profilePicture}
                  alt={user.name}
                  className="w-full h-full rounded-full object-cover"
                />
              ) : (
                <User className="w-4 h-4 text-white" />
              )}
            </div>
          </motion.button>
        </div>
      </motion.header>

      {/* Main Voice Interface */}
      <motion.section
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="text-center mb-12"
      >
        <motion.div
          className="relative mx-auto mb-8"
          style={{ width: 'fit-content' }}
        >
          {/* Orbital rings */}
          {!voiceListening && !isProcessing && (
            <>
              <motion.div
                className="absolute inset-0 w-48 h-48 rounded-full border-2 border-blue-400/30"
                style={{ left: '50%', top: '50%', x: '-50%', y: '-50%' }}
                animate={{ rotate: 360, scale: [1, 1.1, 1] }}
                transition={{ rotate: { duration: 8, repeat: Infinity, ease: "linear" }, scale: { duration: 3, repeat: Infinity } }}
              />
              <motion.div
                className="absolute inset-0 w-56 h-56 rounded-full border-2 border-purple-400/20"
                style={{ left: '50%', top: '50%', x: '-50%', y: '-50%' }}
                animate={{ rotate: -360, scale: [1, 1.15, 1] }}
                transition={{ rotate: { duration: 12, repeat: Infinity, ease: "linear" }, scale: { duration: 4, repeat: Infinity } }}
              />
              <motion.div
                className="absolute inset-0 w-64 h-64 rounded-full border border-cyan-400/10"
                style={{ left: '50%', top: '50%', x: '-50%', y: '-50%' }}
                animate={{ rotate: 360, scale: [1, 1.2, 1] }}
                transition={{ rotate: { duration: 15, repeat: Infinity, ease: "linear" }, scale: { duration: 5, repeat: Infinity } }}
              />
            </>
          )}

          {/* Floating particles */}
          {!voiceListening && !isProcessing && isMounted && [...Array(8)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-2 h-2 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full"
              style={{
                left: '50%',
                top: '50%',
              }}
              animate={{
                x: [0, Math.cos(i * Math.PI / 4) * 120],
                y: [0, Math.sin(i * Math.PI / 4) * 120],
                opacity: [0, 1, 0],
                scale: [0, 1, 0],
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                delay: i * 0.2,
                ease: "easeOut"
              }}
            />
          ))}

          {/* Pulsing glow effect */}
          <motion.div
            className="absolute inset-0 w-48 h-48 rounded-full blur-2xl"
            style={{ left: '50%', top: '50%', x: '-50%', y: '-50%' }}
            animate={{
              background: [
                'radial-gradient(circle, rgba(59,130,246,0.4) 0%, transparent 70%)',
                'radial-gradient(circle, rgba(168,85,247,0.4) 0%, transparent 70%)',
                'radial-gradient(circle, rgba(59,130,246,0.4) 0%, transparent 70%)',
              ],
              scale: [1, 1.2, 1],
            }}
            transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
          />

          <motion.button
            onClick={handleVoiceStart}
            disabled={backendStatus !== 'online' || voiceListening || isProcessing}
            className={`
              relative w-48 h-48 rounded-full transition-all duration-500 transform overflow-hidden
              ${voiceListening
                ? 'bg-gradient-to-br from-red-500 via-pink-500 to-red-600 shadow-2xl shadow-red-500/50'
                : isProcessing
                  ? 'bg-gradient-to-br from-yellow-400 via-orange-500 to-yellow-600 shadow-2xl shadow-yellow-500/50'
                  : 'bg-gradient-to-br from-blue-500 via-purple-600 to-indigo-700 shadow-2xl shadow-blue-500/50'
              }
              disabled:opacity-50 disabled:cursor-not-allowed
              cursor-pointer
            `}
            whileHover={{ 
              scale: backendStatus === 'online' ? 1.08 : 1,
              rotate: [0, -2, 2, -2, 0],
              transition: { rotate: { duration: 0.5 } }
            }}
            whileTap={{ scale: backendStatus === 'online' ? 0.92 : 1 }}
            animate={{
              boxShadow: voiceListening 
                ? [
                    '0 0 30px rgba(239, 68, 68, 0.5)',
                    '0 0 50px rgba(239, 68, 68, 0.8)',
                    '0 0 30px rgba(239, 68, 68, 0.5)',
                  ]
                : isProcessing
                  ? [
                      '0 0 30px rgba(234, 179, 8, 0.5)',
                      '0 0 50px rgba(234, 179, 8, 0.8)',
                      '0 0 30px rgba(234, 179, 8, 0.5)',
                    ]
                  : [
                      '0 0 30px rgba(59, 130, 246, 0.5)',
                      '0 0 50px rgba(168, 85, 247, 0.5)',
                      '0 0 30px rgba(59, 130, 246, 0.5)',
                    ]
            }}
            transition={{ boxShadow: { duration: 2, repeat: Infinity } }}
          >
            {/* Animated background gradient */}
            <motion.div
              className="absolute inset-0 opacity-50"
              animate={{
                background: [
                  'radial-gradient(circle at 20% 50%, rgba(255,255,255,0.2) 0%, transparent 50%)',
                  'radial-gradient(circle at 80% 50%, rgba(255,255,255,0.2) 0%, transparent 50%)',
                  'radial-gradient(circle at 20% 50%, rgba(255,255,255,0.2) 0%, transparent 50%)',
                ],
              }}
              transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
            />

            <div className="absolute inset-3 rounded-full bg-white/10 backdrop-blur-sm flex items-center justify-center border border-white/20">
              <AnimatePresence mode="wait">
                {voiceListening ? (
                  <motion.div
                    key="listening"
                    initial={{ opacity: 0, scale: 0.5, rotate: -180 }}
                    animate={{ opacity: 1, scale: 1, rotate: 0 }}
                    exit={{ opacity: 0, scale: 0.5, rotate: 180 }}
                    className="flex flex-col items-center"
                    transition={{ type: "spring", damping: 15 }}
                  >
                    <motion.div
                      animate={{ 
                        scale: [1, 1.2, 1],
                      }}
                      transition={{ duration: 0.8, repeat: Infinity }}
                    >
                      <Mic className="w-16 h-16 text-white drop-shadow-lg" />
                    </motion.div>
                    <motion.span 
                      className="text-white text-sm font-bold mt-2"
                      animate={{ opacity: [0.5, 1, 0.5] }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                    >
                      Listening...
                    </motion.span>
                  </motion.div>
                ) : isProcessing ? (
                  <motion.div
                    key="processing"
                    initial={{ opacity: 0, scale: 0.5 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.5 }}
                    className="flex flex-col items-center"
                  >
                    <motion.div
                      animate={{ 
                        rotate: 360,
                        scale: [1, 1.1, 1]
                      }}
                      transition={{ 
                        rotate: { duration: 2, repeat: Infinity, ease: "linear" },
                        scale: { duration: 1, repeat: Infinity }
                      }}
                    >
                      <Zap className="w-16 h-16 text-white drop-shadow-lg" />
                    </motion.div>
                    <span className="text-white text-sm font-bold mt-2">Processing...</span>
                  </motion.div>
                ) : (
                  <motion.div
                    key="ready"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className="flex flex-col items-center"
                    transition={{ type: "spring", damping: 10 }}
                  >
                    <motion.div
                      animate={{ 
                        y: [0, -8, 0],
                      }}
                      transition={{ 
                        duration: 2,
                        repeat: Infinity,
                        ease: "easeInOut"
                      }}
                    >
                      <Mic className="w-16 h-16 text-white drop-shadow-lg" />
                    </motion.div>
                    <motion.span 
                      className="text-white text-lg font-bold mt-2 tracking-wider"
                      animate={{
                        textShadow: [
                          '0 0 10px rgba(255,255,255,0.5)',
                          '0 0 20px rgba(255,255,255,0.8)',
                          '0 0 10px rgba(255,255,255,0.5)',
                        ]
                      }}
                      transition={{ duration: 2, repeat: Infinity }}
                    >
                      TAP TO SPEAK
                    </motion.span>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Multiple ripple effects */}
            {(voiceListening || isProcessing) && (
              <>
                <motion.div
                  className="absolute inset-0 rounded-full border-4 border-white/60"
                  animate={{
                    scale: [1, 1.3],
                    opacity: [0.6, 0]
                  }}
                  transition={{
                    duration: 1.5,
                    repeat: Infinity,
                    ease: "easeOut"
                  }}
                />
                <motion.div
                  className="absolute inset-0 rounded-full border-4 border-white/40"
                  animate={{
                    scale: [1, 1.5],
                    opacity: [0.4, 0]
                  }}
                  transition={{
                    duration: 1.5,
                    repeat: Infinity,
                    ease: "easeOut",
                    delay: 0.5
                  }}
                />
                <motion.div
                  className="absolute inset-0 rounded-full border-2 border-white/20"
                  animate={{
                    scale: [1, 1.8],
                    opacity: [0.2, 0]
                  }}
                  transition={{
                    duration: 1.5,
                    repeat: Infinity,
                    ease: "easeOut",
                    delay: 1
                  }}
                />
              </>
            )}
          </motion.button>

          {/* Voice Visualization */}
          <VoiceVisualization isActive={voiceListening} />
        </motion.div>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="text-lg text-gray-400 mt-14 mb-4 tracking-wide"
        >
          Speak naturally or choose an agent below
        </motion.p>

        {backendStatus !== 'online' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center px-4 py-2 bg-red-500/20 border border-red-500/30 rounded-lg text-red-400"
          >
            <WifiOff className="w-5 h-5 mr-2" />
            Backend Offline - Please start the SwarAI backend server
          </motion.div>
        )}
      </motion.section>

      {/* Agent Cards - Horizontal Swiper */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="mb-12 mt-16"
      >
        <div className="flex items-center justify-center gap-4 mb-8">
          <div className="glow-line flex-1 max-w-[120px]" />
          <h2 className="text-2xl font-bold text-white text-center tracking-wide">Specialized Agents</h2>
          <div className="glow-line flex-1 max-w-[120px]" />
        </div>

        {/* Swiper container with navigation */}
        <div className="relative group/swiper">
          {/* Left arrow */}
          <button
            onClick={() => scrollSwiper('left')}
            className="absolute left-0 top-1/2 -translate-y-1/2 z-20 w-10 h-10 rounded-full bg-white/10 backdrop-blur-sm border border-white/10 flex items-center justify-center text-white opacity-0 group-hover/swiper:opacity-100 transition-opacity duration-300 hover:bg-white/20 cursor-pointer -ml-2"
            aria-label="Scroll left"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>

          {/* Right arrow */}
          <button
            onClick={() => scrollSwiper('right')}
            className="absolute right-0 top-1/2 -translate-y-1/2 z-20 w-10 h-10 rounded-full bg-white/10 backdrop-blur-sm border border-white/10 flex items-center justify-center text-white opacity-0 group-hover/swiper:opacity-100 transition-opacity duration-300 hover:bg-white/20 cursor-pointer -mr-2"
            aria-label="Scroll right"
          >
            <ChevronRight className="w-5 h-5" />
          </button>

          {/* Wider fade edges for smooth card disappearing */}
          <div className="absolute left-0 top-0 bottom-0 w-20 bg-gradient-to-r from-[#050508] via-[#050508]/80 to-transparent z-10 pointer-events-none" />
          <div className="absolute right-0 top-0 bottom-0 w-20 bg-gradient-to-l from-[#050508] via-[#050508]/80 to-transparent z-10 pointer-events-none" />

          {/* Scrollable cards — 5 visible at a time, no duplication */}
          <div
            ref={swiperRef}
            className="flex gap-4 overflow-x-auto scrollbar-hide pb-2 px-10 snap-x snap-mandatory"
            style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
          >
            {agents.map((agent, index) => (
              <div
                key={agent.id}
                className="snap-start"
                style={{ flex: '0 0 calc((100% - 4 * 1rem) / 5)' }}
              >
                <AgentCard
                  agent={agent}
                  isActive={currentAgent === agent.id}
                  isDisabled={backendStatus !== 'online'}
                  onExampleClick={handleExampleClick}
                  delay={Math.min(index, 4) * 0.1}
                />
              </div>
            ))}
          </div>
        </div>
      </motion.section>

      {/* === INTERACTIVE STATS SECTION === */}
      <motion.section
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="mb-12"
      >
        <div className="glow-line mb-10" />
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
          {[
            { value: `${dynamicStats.agentCount || '13'}+`, label: 'AI Agents', icon: '🤖', color: 'from-blue-500/20 to-indigo-500/20' },
            { value: `${dynamicStats.appLaunchers}+`, label: 'App Launchers', icon: '🚀', color: 'from-purple-500/20 to-violet-500/20' },
            { value: `${dynamicStats.quickSites}+`, label: 'Quick Access Sites', icon: '🌐', color: 'from-cyan-500/20 to-teal-500/20' },
            { value: `${dynamicStats.systemControls}`, label: 'System Controls', icon: '⚙️', color: 'from-orange-500/20 to-amber-500/20' },
          ].map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7 + index * 0.1 }}
              whileHover={{ scale: 1.05, y: -4 }}
              className="stat-card rounded-2xl p-5 text-center cursor-default"
            >
              <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${stat.color} flex items-center justify-center mx-auto mb-3 text-lg`}>
                {stat.icon}
              </div>
              <motion.div
                className="text-2xl font-bold text-white mb-1"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.9 + index * 0.1 }}
              >
                {stat.value}
              </motion.div>
              <div className="text-xs text-gray-400 font-medium uppercase tracking-wider">{stat.label}</div>
            </motion.div>
          ))}
        </div>
      </motion.section>

      {/* === TECH STACK MARQUEE === */}
      <motion.section
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.9 }}
        className="mb-8 overflow-hidden relative"
      >
        <div className="absolute left-0 top-0 bottom-0 w-24 bg-gradient-to-r from-[#050508] to-transparent z-10" />
        <div className="absolute right-0 top-0 bottom-0 w-24 bg-gradient-to-l from-[#050508] to-transparent z-10" />
        <div className="flex animate-marquee whitespace-nowrap py-3">
          {[...Array(2)].map((_, setIndex) => (
            <div key={setIndex} className="flex items-center gap-8 mr-8">
              {[
                'CrewAI', 'LangChain', 'Groq LLM', 'FastAPI', 'Next.js', 'WebSocket',
                'Voice Recognition', 'Whisper AI', 'MongoDB', 'JWT Auth', 'Real-time Processing',
                'Multi-Agent System', 'Smart Intent Detection', 'TTS Engine'
              ].map((tech) => (
                <span
                  key={`${setIndex}-${tech}`}
                  className="text-[11px] font-medium text-gray-500 tracking-widest uppercase px-4 py-1.5 rounded-full border border-white/[0.06] bg-white/[0.02] flex-shrink-0"
                >
                  {tech}
                </span>
              ))}
            </div>
          ))}
        </div>
      </motion.section>

      {/* History Modal */}
      <AnimatePresence>
        {showHistory && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            onClick={() => setShowHistory(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.9, opacity: 0, y: 20 }}
              transition={{ type: "spring", duration: 0.5 }}
              className="bg-[#0d0d14] border border-white/10 rounded-2xl p-6 max-w-2xl w-full max-h-[80vh] mx-4 shadow-2xl shadow-black/50 relative overflow-hidden"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                    <History className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-white">Conversation History</h3>
                    <p className="text-sm text-gray-400">{conversationHistory.length} interactions</p>
                  </div>
                </div>
                <button
                  onClick={() => setShowHistory(false)}
                  className="text-gray-400 hover:text-gray-200 transition-colors p-2 rounded-full hover:bg-white/10"
                  aria-label="Close conversation history"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Conversation History */}
              <div className="overflow-y-auto max-h-96 space-y-4">
                {conversationHistory.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <Bot className="w-12 h-12 mx-auto mb-3 text-gray-600" />
                    <p className="text-gray-400">No conversations yet. Start talking to SwarAI!</p>
                  </div>
                ) : (
                  conversationHistory.map((entry, index) => (
                    <div key={index} className={`flex ${entry.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-2xl ${entry.type === 'user'
                        ? 'bg-blue-500/80 text-white'
                        : 'bg-white/5 border border-white/10 text-gray-200'
                        }`}>
                        <div className="flex items-center space-x-2 mb-1">
                          {entry.type === 'user' ? (
                            <div className="w-4 h-4 bg-white/20 rounded-full" />
                          ) : (
                            <Bot className="w-4 h-4" />
                          )}
                          <span className="text-xs opacity-75">
                            {entry.type === 'user' ? 'You' : 'SwarAI'}
                          </span>
                          <span className="text-xs opacity-50">
                            {entry.timestamp.toLocaleTimeString()}
                          </span>
                        </div>
                        <p className="text-sm">{entry.message}</p>
                        {entry.result?.agent_used && (
                          <div className="mt-1 text-xs opacity-75">
                            via {entry.result.agent_used} agent
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>

              {/* Actions */}
              <div className="mt-6 flex justify-end space-x-3">
                <button
                  onClick={() => {
                    setConversationHistory([]);
                    setShowHistory(false);
                  }}
                  className="px-4 py-2 text-gray-400 hover:text-gray-200 transition-colors"
                >
                  Clear History
                </button>
                <button
                  onClick={() => setShowHistory(false)}
                  className="px-6 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 border border-white/10 transition-colors"
                >
                  Close
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* WhatsApp Popup */}
      <AnimatePresence>
        {showWhatsAppPopup && lastResult && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            onClick={(e) => {
              e.preventDefault();
              setShowWhatsAppPopup(false);
            }}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.9, opacity: 0, y: 20 }}
              transition={{ type: "spring", duration: 0.5 }}
              className="bg-[#0d0d14] border border-white/10 rounded-2xl p-6 max-w-md w-full mx-4 shadow-2xl shadow-black/50 relative"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Close button */}
              <button
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  setShowWhatsAppPopup(false);
                }}
                className="absolute top-4 right-4 text-gray-400 hover:text-gray-200 transition-colors p-1 rounded-full hover:bg-white/10"
                aria-label="Close popup"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>

              <div className="text-center">
                <div className="mx-auto flex items-center justify-center w-16 h-16 rounded-full bg-green-500/20 mb-4">
                  <MessageCircle className="w-8 h-8 text-green-400" />
                </div>

                <h3 className="text-xl font-semibold text-white mb-2">
                  WhatsApp Message Ready!
                </h3>

                {lastResult.agent_used && (
                  <div className="mb-3 px-3 py-1 bg-blue-500/20 text-blue-300 text-sm rounded-full inline-block">
                    🤖 {lastResult.agent_used} Agent
                  </div>
                )}

                <p className="text-sm text-gray-400 mb-6 leading-relaxed">
                  Your WhatsApp message has been processed successfully. Click below to open WhatsApp and send your message.
                </p>

                {lastResult.message && (
                  <div className="mb-6 p-3 bg-white/5 border border-white/10 rounded-lg text-left">
                    <p className="text-xs text-gray-500 mb-1">Message Details:</p>
                    <p className="text-sm text-gray-300 line-clamp-3">{lastResult.message}</p>
                  </div>
                )}

                <div className="flex space-x-3">
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      setShowWhatsAppPopup(false);
                    }}
                    className="flex-1 px-4 py-3 text-gray-300 bg-white/10 hover:bg-white/20 rounded-lg transition-colors font-medium cursor-pointer"
                  >
                    Not Now
                  </button>
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      shareToWhatsApp();
                    }}
                    className="flex-1 px-4 py-3 text-white bg-green-600 hover:bg-green-700 rounded-lg transition-colors font-medium flex items-center justify-center space-x-2 cursor-pointer"
                  >
                    <MessageCircle className="w-4 h-4" />
                    <span>Open WhatsApp</span>
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Profile Settings Modal */}
      <ProfileSettings
        isOpen={showProfileSettings}
        onClose={() => setShowProfileSettings(false)}
      />
    </div>
    </ProtectedRoute>
  );
}
