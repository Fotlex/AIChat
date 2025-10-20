import apiClient from "./apiClient";
import type { User } from "@/types";

export const getUser = async (): Promise<User> => {
  const response = await apiClient.get<User>("/users/me/");
  return response.data;
};
