export interface Character {
  id: number;
  name: string;
  gender: "M" | "F";
  tagline: string;
  user_story: string;
  photo: string | null;
  author_id: number | null;
  author_name: string | null;
  likes_count: number;
  is_favorite: boolean;
  greeting_message: string | null;
  chat_id: string | null;
  created_at?: string;
  is_public?: boolean;
}

export interface User {
  id: number;
  username: string | null;
  balance: number;
  preferred_llm_id?: number | null;
  referrals_count?: number;
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
  id: string;
  character: Character;
  last_message: Message | null;
  created_at: string;
}

export interface ChatState {
  characterId: number;
  chatId: string | null;
  messages: Message[];
  nextCursor: string | null;
  isFullyLoaded: boolean;
}

export interface PaginatedResponse<T> {
  next_cursor: string | null;
  items: T[];
}
