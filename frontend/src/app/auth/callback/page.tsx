'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { motion } from 'framer-motion';
import { Loader2, AlertCircle, Sparkles } from 'lucide-react';

export default function AuthCallback() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);
  const [showThankYou, setShowThankYou] = useState(false);

  useEffect(() => {
    const handleCallback = async () => {
      // Get token from URL parameters (set by backend redirect)
      const token = searchParams.get('token');
      const userJson = searchParams.get('user');

      if (token && userJson) {
        try {
          const user = JSON.parse(decodeURIComponent(userJson));
          
          // Store in localStorage
          localStorage.setItem('swarai_token', token);
          localStorage.setItem('swarai_user', JSON.stringify(user));

          // Show thank you message
          setShowThankYou(true);

          // Redirect to main page after 3 seconds
          setTimeout(() => {
            router.push('/');
          }, 3000);
        } catch (err) {
          console.error('Failed to process auth callback:', err);
          setError('Failed to complete authentication');
        }
      } else {
        setError('Invalid authentication response');
      }
    };

    handleCallback();
  }, [searchParams, router]);

  if (error) {
    return (
      <div className="min-h-screen w-full bg-black flex items-center justify-center">
        <motion.div
          className="text-center"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">Authentication Failed</h2>
          <p className="text-gray-400 mb-4">{error}</p>
          <button
            onClick={() => router.push('/login')}
            className="px-6 py-3 bg-white text-black rounded-lg hover:bg-gray-200 transition-colors"
          >
            Return to Login
          </button>
        </motion.div>
      </div>
    );
  }

  // Show thank you message
  if (showThankYou) {
    return (
      <div className="min-h-screen w-full bg-black flex items-center justify-center">
        <motion.div
          className="text-center"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          <Sparkles className="w-16 h-16 text-white mx-auto mb-4" />
          <h2 className="text-5xl font-bold text-white mb-4">Thank You!</h2>
          <p className="text-xl text-gray-400">Launching Swar AI...</p>
          
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
      </div>
    );
  }

  // Loading state
  return (
    <div className="min-h-screen w-full bg-black flex items-center justify-center">
      <motion.div
        className="text-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <Loader2 className="w-16 h-16 text-white animate-spin mx-auto mb-4" />
        <p className="text-white text-xl">Completing authentication...</p>
      </motion.div>
    </div>
  );
}
