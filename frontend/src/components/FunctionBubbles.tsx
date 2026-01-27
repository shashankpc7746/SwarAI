'use client';

import { MessageCircle, Phone, Calendar, FileText } from 'lucide-react';

export type BubbleType = 'whatsapp' | 'call' | 'calendar' | 'files' | null;

interface FunctionBubblesProps {
  onBubbleClick: (type: BubbleType, agentName: string) => void;
}

export default function FunctionBubbles({ onBubbleClick }: FunctionBubblesProps) {
  return (
    <div className="grid grid-cols-2 gap-8 mb-8 w-full max-w-4xl">
      {/* WhatsApp Bubble */}
      <div 
        onClick={() => onBubbleClick('whatsapp', 'WhatsApp')}
        className="group cursor-pointer transform transition-all duration-300 hover:scale-110 hover:-translate-y-2"
      >
        <div className="bg-white rounded-3xl shadow-xl p-8 text-center border-4 border-green-200 group-hover:border-green-400 group-hover:shadow-2xl">
          <div className="relative mb-4">
            <MessageCircle className="w-16 h-16 text-green-500 mx-auto group-hover:animate-bounce" />
            <div className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 rounded-full animate-pulse" />
          </div>
          <h3 className="text-2xl font-bold text-gray-800 mb-2">Send Message</h3>
          <p className="text-gray-600 text-lg">Tap to send WhatsApp</p>
        </div>
      </div>

      {/* Call Bubble */}
      <div 
        onClick={() => onBubbleClick('call', 'Phone')}
        className="group cursor-pointer transform transition-all duration-300 hover:scale-110 hover:-translate-y-2"
      >
        <div className="bg-white rounded-3xl shadow-xl p-8 text-center border-4 border-blue-200 group-hover:border-blue-400 group-hover:shadow-2xl">
          <div className="relative mb-4">
            <Phone className="w-16 h-16 text-blue-500 mx-auto group-hover:animate-bounce" />
            <div className="absolute -top-2 -right-2 w-6 h-6 bg-green-500 rounded-full animate-pulse" />
          </div>
          <h3 className="text-2xl font-bold text-gray-800 mb-2">Make Call</h3>
          <p className="text-gray-600 text-lg">Tap to call someone</p>
        </div>
      </div>

      {/* Calendar Bubble */}
      <div 
        onClick={() => onBubbleClick('calendar', 'Calendar')}
        className="group cursor-pointer transform transition-all duration-300 hover:scale-110 hover:-translate-y-2"
      >
        <div className="bg-white rounded-3xl shadow-xl p-8 text-center border-4 border-purple-200 group-hover:border-purple-400 group-hover:shadow-2xl">
          <div className="relative mb-4">
            <Calendar className="w-16 h-16 text-purple-500 mx-auto group-hover:animate-bounce" />
            <div className="absolute -top-2 -right-2 w-6 h-6 bg-orange-500 rounded-full animate-pulse" />
          </div>
          <h3 className="text-2xl font-bold text-gray-800 mb-2">Reminders</h3>
          <p className="text-gray-600 text-lg">Tap to set reminders</p>
        </div>
      </div>

      {/* Files Bubble */}
      <div 
        onClick={() => onBubbleClick('files', 'Files')}
        className="group cursor-pointer transform transition-all duration-300 hover:scale-110 hover:-translate-y-2"
      >
        <div className="bg-white rounded-3xl shadow-xl p-8 text-center border-4 border-orange-200 group-hover:border-orange-400 group-hover:shadow-2xl">
          <div className="relative mb-4">
            <FileText className="w-16 h-16 text-orange-500 mx-auto group-hover:animate-bounce" />
            <div className="absolute -top-2 -right-2 w-6 h-6 bg-blue-500 rounded-full animate-pulse" />
          </div>
          <h3 className="text-2xl font-bold text-gray-800 mb-2">My Files</h3>
          <p className="text-gray-600 text-lg">Tap to open files</p>
        </div>
      </div>
    </div>
  );
}