export interface Character {
  id: number;
  name: string;
  gender: "M" | "F";
  tagline: string;
  user_story: string;
  photo: string | null;
  creator: number | null;
  likes_count: number;
  greeting_message: string | null;
  chat_id: number | null;
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
  id: number | string;
  role: "user" | "assistant" | "system";
  content: string;
  created_at: string;
  is_pending?: boolean;
  is_error?: boolean;
}

export interface Chat {
  id: number;
  character: Character;
  last_message: Message | null;
  created_at: string;
}

export interface ChatState {
  characterId: number;
  chatId: number | null;
  messages: Message[];
  nextCursor: string | null;
  isFullyLoaded: boolean;
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
