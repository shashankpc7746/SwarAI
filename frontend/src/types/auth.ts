/**
 * Authentication Types for SwarAI
 */

export interface User {
  id: string;
  name: string;
  email: string;
  age: number;
  profilePicture?: string;
  createdAt: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface LoginCredentials {
  name: string;
  email: string;
  age: number;
}

export interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  loginWithGoogle: () => Promise<void>;
  logout: () => void;
}
