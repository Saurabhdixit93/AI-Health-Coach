/**
 * API client for Disha backend communication.
 */
import axios, { AxiosInstance, AxiosError } from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    console.error("API Error:", error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// ==================== Types ====================

export interface User {
  id: string;
  name: string;
  user_metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  user_id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
  is_onboarding: boolean;
}

export interface ChatResponse {
  user_message: Message;
  ai_response: Message;
}

export interface MessageHistoryResponse {
  messages: Message[];
  has_more: boolean;
  next_cursor: string | null;
}

// ==================== API Functions ====================

export const api = {
  /**
   * Create a new user
   */
  createUser: async (
    name: string,
    user_metadata: Record<string, any> = {}
  ): Promise<User> => {
    const response = await apiClient.post<User>("/api/users", {
      name,
      user_metadata,
    });
    return response.data;
  },

  /**
   * Get user by ID
   */
  getUser: async (userId: string): Promise<User> => {
    const response = await apiClient.get<User>(`/api/users/${userId}`);
    return response.data;
  },

  /**
   * Send a message and get AI response
   */
  sendMessage: async (
    userId: string,
    content: string,
    isOnboarding: boolean = false
  ): Promise<ChatResponse> => {
    const response = await apiClient.post<ChatResponse>("/api/messages", {
      user_id: userId,
      content,
      is_onboarding: isOnboarding,
    });
    return response.data;
  },

  /**
   * Get message history with pagination
   */
  getMessages: async (
    userId: string,
    before?: string,
    limit: number = 50
  ): Promise<MessageHistoryResponse> => {
    const params: any = { user_id: userId, limit };
    if (before) {
      params.before = before;
    }
    const response = await apiClient.get<MessageHistoryResponse>(
      "/api/messages",
      { params }
    );
    return response.data;
  },

  /**
   * Get typing indicator status
   */
  getTypingStatus: async (
    userId: string
  ): Promise<{ is_typing: boolean; user_id: string }> => {
    const response = await apiClient.get(`/api/typing/${userId}`);
    return response.data;
  },

  /**
   * Health check
   */
  healthCheck: async (): Promise<{
    status: string;
    app_name: string;
    timestamp: string;
  }> => {
    const response = await apiClient.get("/api/health");
    return response.data;
  },
};

export default api;
