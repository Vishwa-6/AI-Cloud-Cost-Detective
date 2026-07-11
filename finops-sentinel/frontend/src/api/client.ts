import axios from 'axios';

// Create a globally configured Axios instance
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE,
});

// We'll store the token in memory here for the interceptor to use
let currentToken: string | null = null;

export const setAuthToken = (token: string | null) => {
  currentToken = token;
};

// Interceptor: Attach token if it exists
apiClient.interceptors.request.use(
  (config) => {
    if (currentToken && config.headers) {
      config.headers.Authorization = `Bearer ${currentToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor: Handle 401 Unauthorized globally
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear token and redirect to login ONLY if it wasn't a login attempt itself
      if (error.config && !error.config.url.includes('/api/auth/login')) {
        currentToken = null;
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
