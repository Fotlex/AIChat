export interface Character {
  id: number;
  name: string;
  gender: "M" | "F";
  description: string;
  photo: string | null;
  creator: number | null;
  likes_count: number;
  welcome_message: string | null;
}

export interface User {
  telegram_id: number;
  username: string | null;
  first_name: string | null;
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

export interface Message {
  id: number;
  role: "user" | "assistant" | "system";
  content: string;
  created_at: string;
}

export interface Chat {
  id: number;
  character: Character;
  last_message: Message | null;
  created_at: string;
}

export interface PaginatedResponse<T> {
  next: string | null;
  previous: string | null;
  results: T;
}

export interface PaginatedResponse<T> {
  next_cursor: string | null;
  items: T[];
}
