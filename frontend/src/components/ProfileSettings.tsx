'use client';

import { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X,
  User,
  Mail,
  Calendar,
  Camera,
  Volume2,
  Zap,
  Gauge,
  Mic2,
  Moon,
  Sun,
  Layout,
  Save,
  Settings as SettingsIcon,
  LogOut
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

interface ProfileSettingsProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ProfileSettings({ isOpen, onClose }: ProfileSettingsProps) {
  const { user, logout } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);

  // User Profile Section State
  const [profileData, setProfileData] = useState({
    firstName: user?.name?.split(' ')[0] || '',
    lastName: user?.name?.split(' ').slice(1).join(' ') || '',
    email: user?.email || '',
    age: user?.age || '',
    profilePicture: user?.profilePicture || '',
  });

  // Voice Settings State
  const [voiceSettings, setVoiceSettings] = useState({
    voiceType: 'female', // 'male', 'female'
    accent: 'american', // 'american', 'british', 'australian', 'indian'
    speed: 1.0, // 0.5 to 2.0
    volume: 0.8, // 0 to 1
    pitch: 1.0, // 0.5 to 2.0
  });

  // UI Settings State
  const [uiSettings, setUiSettings] = useState({
    theme: 'dark', // 'dark', 'light'
    layout: 'modern', // 'modern', 'compact', 'classic'
    animations: true,
    soundEffects: true,
  });

  const [activeSection, setActiveSection] = useState<'profile' | 'voice' | 'ui'>('profile');
  const [isUploading, setIsUploading] = useState(false);

  const handleProfilePictureClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    // Simulate upload - replace with actual upload logic
    const reader = new FileReader();
    reader.onloadend = () => {
      setProfileData({ ...profileData, profilePicture: reader.result as string });
      setIsUploading(false);
    };
    reader.readAsDataURL(file);
  };

  const handleSaveProfile = () => {
    // TODO: Implement save profile logic
    console.log('Saving profile:', profileData);
    alert('Profile saved successfully!');
  };

  const handleSaveVoiceSettings = () => {
    // TODO: Implement save voice settings logic
    console.log('Saving voice settings:', voiceSettings);
    alert('Voice settings saved successfully!');
  };

  const handleSaveUISettings = () => {
    // TODO: Implement save UI settings logic
    console.log('Saving UI settings:', uiSettings);
    alert('UI settings saved successfully!');
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/60 backdrop-blur-md flex items-center justify-center z-50 p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0, y: 20 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.9, opacity: 0, y: 20 }}
          transition={{ type: "spring", duration: 0.5 }}
          className="bg-gradient-to-br from-gray-900 to-black border border-white/20 rounded-3xl p-6 max-w-4xl w-full max-h-[90vh] overflow-hidden shadow-2xl"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between mb-6 pb-4 border-b border-white/10">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                <SettingsIcon className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">Settings</h2>
                <p className="text-sm text-gray-400">Manage your preferences</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <motion.button
                onClick={() => {
                  logout();
                  onClose();
                }}
                className="text-gray-400 hover:text-red-400 transition-colors p-2 rounded-full hover:bg-white/10 flex items-center gap-2"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                title="Logout"
              >
                <LogOut className="w-5 h-5" />
                <span className="text-sm font-medium">Logout</span>
              </motion.button>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-white transition-colors p-2 rounded-full hover:bg-white/10"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 mb-6">
            <button
              onClick={() => setActiveSection('profile')}
              className={`flex-1 py-3 px-4 rounded-xl font-medium transition-all ${
                activeSection === 'profile'
                  ? 'bg-white text-black'
                  : 'bg-white/5 text-gray-400 hover:bg-white/10'
              }`}
            >
              <User className="w-4 h-4 inline mr-2" />
              Profile
            </button>
            <button
              onClick={() => setActiveSection('voice')}
              className={`flex-1 py-3 px-4 rounded-xl font-medium transition-all ${
                activeSection === 'voice'
                  ? 'bg-white text-black'
                  : 'bg-white/5 text-gray-400 hover:bg-white/10'
              }`}
            >
              <Mic2 className="w-4 h-4 inline mr-2" />
              Voice
            </button>
            <button
              onClick={() => setActiveSection('ui')}
              className={`flex-1 py-3 px-4 rounded-xl font-medium transition-all ${
                activeSection === 'ui'
                  ? 'bg-white text-black'
                  : 'bg-white/5 text-gray-400 hover:bg-white/10'
              }`}
            >
              <Layout className="w-4 h-4 inline mr-2" />
              Interface
            </button>
          </div>

          {/* Content Area */}
          <div className="overflow-y-auto max-h-[60vh] pr-2">
            {/* Profile Section */}
            {activeSection === 'profile' && (
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="space-y-6"
              >
                {/* Profile Picture */}
                <div className="flex flex-col items-center mb-6">
                  <div className="relative">
                    <div className="w-32 h-32 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center overflow-hidden border-4 border-white/20">
                      {profileData.profilePicture ? (
                        <img
                          src={profileData.profilePicture}
                          alt="Profile"
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <User className="w-16 h-16 text-white" />
                      )}
                    </div>
                    <button
                      onClick={handleProfilePictureClick}
                      disabled={isUploading}
                      className="absolute bottom-0 right-0 w-10 h-10 bg-white rounded-full flex items-center justify-center shadow-lg hover:bg-gray-200 transition-all disabled:opacity-50"
                    >
                      {isUploading ? (
                        <motion.div
                          animate={{ rotate: 360 }}
                          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                          className="w-5 h-5 border-2 border-black border-t-transparent rounded-full"
                        />
                      ) : (
                        <Camera className="w-5 h-5 text-black" />
                      )}
                    </button>
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="image/*"
                      onChange={handleFileChange}
                      className="hidden"
                    />
                  </div>
                  <p className="text-gray-400 text-sm mt-2">Click camera to change picture</p>
                </div>

                {/* First Name */}
                <div>
                  <label className="block text-white text-sm font-medium mb-2">
                    First Name
                  </label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="text"
                      value={profileData.firstName}
                      onChange={(e) =>
                        setProfileData({ ...profileData, firstName: e.target.value })
                      }
                      className="w-full bg-white/10 border border-white/20 rounded-xl pl-11 pr-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-white/50 transition-all"
                      placeholder="Enter first name"
                    />
                  </div>
                </div>

                {/* Last Name */}
                <div>
                  <label className="block text-white text-sm font-medium mb-2">
                    Last Name
                  </label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="text"
                      value={profileData.lastName}
                      onChange={(e) =>
                        setProfileData({ ...profileData, lastName: e.target.value })
                      }
                      className="w-full bg-white/10 border border-white/20 rounded-xl pl-11 pr-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-white/50 transition-all"
                      placeholder="Enter last name"
                    />
                  </div>
                </div>

                {/* Email */}
                <div>
                  <label className="block text-white text-sm font-medium mb-2">
                    Email
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="email"
                      value={profileData.email}
                      onChange={(e) =>
                        setProfileData({ ...profileData, email: e.target.value })
                      }
                      className="w-full bg-white/10 border border-white/20 rounded-xl pl-11 pr-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-white/50 transition-all"
                      placeholder="your.email@gmail.com"
                    />
                  </div>
                </div>

                {/* Age */}
                <div>
                  <label className="block text-white text-sm font-medium mb-2">
                    Age
                  </label>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="number"
                      value={profileData.age}
                      onChange={(e) =>
                        setProfileData({ ...profileData, age: e.target.value })
                      }
                      className="w-full bg-white/10 border border-white/20 rounded-xl pl-11 pr-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-white/50 transition-all"
                      placeholder="Enter your age"
                      min="13"
                      max="120"
                    />
                  </div>
                </div>

                {/* Save Button */}
                <button
                  onClick={handleSaveProfile}
                  className="w-full bg-white text-black font-semibold py-3 rounded-xl hover:bg-gray-200 transition-all flex items-center justify-center gap-2"
                >
                  <Save className="w-5 h-5" />
                  Save Profile
                </button>
              </motion.div>
            )}

            {/* Voice Settings Section */}
            {activeSection === 'voice' && (
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="space-y-6"
              >
                {/* Voice Type */}
                <div>
                  <label className="block text-white text-sm font-medium mb-3">
                    Voice Type
                  </label>
                  <div className="grid grid-cols-2 gap-3">
                    <button
                      onClick={() =>
                        setVoiceSettings({ ...voiceSettings, voiceType: 'male' })
                      }
                      className={`py-3 px-4 rounded-xl font-medium transition-all ${
                        voiceSettings.voiceType === 'male'
                          ? 'bg-white text-black'
                          : 'bg-white/5 text-gray-400 hover:bg-white/10'
                      }`}
                    >
                      Male Voice
                    </button>
                    <button
                      onClick={() =>
                        setVoiceSettings({ ...voiceSettings, voiceType: 'female' })
                      }
                      className={`py-3 px-4 rounded-xl font-medium transition-all ${
                        voiceSettings.voiceType === 'female'
                          ? 'bg-white text-black'
                          : 'bg-white/5 text-gray-400 hover:bg-white/10'
                      }`}
                    >
                      Female Voice
                    </button>
                  </div>
                </div>

                {/* Accent */}
                <div>
                  <label className="block text-white text-sm font-medium mb-3">
                    Accent
                  </label>
                  <div className="grid grid-cols-2 gap-3">
                    {['american', 'british', 'australian', 'indian'].map((accent) => (
                      <button
                        key={accent}
                        onClick={() =>
                          setVoiceSettings({ ...voiceSettings, accent })
                        }
                        className={`py-3 px-4 rounded-xl font-medium transition-all capitalize ${
                          voiceSettings.accent === accent
                            ? 'bg-white text-black'
                            : 'bg-white/5 text-gray-400 hover:bg-white/10'
                        }`}
                      >
                        {accent}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Speed */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-white text-sm font-medium flex items-center gap-2">
                      <Gauge className="w-4 h-4" />
                      Speech Speed
                    </label>
                    <span className="text-white text-sm">{voiceSettings.speed.toFixed(1)}x</span>
                  </div>
                  <input
                    type="range"
                    min="0.5"
                    max="2.0"
                    step="0.1"
                    value={voiceSettings.speed}
                    onChange={(e) =>
                      setVoiceSettings({
                        ...voiceSettings,
                        speed: parseFloat(e.target.value),
                      })
                    }
                    className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer slider"
                  />
                  <div className="flex justify-between text-xs text-gray-400 mt-1">
                    <span>Slower</span>
                    <span>Faster</span>
                  </div>
                </div>

                {/* Volume */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-white text-sm font-medium flex items-center gap-2">
                      <Volume2 className="w-4 h-4" />
                      Volume
                    </label>
                    <span className="text-white text-sm">{Math.round(voiceSettings.volume * 100)}%</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={voiceSettings.volume}
                    onChange={(e) =>
                      setVoiceSettings({
                        ...voiceSettings,
                        volume: parseFloat(e.target.value),
                      })
                    }
                    className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer slider"
                  />
                  <div className="flex justify-between text-xs text-gray-400 mt-1">
                    <span>Quiet</span>
                    <span>Loud</span>
                  </div>
                </div>

                {/* Pitch */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-white text-sm font-medium flex items-center gap-2">
                      <Zap className="w-4 h-4" />
                      Pitch
                    </label>
                    <span className="text-white text-sm">{voiceSettings.pitch.toFixed(1)}</span>
                  </div>
                  <input
                    type="range"
                    min="0.5"
                    max="2.0"
                    step="0.1"
                    value={voiceSettings.pitch}
                    onChange={(e) =>
                      setVoiceSettings({
                        ...voiceSettings,
                        pitch: parseFloat(e.target.value),
                      })
                    }
                    className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer slider"
                  />
                  <div className="flex justify-between text-xs text-gray-400 mt-1">
                    <span>Lower</span>
                    <span>Higher</span>
                  </div>
                </div>

                {/* Test Voice Button */}
                <button
                  onClick={() => {
                    // TODO: Test voice with current settings
                    console.log('Testing voice:', voiceSettings);
                    alert('Voice test (feature coming soon)');
                  }}
                  className="w-full bg-purple-600 text-white font-semibold py-3 rounded-xl hover:bg-purple-700 transition-all flex items-center justify-center gap-2"
                >
                  <Mic2 className="w-5 h-5" />
                  Test Voice
                </button>

                {/* Save Button */}
                <button
                  onClick={handleSaveVoiceSettings}
                  className="w-full bg-white text-black font-semibold py-3 rounded-xl hover:bg-gray-200 transition-all flex items-center justify-center gap-2"
                >
                  <Save className="w-5 h-5" />
                  Save Voice Settings
                </button>
              </motion.div>
            )}

            {/* UI Settings Section */}
            {activeSection === 'ui' && (
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="space-y-6"
              >
                {/* Theme */}
                <div>
                  <label className="block text-white text-sm font-medium mb-3">
                    Theme
                  </label>
                  <div className="grid grid-cols-2 gap-3">
                    <button
                      onClick={() =>
                        setUiSettings({ ...uiSettings, theme: 'dark' })
                      }
                      className={`py-3 px-4 rounded-xl font-medium transition-all flex items-center justify-center gap-2 ${
                        uiSettings.theme === 'dark'
                          ? 'bg-white text-black'
                          : 'bg-white/5 text-gray-400 hover:bg-white/10'
                      }`}
                    >
                      <Moon className="w-4 h-4" />
                      Dark Mode
                    </button>
                    <button
                      onClick={() =>
                        setUiSettings({ ...uiSettings, theme: 'light' })
                      }
                      className={`py-3 px-4 rounded-xl font-medium transition-all flex items-center justify-center gap-2 ${
                        uiSettings.theme === 'light'
                          ? 'bg-white text-black'
                          : 'bg-white/5 text-gray-400 hover:bg-white/10'
                      }`}
                    >
                      <Sun className="w-4 h-4" />
                      Light Mode
                    </button>
                  </div>
                  <p className="text-gray-400 text-xs mt-2">Note: Light mode coming soon!</p>
                </div>

                {/* Layout */}
                <div>
                  <label className="block text-white text-sm font-medium mb-3">
                    Layout Style
                  </label>
                  <div className="grid grid-cols-3 gap-3">
                    {['modern', 'compact', 'classic'].map((layout) => (
                      <button
                        key={layout}
                        onClick={() =>
                          setUiSettings({ ...uiSettings, layout })
                        }
                        className={`py-3 px-4 rounded-xl font-medium transition-all capitalize ${
                          uiSettings.layout === layout
                            ? 'bg-white text-black'
                            : 'bg-white/5 text-gray-400 hover:bg-white/10'
                        }`}
                      >
                        {layout}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Animations Toggle */}
                <div className="flex items-center justify-between bg-white/5 p-4 rounded-xl">
                  <div>
                    <p className="text-white font-medium">Animations</p>
                    <p className="text-gray-400 text-sm">Enable smooth transitions and effects</p>
                  </div>
                  <button
                    onClick={() =>
                      setUiSettings({ ...uiSettings, animations: !uiSettings.animations })
                    }
                    className={`relative w-14 h-8 rounded-full transition-colors ${
                      uiSettings.animations ? 'bg-green-500' : 'bg-gray-600'
                    }`}
                  >
                    <motion.div
                      className="absolute top-1 w-6 h-6 bg-white rounded-full"
                      animate={{ x: uiSettings.animations ? 28 : 4 }}
                      transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                    />
                  </button>
                </div>

                {/* Sound Effects Toggle */}
                <div className="flex items-center justify-between bg-white/5 p-4 rounded-xl">
                  <div>
                    <p className="text-white font-medium">Sound Effects</p>
                    <p className="text-gray-400 text-sm">Play sounds for interactions</p>
                  </div>
                  <button
                    onClick={() =>
                      setUiSettings({ ...uiSettings, soundEffects: !uiSettings.soundEffects })
                    }
                    className={`relative w-14 h-8 rounded-full transition-colors ${
                      uiSettings.soundEffects ? 'bg-green-500' : 'bg-gray-600'
                    }`}
                  >
                    <motion.div
                      className="absolute top-1 w-6 h-6 bg-white rounded-full"
                      animate={{ x: uiSettings.soundEffects ? 28 : 4 }}
                      transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                    />
                  </button>
                </div>

                {/* Save Button */}
                <button
                  onClick={handleSaveUISettings}
                  className="w-full bg-white text-black font-semibold py-3 rounded-xl hover:bg-gray-200 transition-all flex items-center justify-center gap-2"
                >
                  <Save className="w-5 h-5" />
                  Save UI Settings
                </button>
              </motion.div>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
