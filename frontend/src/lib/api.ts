import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
});

// Attach JWT Bearer token on every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Redirect to login on 401 responses (skip for login requests)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const isLoginRequest = error.config?.url?.includes("/auth/login");
    if (error.response?.status === 401 && !isLoginRequest) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login?expired=true";
    }
    return Promise.reject(error);
  },
);

export default api;
