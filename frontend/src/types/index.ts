export interface Character {
  id: number;
  name: string;
  gender: 'M' | 'F';
  description: string;
  photo: string;
  creator: number | null;
}

export interface User {
  telegram_id: number;
  username: string | null;
  first_name: string;
  last_name: string | null;
  balance: number;
}

export interface Tariff {
  id: number; 
  name: string;
  cost: number;
  reward: number;
  photo: string | null;
}