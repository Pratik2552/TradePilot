// ============================================================
// API Contract Types
// Golden Cross Research Platform
// ============================================================

export interface ApiResponse<T> {
  data: T;
  message: string;
  success: boolean;
  timestamp: string; // ISO
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  hasMore: boolean;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, string[]>;
  statusCode: number;
}

export interface SortConfig {
  field: string;
  direction: "asc" | "desc";
}

export interface PaginationConfig {
  page: number;
  pageSize: number;
}

export interface QueryConfig {
  pagination?: PaginationConfig;
  sort?: SortConfig;
  search?: string;
}

// ============================================================
// App Notification Types
// ============================================================

export type NotificationType = "info" | "success" | "warning" | "error";

export interface AppNotification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  read: boolean;
  createdAt: string; // ISO
  actionUrl?: string;
  actionLabel?: string;
}
