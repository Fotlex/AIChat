import apiClient from "./apiClient";
import type { Tariff } from "@/types";

export const getTariffs = async (): Promise<Tariff[]> => {
  const response = await apiClient.get<Tariff[]>("/tariffs/");
  return response.data;
};

export const createPayment = async (tariffId: number): Promise<{ payment_url: string }> => {
  const response = await apiClient.post("/payments/create/", { tariff_id: tariffId });
  return response.data;
};