'use client';

import { Bot, Sparkles } from 'lucide-react';

interface HeaderProps {
  backendStatus: 'online' | 'offline' | 'checking';
}

export default function Header({ backendStatus }: HeaderProps) {
  return (
    <header className="text-center py-8">
      <div className="flex items-center justify-center mb-4">
        <div className="relative">
          <Bot className="w-16 h-16 text-blue-600 animate-bounce" />
          <Sparkles className="w-6 h-6 text-yellow-500 absolute -top-2 -right-2 animate-spin" />
        </div>
      </div>
      <h1 className="text-4xl font-bold text-gray-800 mb-2">AI Assistant</h1>
      <p className="text-xl text-gray-600">Just speak or tap to get help!</p>
      
      {/* Status Indicator */}
      <div className="flex items-center justify-center mt-4">
        <div className={`w-4 h-4 rounded-full mr-3 ${
          backendStatus === 'online' ? 'bg-green-500 animate-pulse' :
          backendStatus === 'offline' ? 'bg-red-500' : 'bg-yellow-500 animate-spin'
        }`} />
        <span className="text-lg font-medium text-gray-700">
          {backendStatus === 'online' ? '✅ Ready to Help' :
           backendStatus === 'offline' ? '❌ Connection Issue' : '🔄 Connecting...'}
        </span>
      </div>
    </header>
  );
}