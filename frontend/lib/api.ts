import axios from "axios";
import { getToken, clearSession } from "./auth";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  timeout: 60000,
});

// Attach JWT on every request
api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Redirect to login on 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      clearSession();
      if (typeof window !== "undefined") window.location.href = "/auth/login";
    }
    return Promise.reject(err);
  }
);

// ── Auth ──────────────────────────────────────────────────────

export const authApi = {
  login: (email: string, password: string) =>
    api.post("/api/auth/login", { email, password }),
  register: (email: string, password: string, full_name: string) =>
    api.post("/api/auth/register", { email, password, full_name }),
  logout: () => api.post("/api/auth/logout"),
};

// ── Datasets ─────────────────────────────────────────────────

export const datasetApi = {
  upload: (formData: FormData) =>
    api.post("/api/datasets/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  list: () => api.get("/api/datasets/"),
  get: (id: string) => api.get(`/api/datasets/${id}`),
  delete: (id: string) => api.delete(`/api/datasets/${id}`),
};

// ── Analyses ─────────────────────────────────────────────────

export const analysisApi = {
  create: (payload: {
    dataset_id: string;
    title: string;
    dependent_var: string;
    independent_vars: string[];
    control_vars?: string[];
    models: string[];
    diagnostics?: string[];
  }) => api.post("/api/analyses/", payload),

  list: () => api.get("/api/analyses/"),
  get: (id: string) => api.get(`/api/analyses/${id}`),
  delete: (id: string) => api.delete(`/api/analyses/${id}`),
  downloadReport: (id: string) =>
    api.get(`/api/analyses/${id}/download`, { responseType: "blob" }),
};

// ── Tasks ─────────────────────────────────────────────────────

export const taskApi = {
  status: (taskId: string) => api.get(`/api/tasks/${taskId}`),
};

export default api;
