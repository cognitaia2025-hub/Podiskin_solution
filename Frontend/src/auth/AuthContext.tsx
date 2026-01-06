import React, { createContext, useContext, useState, useEffect, useCallback, useRef, type ReactNode } from 'react';
import { login as authLogin, logout as authLogout, getStoredToken, setStoredToken, removeStoredToken, refreshToken as refreshAuthToken, verifyToken } from './authService';
import type { User } from './authService';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string, rememberMe?: boolean) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => void;
  refreshToken: () => Promise<void>;
  updateUser: (userData: Partial<User>) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Export AuthContext for direct access
export { AuthContext };

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const refreshTimerRef = useRef<number | null>(null);

  // Clear refresh timer
  const clearRefreshTimer = useCallback(() => {
    if (refreshTimerRef.current) {
      window.clearTimeout(refreshTimerRef.current);
      refreshTimerRef.current = null;
    }
  }, []);

  // Refresh token function
  const refreshToken = useCallback(async (): Promise<void> => {
    try {
      console.log('[AuthContext] Refreshing token...');
      const response = await refreshAuthToken();
      
      setStoredToken(response.access_token);
      setToken(response.access_token);
      
      console.log('[AuthContext] Token refreshed successfully');
    } catch (error) {
      console.error('[AuthContext] Failed to refresh token:', error);
      // If refresh fails, logout user
      await logout();
    }
  }, []);

  // Setup auto-refresh timer (every 25 minutes, token expires in 30)
  const setupAutoRefresh = useCallback(() => {
    clearRefreshTimer();
    
    // Refresh token every 25 minutes (1500000 ms)
    const REFRESH_INTERVAL = 25 * 60 * 1000;
    
    refreshTimerRef.current = window.setTimeout(async () => {
      await refreshToken();
      setupAutoRefresh(); // Setup next refresh
    }, REFRESH_INTERVAL);
    
    console.log('[AuthContext] Auto-refresh scheduled in 25 minutes');
  }, [clearRefreshTimer, refreshToken]);

  // Update user data
  const updateUser = useCallback((userData: Partial<User>) => {
    setUser((prevUser) => {
      if (!prevUser) return null;
      
      const updatedUser = { ...prevUser, ...userData };
      localStorage.setItem('user', JSON.stringify(updatedUser));
      return updatedUser;
    });
    
    console.log('[AuthContext] User data updated');
  }, []);

  const checkAuth = useCallback(async () => {
    const storedToken = getStoredToken();
    const storedUser = localStorage.getItem('user');
    
    if (storedToken && storedUser) {
      try {
        // Verify token is still valid
        const isValid = await verifyToken();
        
        if (isValid) {
          const parsedUser = JSON.parse(storedUser) as User;
          setToken(storedToken);
          setUser(parsedUser);
          setupAutoRefresh();
          console.log('[AuthContext] User authenticated from storage');
        } else {
          // Token invalid, clear storage
          removeStoredToken();
          localStorage.removeItem('user');
          console.log('[AuthContext] Stored token invalid, cleared');
        }
      } catch (error) {
        console.error('[AuthContext] Error parsing stored user:', error);
        removeStoredToken();
        localStorage.removeItem('user');
      }
    } else {
      setToken(null);
      setUser(null);
    }
    
    setIsLoading(false);
  }, [setupAutoRefresh]);

  useEffect(() => {
    checkAuth();
    
    // Cleanup on unmount
    return () => {
      clearRefreshTimer();
    };
  }, [checkAuth, clearRefreshTimer]);

  // Handle beforeunload to persist state
  useEffect(() => {
    const handleBeforeUnload = () => {
      if (token && user) {
        console.log('[AuthContext] Persisting auth state before unload');
        // State is already persisted in localStorage, nothing else needed
      }
    };
    
    window.addEventListener('beforeunload', handleBeforeUnload);
    
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [token, user]);

  const login = async (username: string, password: string, rememberMe: boolean = false): Promise<void> => {
    try {
      setIsLoading(true);
      const response = await authLogin({ username, password });
      
      // Store token and user
      setStoredToken(response.access_token);
      localStorage.setItem('user', JSON.stringify(response.user));
      
      if (rememberMe) {
        localStorage.setItem('rememberMe', 'true');
      }
      
      setToken(response.access_token);
      setUser(response.user);
      
      // Setup auto-refresh
      setupAutoRefresh();
      
      console.log(`[AuthContext] User ${username} logged in successfully`);
    } catch (error) {
      console.error('[AuthContext] Login failed:', error);
      // Re-throw error to be handled by the component
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async (): Promise<void> => {
    try {
      setIsLoading(true);
      console.log('[AuthContext] Logging out...');
      
      clearRefreshTimer();
      await authLogout();
    } catch (error) {
      console.error('[AuthContext] Error during logout:', error);
    } finally {
      // Always clear local state
      removeStoredToken();
      localStorage.removeItem('user');
      localStorage.removeItem('rememberMe');
      setToken(null);
      setUser(null);
      setIsLoading(false);
      
      console.log('[AuthContext] User logged out');
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
    refreshToken,
    updateUser,
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
