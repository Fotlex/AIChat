import axios from 'axios';
import type { Character } from '@/types';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
});

export const getCharacters = async (): Promise<Character[]> => {
  try {
    const response = await apiClient.get<Character[]>('/characters/');

    
    return response.data;

  } catch (error) {
    console.error('Ошибка при загрузке персонажей:', error);
    throw new Error('Не удалось загрузить список персонажей.');
  }
};