import axios from 'axios';

const api = axios.create({
  baseURL: '/api/gensui',
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('gensui_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('gensui_token');
      localStorage.removeItem('gensui_admin');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
