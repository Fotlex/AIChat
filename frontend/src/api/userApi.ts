import apiClient from "./apiClient";
import type { User } from "@/types";

export const getUser = async (): Promise<User> => {
  const response = await apiClient.get<User>("/users/me/");
  return response.data;
};

export const getSettingsInfo = async () => {
  const response = await apiClient.get("/users/settings/info/");
  return response.data;
};

export const updatePreferredLLm = async (llmId: number) => {
  await apiClient.post("/users/settings/update-llm/", { llm_id: llmId });
};

export const redeemPromocode = async (code: string) => {
  const response = await apiClient.post("/users/promocodes/redeem/", { code });
  return response.data;
};

export const updateProfile = async (username: string) => {
  const response = await apiClient.post("/users/settings/update-profile/", { username });
  return response.data;
};
