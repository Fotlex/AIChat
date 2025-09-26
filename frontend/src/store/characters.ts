import { defineStore } from 'pinia';
import { getCharacters } from '@/api/charactersApi';
import type { Character } from '@/types';


export interface CharactersState {
  characters: Character[];
  isLoading: boolean;
  error: string | null;
}

export const useCharactersStore = defineStore('characters', {
  state: (): CharactersState => ({
    characters: [],
    isLoading: false,
    error: null,
  }),


  actions: {
    async fetchCharacters() {
      if (this.isLoading) return;
      
      this.isLoading = true;
      this.error = null;
      try {
        const data = await getCharacters();
        this.characters = data;
      } catch (err) {
        this.error = (err as Error).message;
      } finally {
        this.isLoading = false;
      }
    },

    selectCharacter(characterId: number) {
      const character = this.characters.find(c => c.id === characterId);
      if (character) {
        console.log(`STORE: Выбран персонаж: ${character.name}. Открываем чат...`);
        alert(`Нажатие на карточку персонажа: ${character.name}`);
      }
    },

    
    toggleFavorite(characterId: number) {
      const character = this.characters.find(c => c.id === characterId);
      if (character) {
        console.log(`STORE: Запрос на изменение "избранного" для ${character.name}.`);
        alert(`Нажатие на "сердечко" у персонажа: ${character.name}`);
      }
    },
  },
});