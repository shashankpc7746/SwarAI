'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Mail, User, Calendar } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { GoogleLogin } from '@react-oauth/google';

export default function LoginPage() {
  const [showIntro, setShowIntro] = useState(true);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    age: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showThankYou, setShowThankYou] = useState(false);
  const [errors, setErrors] = useState<{
    name?: string;
    email?: string;
    age?: string;
  }>({});
  const [isMounted, setIsMounted] = useState(false);

  const { login, loginWithGoogle } = useAuth();
  const router = useRouter();

  // Set mounted state on client side
  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Hide intro after 3 seconds
  useEffect(() => {
    const timer = setTimeout(() => {
      setShowIntro(false);
    }, 3000);
    return () => clearTimeout(timer);
  }, []);

  const validateForm = () => {
    const newErrors: typeof errors = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    } else if (formData.name.trim().length < 2) {
      newErrors.name = 'Name must be at least 2 characters';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email';
    }

    if (!formData.age) {
      newErrors.age = 'Age is required';
    } else if (parseInt(formData.age) < 13 || parseInt(formData.age) > 120) {
      newErrors.age = 'Age must be between 13 and 120';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      await login({
        name: formData.name,
        email: formData.email,
        age: parseInt(formData.age),
      });

      // Show thank you message before redirecting
      setShowThankYou(true);
      setTimeout(() => {
        router.push('/');
      }, 2000);
    } catch (error) {
      console.error('Login failed:', error);
      setErrors({ email: 'Login failed. Please try again.' });
      setIsSubmitting(false);
    }
  };

  const handleGoogleSuccess = async (credentialResponse: any) => {
    try {
      console.log('🎯 Google Sign-In successful, processing...');
      await loginWithGoogle(credentialResponse);
    } catch (error: any) {
      console.error('❌ Google Sign-In failed:', error);
      const errorMessage = error?.message || 'Google Sign-In failed. Please try again.';
      setErrors({ email: errorMessage });
    }
  };

  const handleGoogleError = () => {
    console.error('❌ Google Sign-In error - User cancelled or error occurred');
    setErrors({ email: 'Google Sign-In was cancelled or failed. Please try again.' });
  };

  return (
    <div className="min-h-screen w-full bg-black flex items-center justify-center overflow-hidden">
      {/* Animated background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-black via-gray-900 to-black">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-gray-700 via-gray-900 to-black opacity-50" />
      </div>

      {/* Floating particles */}
      <div className="absolute inset-0 overflow-hidden">
        {isMounted && [...Array(20)].map((_, i) => {
          const randomX = Math.random() * window.innerWidth;
          const randomY = Math.random() * window.innerHeight;
          const randomOpacity = Math.random() * 0.5;
          const randomDuration = Math.random() * 10 + 10;
          const randomTargetY = Math.random() * window.innerHeight;
          const randomTargetOpacity = Math.random() * 0.5;

          return (
            <motion.div
              key={i}
              className="absolute w-1 h-1 bg-white rounded-full"
              initial={{
                x: randomX,
                y: randomY,
                opacity: randomOpacity,
              }}
              animate={{
                y: [null, randomTargetY],
                opacity: [null, randomTargetOpacity, 0],
              }}
              transition={{
                duration: randomDuration,
                repeat: Infinity,
                ease: 'linear',
              }}
            />
          );
        })}
      </div>

      <AnimatePresence mode="wait">
        {showIntro ? (
          // Intro Animation
          <motion.div
            key="intro"
            className="relative z-10 text-center"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.2 }}
            transition={{ duration: 1 }}
          >
            <motion.div
              className="flex items-center justify-center gap-4"
              animate={{
                y: [0, -10, 0],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
            >
              <Sparkles className="w-12 h-12 text-white" />
              <h1 className="text-6xl md:text-8xl font-bold text-white">
                Welcome to{' '}
                <span className="bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
                  Swar AI
                </span>
              </h1>
              <Sparkles className="w-12 h-12 text-white" />
            </motion.div>

            {/* Loading dots */}
            <div className="flex justify-center gap-2 mt-8">
              {[0, 1, 2].map((i) => (
                <motion.div
                  key={i}
                  className="w-3 h-3 bg-white rounded-full"
                  animate={{
                    scale: [1, 1.5, 1],
                    opacity: [0.3, 1, 0.3],
                  }}
                  transition={{
                    duration: 1.5,
                    repeat: Infinity,
                    delay: i * 0.2,
                  }}
                />
              ))}
            </div>
          </motion.div>
        ) : showThankYou ? (
          // Thank You Message
          <motion.div
            key="thankyou"
            className="relative z-10 text-center"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Sparkles className="w-16 h-16 text-white mx-auto mb-4" />
            <h2 className="text-5xl font-bold text-white mb-4">Thank You!</h2>
            <p className="text-xl text-gray-400">Launching Swar AI...</p>
          </motion.div>
        ) : (
          // Login Form
          <motion.div
            key="login"
            className="relative z-10 w-full max-w-md px-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            {/* Login Card */}
            <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-2xl">
              {/* Logo/Title */}
              <div className="text-center mb-8">
                <motion.h2
                  className="text-4xl font-bold text-white mb-2"
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                >
                  Swar AI
                </motion.h2>
                <motion.p
                  className="text-gray-400"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.3 }}
                >
                  Your Intelligent Voice Assistant
                </motion.p>
              </div>

              {/* Login Form */}
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Name Field */}
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4 }}
                >
                  <label className="block text-white text-sm font-medium mb-2">
                    Name
                  </label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) =>
                        setFormData({ ...formData, name: e.target.value })
                      }
                      className="w-full bg-white/10 border border-white/20 rounded-xl pl-11 pr-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-white/50 transition-all"
                      placeholder="Enter your name"
                    />
                  </div>
                  {errors.name && (
                    <p className="text-red-400 text-sm mt-1">{errors.name}</p>
                  )}
                </motion.div>

                {/* Email Field */}
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 }}
                >
                  <label className="block text-white text-sm font-medium mb-2">
                    Gmail
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) =>
                        setFormData({ ...formData, email: e.target.value })
                      }
                      className="w-full bg-white/10 border border-white/20 rounded-xl pl-11 pr-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-white/50 transition-all"
                      placeholder="your.email@gmail.com"
                    />
                  </div>
                  {errors.email && (
                    <p className="text-red-400 text-sm mt-1">{errors.email}</p>
                  )}
                </motion.div>

                {/* Age Field */}
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.6 }}
                >
                  <label className="block text-white text-sm font-medium mb-2">
                    Age
                  </label>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="number"
                      value={formData.age}
                      onChange={(e) =>
                        setFormData({ ...formData, age: e.target.value })
                      }
                      className="w-full bg-white/10 border border-white/20 rounded-xl pl-11 pr-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-white/50 transition-all"
                      placeholder="Enter your age"
                      min="13"
                      max="120"
                    />
                  </div>
                  {errors.age && (
                    <p className="text-red-400 text-sm mt-1">{errors.age}</p>
                  )}
                </motion.div>

                {/* Submit Button */}
                <motion.button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full bg-white text-black font-semibold py-3 rounded-xl hover:bg-gray-200 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.7 }}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {isSubmitting ? 'Signing In...' : 'Sign In'}
                </motion.button>

                {/* Divider */}
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-white/20" />
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-2 bg-transparent text-gray-400">Or</span>
                  </div>
                </div>

                {/* Google Sign In Button */}
                <motion.div
                  className="w-full"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.8 }}
                >
                  <div className="w-full [&>div]:w-full [&>div>div]:!w-full">
                    <GoogleLogin
                      onSuccess={handleGoogleSuccess}
                      onError={handleGoogleError}
                      theme="filled_black"
                      size="large"
                      text="signin_with"
                      shape="rectangular"
                      width="100%"
                    />
                  </div>
                </motion.div>
              </form>

              {/* Thank You Note */}
              <motion.p
                className="text-center text-gray-500 text-sm mt-6"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.9 }}
              >
                Thank you for choosing Swar AI
              </motion.p>
            </div>

            {/* Footer */}
            <motion.div
              className="text-center mt-6 text-gray-500 text-sm"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1 }}
            >
              By signing in, you agree to our terms and conditions
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
