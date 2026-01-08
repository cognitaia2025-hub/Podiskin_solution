/**
 * Base API Client Configuration
 * 
 * Configures axios with interceptors for JWT authentication
 * and automatic error handling.
 */

import axios, { type AxiosInstance, type InternalAxiosRequestConfig } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Create configured axios instance
 */
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

/**
 * Request interceptor - Add JWT token to all requests
 */
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('token');

    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor - Handle errors globally with user-friendly messages
 */
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle network errors (no response)
    if (!error.response) {
      const networkError = new Error('Error de conexión. Por favor, verifica tu conexión a internet e intenta de nuevo.');
      (networkError as any).isNetworkError = true;
      (networkError as any).originalError = error;
      console.error('❌ Error de red:', error.message);
      return Promise.reject(networkError);
    }

    // Handle specific HTTP errors
    switch (error.response?.status) {
      case 401:
        // Token expired or invalid - logout user
        localStorage.removeItem('token');
        localStorage.removeItem('user');

        // Redirect to login if not already there
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
        break;

      case 429:
        error.message = 'Demasiadas solicitudes. Por favor, espera un momento antes de intentar de nuevo.';
        break;

      case 500:
      case 502:
      case 503:
      case 504:
        error.message = 'Error del servidor. Por favor, intenta de nuevo más tarde.';
        break;
    }

    return Promise.reject(error);
  }
);

export default api;
export { API_BASE_URL };
