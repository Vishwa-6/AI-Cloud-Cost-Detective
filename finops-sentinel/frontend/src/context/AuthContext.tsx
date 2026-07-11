import { createContext, useState, useContext, useEffect } from 'react';
import type { ReactNode } from 'react';
import apiClient, { setAuthToken } from '../api/client';

interface User {
  id: number;
  email: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);

  // Sync token to API client interceptor whenever it changes
  useEffect(() => {
    setAuthToken(token);
    
    // If we have a token but no user, we could fetch /api/auth/me here
    // But for simplicity in this stage, login() directly sets the user.
    if (token && !user) {
      apiClient.get('/api/auth/me')
        .then(res => setUser(res.data))
        .catch(() => logout()); // Token might be invalid
    }
  }, [token]);

  const login = async (email: string, password: string) => {
    const response = await apiClient.post('/api/auth/login', { email, password });
    const { access_token } = response.data;
    
    setToken(access_token);
    setAuthToken(access_token);
    
    // Fetch user details
    const meResponse = await apiClient.get('/api/auth/me');
    setUser(meResponse.data);
  };

  const signup = async (email: string, password: string) => {
    await apiClient.post('/api/auth/signup', { email, password });
    // Auto login after signup
    await login(email, password);
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    setAuthToken(null);
  };

  const value = {
    user,
    token,
    isAuthenticated: !!token,
    login,
    signup,
    logout
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
