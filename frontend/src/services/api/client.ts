// ============================================================
// Axios HTTP Client
// Golden Cross Research Platform
//
// This is the single Axios instance for the entire application.
// All API services import from here.
// Configure interceptors for auth, error handling, and logging.
// ============================================================

import axios, { AxiosError, type AxiosInstance } from "axios";
import { API_BASE_URL, API_TIMEOUT_MS } from "@/lib/constants";
import type { ApiError } from "@/types";

// Create the base Axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT_MS,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

// ---- Request Interceptor ---------------------------------------------------
// Attach auth token once Supabase Auth is integrated
apiClient.interceptors.request.use(
  (config) => {
    // TODO (Auth): Attach Authorization header
    // const token = supabase.auth.getSession()?.access_token;
    // if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error)
);

// ---- Response Interceptor --------------------------------------------------
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    const status = error.response?.status;

    if (status === 401) {
      // TODO (Auth): Redirect to login
      console.warn("[API] Unauthorized — redirect to login");
    }

    if (status === 403) {
      console.warn("[API] Forbidden — insufficient permissions");
    }

    if (status === 429) {
      console.warn("[API] Rate limited — retry after backoff");
    }

    if (status && status >= 500) {
      console.error("[API] Server error", error.response?.data);
    }

    return Promise.reject(error);
  }
);

export default apiClient;
