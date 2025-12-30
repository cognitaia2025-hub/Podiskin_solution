import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const TOKEN_KEY = 'token';

// Create axios instance for auth
const authApi = axios.create({
  baseURL: `${API_URL}/auth`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface User {
  id: number;
  username: string;
  email: string;
  rol: string;
  nombre_completo: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

// Token management functions
export const getStoredToken = (): string | null => {
  return localStorage.getItem(TOKEN_KEY);
};

export const setStoredToken = (token: string): void => {
  localStorage.setItem(TOKEN_KEY, token);
};

export const removeStoredToken = (): void => {
  localStorage.removeItem(TOKEN_KEY);
};

// Auth API functions
export const login = async (credentials: LoginCredentials): Promise<LoginResponse> => {
  try {
    const response = await authApi.post<LoginResponse>('/login', credentials);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const status = error.response?.status;
      const message = error.response?.data?.detail || error.message;

      switch (status) {
        case 401:
          throw new Error('Usuario o contraseña incorrectos');
        case 403:
          throw new Error('No tienes permisos para acceder');
        case 429:
          throw new Error('Demasiados intentos. Por favor, espera un momento');
        default:
          throw new Error(message || 'Error al iniciar sesión');
      }
    }
    throw new Error('Error de conexión. Por favor, verifica tu internet');
  }
};

export const logout = async (): Promise<void> => {
  const token = getStoredToken();
  
  if (!token) {
    return;
  }

  try {
    await authApi.post('/logout', {}, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  } catch (error) {
    console.error('Error during logout:', error);
    // Continue with local logout even if API call fails
  } finally {
    removeStoredToken();
  }
};
