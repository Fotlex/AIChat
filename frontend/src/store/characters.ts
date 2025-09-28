import { defineStore } from "pinia";
import { getCharacters } from "@/api";
import type { Character } from "@/types";
import { useUserStore } from "./user";

type FilterMode = 'F' | 'M' | 'yours';

export interface CharactersState {
  characters: Character[];
  isLoading: boolean;
  error: string | null;
  activeFilter: FilterMode;
}

export const useCharactersStore = defineStore("characters", {
  state: (): CharactersState => ({
    characters: [],
    isLoading: false,
    error: null,
    activeFilter: 'F',
  }),

  getters: {
    getCharacterById: (state) => (id: number) => {
      return state.characters.find((c) => c.id === id);
    },
    
    filteredCharacters(state): Character[] {
      const userStore = useUserStore();
      const currentUserId = userStore.currentUser?.telegram_id;

      switch (state.activeFilter) {
        case 'F':
          return state.characters.filter(c => c.gender === 'F' && c.creator === null);
        
        case 'M':
          return state.characters.filter(c => c.gender === 'M' && c.creator === null);
        
        case 'yours':
          if (!currentUserId) return [];
          return state.characters.filter(c => c.creator === currentUserId);
        
        default:
          return state.characters.filter(c => c.gender === 'F' && c.creator === null);
      }
    }
  },

  actions: {
    async fetchCharacters() {
      if (this.characters.length > 0 || this.isLoading) return;

      this.isLoading = true;
      this.error = null;
      try {
        this.characters = await getCharacters();
      } catch (err) {
        this.error = err instanceof Error ? err.message : "Произошла ошибка при загрузке персонажей";
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
    
    setFilter(filter: FilterMode) {
      this.activeFilter = filter;
    }
  },
});