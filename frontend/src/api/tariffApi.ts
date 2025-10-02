import apiClient from './apiClient'; 
import type { Tariff } from '@/types';


export async function fetchTariffs(): Promise<Tariff[]> {
  try {
    const response = await apiClient.get<Tariff[]>('/tariffs/');
    return response.data;
  } catch (error) {
    console.error('Ошибка при загрузке тарифов:', error);
    throw new Error('Не удалось загрузить список тарифов.');
  }
}