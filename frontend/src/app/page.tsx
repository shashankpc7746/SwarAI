'use client';

import { useState, useEffect } from 'react';
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
  X
} from 'lucide-react';
import useVoiceRecognition from '@/hooks/useVoiceRecognition';
import { useCrewAI } from '@/hooks/useCrewAI';
import { useSound } from '@/hooks/useSound';
import { VoiceVisualization } from '@/components/VoiceVisualization';
import { AgentCard } from '@/components/AgentCard';
import { ResultDisplay } from '@/components/ResultDisplay';
import { StatusIndicator } from '@/components/StatusIndicator';

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

  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 10000);
    return () => clearInterval(interval);
  }, []);

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

    // Stop any current speech and play start sound
    stopSpeaking();
    playSound('start');

    // Use real voice recognition
    startVoiceRecognition(
      async (transcript: string) => {
        console.log('🎤 Voice transcript received:', transcript);
        addToHistory('user', transcript);

        // Immediate acknowledgment - brief and natural
        speak("Got it!");

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

  const handleAgentSelect = async (agentType: string, command: string) => {
    setCurrentAgent(agentType);

    // Add to history and acknowledge
    addToHistory('user', command);
    speak("I'll help you with that right away.");

    const result = await executeWorkflow(agentType, { command });
    if (result) {
      handleNaturalResult(result, command);
    }
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

  const agents = [
    {
      id: 'whatsapp',
      name: 'WhatsApp Agent',
      description: 'Send messages and create shareable links',
      icon: MessageCircle,
      color: 'from-green-500 to-emerald-600',
      command: 'Send WhatsApp message'
    },
    {
      id: 'file_management',
      name: 'File Manager',
      description: 'Search, open, and organize your files',
      icon: FileText,
      color: 'from-blue-500 to-cyan-600',
      command: 'Find and manage files'
    },
    {
      id: 'calendar',
      name: 'Calendar Agent',
      description: 'Schedule events and set reminders',
      icon: Calendar,
      color: 'from-purple-500 to-violet-600',
      command: 'Schedule appointment'
    },
    {
      id: 'research',
      name: 'Research Agent',
      description: 'Find information and conduct research',
      icon: Sparkles,
      color: 'from-orange-500 to-red-600',
      command: 'Research information'
    }
  ];

  return (
    <div className="min-h-screen p-4 md:p-8">
      {/* Header */}
      <motion.header
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex justify-between items-center mb-8"
      >
        <div className="flex items-center space-x-4">
          <motion.div
            whileHover={{ scale: 1.05 }}
            transition={{ duration: 0.3 }}
            className="w-16 h-16 rounded-2xl flex items-center justify-center overflow-hidden bg-white/10 backdrop-blur-sm p-1"
          >
            <img
              src="/swarai_logo.png"
              alt="SwarAI Logo"
              className="w-full h-full object-contain rounded-xl"
            />
          </motion.div>
          <div>
            <h1 className="text-3xl font-bold text-white">SwarAI</h1>
            <p className="text-gray-300">Multi-Agent AI System</p>
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
            className="glass p-3 rounded-xl text-white hover:bg-white/20 transition-all relative"
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
            className="glass p-3 rounded-xl text-white hover:bg-white/20 transition-all"
          >
            <Settings className="w-6 h-6" />
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
          <motion.button
            onClick={handleVoiceStart}
            disabled={backendStatus !== 'online' || voiceListening || isProcessing}
            className={`
              relative w-48 h-48 rounded-full transition-all duration-300 transform
              ${voiceListening
                ? 'bg-red-500 shadow-2xl scale-110 animate-pulse'
                : isProcessing
                  ? 'bg-yellow-500 shadow-xl animate-bounce'
                  : 'bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 shadow-xl hover:shadow-2xl hover:scale-105'
              }
              disabled:opacity-50 disabled:cursor-not-allowed
              glass-strong voice-ripple ${voiceListening ? 'active' : ''}
            `}
            whileHover={{ scale: backendStatus === 'online' ? 1.05 : 1 }}
            whileTap={{ scale: backendStatus === 'online' ? 0.95 : 1 }}
          >
            <div className="absolute inset-4 rounded-full bg-white/20 flex items-center justify-center">
              <AnimatePresence mode="wait">
                {voiceListening ? (
                  <motion.div
                    key="listening"
                    initial={{ opacity: 0, scale: 0.5 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.5 }}
                    className="flex flex-col items-center"
                  >
                    <Mic className="w-16 h-16 text-white animate-pulse" />
                    <span className="text-white text-sm font-bold mt-2">Listening...</span>
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
                      animate={{ rotate: 360 }}
                      transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                    >
                      <Zap className="w-16 h-16 text-white" />
                    </motion.div>
                    <span className="text-white text-sm font-bold mt-2">Processing...</span>
                  </motion.div>
                ) : (
                  <motion.div
                    key="ready"
                    initial={{ opacity: 0, scale: 0.5 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.5 }}
                    className="flex flex-col items-center"
                  >
                    <Mic className="w-16 h-16 text-white group-hover:scale-110 transition-transform" />
                    <span className="text-white text-lg font-bold mt-2">TAP TO SPEAK</span>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Ripple effect */}
            {(voiceListening || isProcessing) && (
              <motion.div
                className="absolute inset-0 rounded-full border-4 border-white"
                animate={{
                  scale: [1, 1.2, 1],
                  opacity: [0.8, 0, 0.8]
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              />
            )}
          </motion.button>

          {/* Voice Visualization */}
          <VoiceVisualization isActive={voiceListening} />
        </motion.div>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="text-xl text-gray-300 mb-4"
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

      {/* Agent Cards */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="mb-12"
      >
        <h2 className="text-2xl font-bold text-white text-center mb-8">Specialized Agents</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {agents.map((agent, index) => (
            <AgentCard
              key={agent.id}
              agent={agent}
              isActive={currentAgent === agent.id}
              isDisabled={backendStatus !== 'online'}
              onClick={() => handleAgentSelect(agent.id, agent.command)}
              delay={index * 0.1}
            />
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
              className="bg-white rounded-2xl p-6 max-w-2xl w-full max-h-[80vh] mx-4 shadow-2xl relative overflow-hidden"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                    <History className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">Conversation History</h3>
                    <p className="text-sm text-gray-500">{conversationHistory.length} interactions</p>
                  </div>
                </div>
                <button
                  onClick={() => setShowHistory(false)}
                  className="text-gray-400 hover:text-gray-600 transition-colors p-2 rounded-full hover:bg-gray-100"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Conversation History */}
              <div className="overflow-y-auto max-h-96 space-y-4">
                {conversationHistory.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <Bot className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                    <p>No conversations yet. Start talking to SwarAI!</p>
                  </div>
                ) : (
                  conversationHistory.map((entry, index) => (
                    <div key={index} className={`flex ${entry.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-2xl ${entry.type === 'user'
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-100 text-gray-900'
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
                  className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
                >
                  Clear History
                </button>
                <button
                  onClick={() => setShowHistory(false)}
                  className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
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
              className="bg-white rounded-2xl p-6 max-w-md w-full mx-4 shadow-2xl relative"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Close button */}
              <button
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  setShowWhatsAppPopup(false);
                }}
                className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors p-1 rounded-full hover:bg-gray-100"
                aria-label="Close popup"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>

              <div className="text-center">
                <div className="mx-auto flex items-center justify-center w-16 h-16 rounded-full bg-green-100 mb-4">
                  <MessageCircle className="w-8 h-8 text-green-600" />
                </div>

                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  WhatsApp Message Ready!
                </h3>

                {lastResult.agent_used && (
                  <div className="mb-3 px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full inline-block">
                    🤖 {lastResult.agent_used} Agent
                  </div>
                )}

                <p className="text-sm text-gray-600 mb-6 leading-relaxed">
                  Your WhatsApp message has been processed successfully. Click below to open WhatsApp and send your message.
                </p>

                {lastResult.message && (
                  <div className="mb-6 p-3 bg-gray-50 rounded-lg text-left">
                    <p className="text-xs text-gray-500 mb-1">Message Details:</p>
                    <p className="text-sm text-gray-700 line-clamp-3">{lastResult.message}</p>
                  </div>
                )}

                <div className="flex space-x-3">
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      setShowWhatsAppPopup(false);
                    }}
                    className="flex-1 px-4 py-3 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors font-medium"
                  >
                    Not Now
                  </button>
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      shareToWhatsApp();
                    }}
                    className="flex-1 px-4 py-3 text-white bg-green-600 hover:bg-green-700 rounded-lg transition-colors font-medium flex items-center justify-center space-x-2"
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
    </div>
  );
}
