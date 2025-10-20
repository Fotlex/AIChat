import apiClient from "./apiClient";
import type { Character } from "@/types";

export const getCharacters = async (): Promise<Character[]> => {
  const response = await apiClient.get<Character[]>("/characters/");
  return response.data;
};
