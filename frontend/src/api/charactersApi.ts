import apiClient from "./apiClient";
import type { Character, PaginatedResponse } from "@/types";

interface FetchParams {
  gender?: "M" | "F";
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
