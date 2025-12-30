import React, { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { login as authLogin, logout as authLogout, getStoredToken, setStoredToken, removeStoredToken } from './authService';
import type { User } from './authService';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const checkAuth = () => {
    const storedToken = getStoredToken();
    
    if (storedToken) {
      setToken(storedToken);
      // In a real app, you would validate the token with the backend
      // For now, we'll consider the user authenticated if token exists
      // The user data should be fetched from the backend or decoded from token
      setIsLoading(false);
    } else {
      setToken(null);
      setUser(null);
      setIsLoading(false);
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  const login = async (username: string, password: string): Promise<void> => {
    try {
      setIsLoading(true);
      const response = await authLogin({ username, password });
      
      // Store token
      setStoredToken(response.access_token);
      setToken(response.access_token);
      setUser(response.user);
    } catch (error) {
      // Re-throw error to be handled by the component
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async (): Promise<void> => {
    try {
      setIsLoading(true);
      await authLogout();
    } catch (error) {
      console.error('Error during logout:', error);
    } finally {
      // Always clear local state
      removeStoredToken();
      setToken(null);
      setUser(null);
      setIsLoading(false);
    }
  };

  const isAuthenticated = !!token && !!user;

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated,
    isLoading,
    login,
    logout,
    checkAuth,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
