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

export const refreshToken = async (): Promise<LoginResponse> => {
  const token = getStoredToken();
  
  if (!token) {
    throw new Error('No token available to refresh');
  }

  try {
    const response = await authApi.post<LoginResponse>('/refresh', {}, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error('No se pudo renovar la sesión');
    }
    throw new Error('Error de conexión al renovar sesión');
  }
};

export const verifyToken = async (): Promise<boolean> => {
  const token = getStoredToken();
  
  if (!token) {
    return false;
  }

  try {
    await authApi.get('/verify', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return true;
  } catch (error) {
    return false;
  }
};

export const requestPasswordReset = async (email: string): Promise<{ message: string }> => {
  try {
    const response = await authApi.post<{ message: string }>('/request-password-reset', { email });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const message = error.response?.data?.detail || error.message;
      throw new Error(message || 'Error al solicitar recuperación de contraseña');
    }
    throw new Error('Error de conexión');
  }
};

export const resetPassword = async (token: string, newPassword: string): Promise<{ message: string }> => {
  try {
    const response = await authApi.post<{ message: string }>('/reset-password', {
      token,
      new_password: newPassword,
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const status = error.response?.status;
      const message = error.response?.data?.detail || error.message;

      switch (status) {
        case 400:
          throw new Error('Token inválido o expirado');
        case 422:
          throw new Error('La contraseña no cumple con los requisitos mínimos');
        default:
          throw new Error(message || 'Error al restablecer contraseña');
      }
    }
    throw new Error('Error de conexión');
  }
};

export const changePassword = async (currentPassword: string, newPassword: string): Promise<{ message: string }> => {
  const token = getStoredToken();
  
  if (!token) {
    throw new Error('No hay sesión activa');
  }

  try {
    const response = await authApi.post<{ message: string }>('/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    }, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const status = error.response?.status;
      const message = error.response?.data?.detail || error.message;

      switch (status) {
        case 401:
          throw new Error('Contraseña actual incorrecta');
        case 422:
          throw new Error('La nueva contraseña no cumple con los requisitos mínimos');
        default:
          throw new Error(message || 'Error al cambiar contraseña');
      }
    }
    throw new Error('Error de conexión');
  }
};
