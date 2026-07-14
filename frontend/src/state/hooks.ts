import { useMutation, useQuery } from "@tanstack/react-query";
import { AxiosError } from "axios";

import { api } from "./api";

export type LoginPayload = {
  email: string;
  password: string;
};

export type RegisterPayload = {
  name: string;
  email: string;
  password: string;
};

export type DashboardResponse = {
  stats: {
    total_documents: number;
    total_flashcards: number;
    total_quizzes: number;
    total_mcqs: number;
    total_ai_requests: number;
    storage_used_bytes: number;
  };
  recent_uploads: Array<{
    id: number;
    original_name: string;
    created_at: string;
    file_size: number;
    processing_status: string;
  }>;
};

export type ChatHistoryItem = {
  id: number;
  document_id: number;
  owner_id: number;
  question: string;
  answer: string;
  created_at: string;
};

export type ChatResponse = {
  answer: string;
};

export type DocumentResponse = {
  id: number;
  original_name: string;
  file_size: number;
  processing_status: string;
  created_at: string;
  summary: string | null;
};

export type ArtifactResponse = {
  id: number;
  artifact_type: string;
  payload: Record<string, unknown>;
  created_at: string;
};

export function normalizeApiError(error: unknown): string {
  if (error instanceof AxiosError) {
    return (error.response?.data as { detail?: string } | undefined)?.detail ?? error.message;
  }
  return "Something went wrong.";
}

export function useRegisterMutation() {
  return useMutation({
    mutationFn: async (payload: RegisterPayload) => {
      const response = await api.post("/auth/register", payload);
      return response.data;
    },
  });
}

export function useLoginMutation() {
  return useMutation({
    mutationFn: async (payload: LoginPayload) => {
      const form = new URLSearchParams();
      form.set("username", payload.email);
      form.set("password", payload.password);

      const response = await api.post("/auth/login", form, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });
      return response.data as { access_token: string; token_type: string };
    },
  });
}

export function useDashboardQuery(enabled: boolean) {
  return useQuery({
    queryKey: ["dashboard"],
    enabled,
    queryFn: async () => {
      const response = await api.get("/users/dashboard");
      return response.data as DashboardResponse;
    },
  });
}

export function useDocumentsQuery(enabled: boolean) {
  return useQuery({
    queryKey: ["documents"],
    enabled,
    queryFn: async () => {
      const response = await api.get("/documents");
      return response.data as DocumentResponse[];
    },
  });
}

export function useUploadDocumentMutation() {
  return useMutation({
    mutationFn: async ({
      file,
      onProgress,
    }: {
      file: File;
      onProgress?: (value: number) => void;
    }) => {
      const form = new FormData();
      form.append("file", file);
      const response = await api.post("/documents/upload", form, {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress: (event) => {
          if (event.total && onProgress) {
            const value = Math.round((event.loaded * 100) / event.total);
            onProgress(value);
          }
        },
      });
      return response.data as DocumentResponse;
    },
  });
}

export function useChatHistoryQuery(documentId: number, enabled: boolean) {
  return useQuery({
    queryKey: ["chat-history", documentId],
    enabled,
    queryFn: async () => {
      const response = await api.get(`/documents/${documentId}/chat/history`);
      return response.data as ChatHistoryItem[];
    },
  });
}

export function useChatMutation(documentId: number) {
  return useMutation({
    mutationFn: async (question: string) => {
      const response = await api.post(`/documents/${documentId}/chat`, { question });
      return response.data as ChatResponse;
    },
  });
}

export function useArtifactsQuery(documentId: number, artifactPath: string, enabled: boolean) {
  return useQuery({
    queryKey: ["artifacts", artifactPath, documentId],
    enabled,
    queryFn: async () => {
      const response = await api.get(`/documents/${documentId}/${artifactPath}`);
      return response.data as ArtifactResponse[];
    },
  });
}

export function useGenerateArtifactMutation(documentId: number, artifactPath: string) {
  return useMutation({
    mutationFn: async (payload: { count: number; difficulty?: string; language?: string }) => {
      const response = await api.post(`/documents/${documentId}/${artifactPath}`, payload);
      return response.data as ArtifactResponse;
    },
  });
}
