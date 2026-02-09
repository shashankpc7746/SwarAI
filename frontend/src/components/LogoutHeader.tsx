'use client';

import { motion } from 'framer-motion';
import { LogOut, User } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

export function LogoutHeader() {
  const { user, logout } = useAuth();

  if (!user) return null;

  return (
    <motion.div
      className="absolute top-4 right-4 z-40"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5 }}
    >
      <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl px-4 py-2 flex items-center gap-3">
        {/* User Info */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
            {user.profilePicture ? (
              <img
                src={user.profilePicture}
                alt={user.name}
                className="w-full h-full rounded-full object-cover"
              />
            ) : (
              <User className="w-4 h-4 text-white" />
            )}
          </div>
          <div className="text-sm">
            <p className="text-white font-medium">{user.name}</p>
            <p className="text-gray-400 text-xs">{user.email}</p>
          </div>
        </div>

        {/* Logout Button */}
        <motion.button
          onClick={logout}
          className="p-2 hover:bg-white/10 rounded-lg transition-colors"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          title="Logout"
        >
          <LogOut className="w-4 h-4 text-white" />
        </motion.button>
      </div>
    </motion.div>
  );
}
