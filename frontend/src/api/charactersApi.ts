import apiClient from "./apiClient";
import type { Character, PaginatedResponse } from "@/types";

interface FetchParams {
  tab?: "all" | "favorites";
  sort?: "recent" | "popular";
  cursor?: string;
}

export const getCharacters = async (
  params: FetchParams,
): Promise<PaginatedResponse<Character>> => {
  const response = await apiClient.get<PaginatedResponse<Character>>(
    "/characters/",
    { params },
  );
  return response.data;
};

export const toggleFavoriteApi = async (
  characterId: number,
): Promise<{ status: string }> => {
  const response = await apiClient.post(`/characters/${characterId}/favorite/`);
  return response.data;
};
