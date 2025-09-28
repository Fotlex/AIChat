import { defineStore } from "pinia";

export interface UserState {
  balance: number;
  isLoading: boolean;
  error: string | null;
}

export const useUserStore = defineStore("user", {
  state: (): UserState => ({
    balance: 66,
    isLoading: false,
    error: null,
  }),

  actions: {},
});
