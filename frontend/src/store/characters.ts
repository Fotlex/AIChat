import { defineStore } from "pinia";
import { getCharacters } from "@/api";
import type { Character } from "@/types";

export interface CharactersState {
  characters: Character[];
  isLoading: boolean;
  error: string | null;
}

export const useCharactersStore = defineStore("characters", {
  state: (): CharactersState => ({
    characters: [],
    isLoading: false,
    error: null,
  }),

  getters: {
    getCharacterById: (state) => (id: number) => {
      return state.characters.find((c) => c.id === id);
    },
  },

  actions: {
    async fetchCharacters() {
      if (this.isLoading) return;

      this.isLoading = true;
      this.error = null;
      try {
        this.characters = await getCharacters();
      } catch (err) {
        this.error =
          err instanceof Error ? err.message : "Произошла неизвестная ошибка";
      } finally {
        this.isLoading = false;
      }
    },

    async toggleFavorite(characterId: number) {
      const character = this.characters.find((c) => c.id === characterId);
      if (character) {
        console.log(
          `STORE: Запрос на изменение "избранного" для ${character.name}.`
        );
      }
    },
  },
});
