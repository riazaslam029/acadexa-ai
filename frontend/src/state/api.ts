import axios from "axios";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

export const api = axios.create({
  baseURL: apiBaseUrl,
  timeout: 30_000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("acadexa_access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
