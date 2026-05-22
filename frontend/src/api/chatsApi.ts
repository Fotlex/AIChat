import apiClient from "./apiClient";
import type { Chat, PaginatedResponse } from "@/types";

export const getChats = async (cursor?: string | null): Promise<PaginatedResponse<Chat>> => {
  const params = cursor ? { cursor } : {};
  const response = await apiClient.get<PaginatedResponse<Chat>>("/chats/", { params });
  return response.data;
};
