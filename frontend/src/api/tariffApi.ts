import apiClient from "./apiClient";
import type { Tariff } from "@/types";

export const getTariffs = async (): Promise<Tariff[]> => {
  const response = await apiClient.get<Tariff[]>("/tariffs/");
  return response.data;
};
