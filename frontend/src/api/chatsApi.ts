import apiClient from "./apiClient";
import type { Chat, Message, PaginatedResponse } from "@/types";

export const getChats = async (): Promise<Chat[]> => {
  const response = await apiClient.get<Chat[]>("/chats/");
  return response.data;
};

export const getOrCreateChatWithMessages = async (
  characterId: number
): Promise<PaginatedResponse<any> & { chat: Chat }> => {
  const response = await apiClient.get<PaginatedResponse<any> & { chat: Chat }>(
    `/chats/character/${characterId}/`
  );
  return response.data;
};

export const getMessagesByUrl = async (
  url: string
): Promise<PaginatedResponse<Message[]>> => {
  const response = await apiClient.get<PaginatedResponse<Message[]>>(url);
  return response.data;
};
