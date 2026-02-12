'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, AuthState, AuthContextType, LoginCredentials } from '@/types/auth';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
  });

  // Check for existing session on mount
  useEffect(() => {
    const checkAuth = () => {
      const storedUser = localStorage.getItem('swarai_user');
      const token = localStorage.getItem('swarai_token');

      if (storedUser && token) {
        try {
          const user = JSON.parse(storedUser);
          setAuthState({
            user,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          console.error('Failed to parse stored user:', error);
          localStorage.removeItem('swarai_user');
          localStorage.removeItem('swarai_token');
          setAuthState({
            user: null,
            isAuthenticated: false,
            isLoading: false,
          });
        }
      } else {
        setAuthState({
          user: null,
          isAuthenticated: false,
          isLoading: false,
        });
      }
    };

    checkAuth();
  }, []);

  const login = async (credentials: LoginCredentials) => {
    try {
      // Call backend API to authenticate
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      if (!response.ok) {
        throw new Error('Login failed');
      }

      const data = await response.json();
      const user: User = data.user;
      const token = data.token;

      // Store user and token
      localStorage.setItem('swarai_user', JSON.stringify(user));
      localStorage.setItem('swarai_token', token);

      setAuthState({
        user,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const loginWithGoogle = async (credentialResponse: any) => {
    try {
      console.log('🔐 Starting Google login process...');
      console.log('📝 Credential received:', credentialResponse.credential ? 'Yes' : 'No');
      
      // Send Google credential to backend for verification
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
      
      try {
        console.log('📡 Sending request to backend...');
        const response = await fetch('http://localhost:8000/api/auth/google', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            credential: credentialResponse.credential,
          }),
          signal: controller.signal,
        });

        clearTimeout(timeoutId);
        console.log('📡 Backend response status:', response.status);

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
          console.error('❌ Backend error:', errorData);
          throw new Error(errorData.detail || 'Google login failed');
        }

        const data = await response.json();
        console.log('✅ Login successful! User:', data.user?.name, data.user?.email);
        
        const user: User = data.user;
        const token = data.token;

        // Store user and token
        localStorage.setItem('swarai_user', JSON.stringify(user));
        localStorage.setItem('swarai_token', token);

        setAuthState({
          user,
          isAuthenticated: true,
          isLoading: false,
        });

        console.log('🎉 Redirecting to main page...');
        // Redirect to main page
        window.location.href = '/';
      } catch (fetchError: any) {
        clearTimeout(timeoutId);
        if (fetchError.name === 'AbortError') {
          console.error('❌ Request timeout - Backend not responding');
          throw new Error('Request timeout. Please check if backend is running.');
        }
        throw fetchError;
      }
    } catch (error: any) {
      console.error('❌ Google login error:', error);
      console.error('Error details:', error.message);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('swarai_user');
    localStorage.removeItem('swarai_token');
    setAuthState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
    });
  };

  return (
    <AuthContext.Provider
      value={{
        ...authState,
        login,
        loginWithGoogle,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
