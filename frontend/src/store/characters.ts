import { defineStore } from "pinia";
import { getCharacters } from "@/api";
import type { Character } from "@/types";

export type GenderFilter = "F" | "M";
export type SortOption = "recent" | "popular";

interface ListState {
  items: Character[];
  ids: Set<number>;
  nextCursor: string | null;
  isLoading: boolean;
  isLoaded: boolean;
}

interface State {
  lists: Record<string, ListState>;

  activeGender: GenderFilter;
  activeSort: SortOption;

  error: string | null;
}

const createEmptyList = (): ListState => ({
  items: [],
  ids: new Set(),
  nextCursor: null,
  isLoading: false,
  isLoaded: false,
});

export const useCharactersStore = defineStore("characters", {
  state: (): State => ({
    lists: {},
    activeGender: "F",
    activeSort: "popular",
    error: null,
  }),

  getters: {
    currentKey(state): string {
      return `${state.activeGender}_${state.activeSort}`;
    },

    currentList(state): ListState {
      const key = this.currentKey;
      if (!state.lists[key]) {
        state.lists[key] = createEmptyList();
      }
      return state.lists[key];
    },

    chunkedItems(): Character[][] {
      const items = this.currentList.items;
      const chunks: Character[][] = [];
      for (let i = 0; i < items.length; i += 2) {
        chunks.push(items.slice(i, i + 2));
      }
      return chunks;
    },
  },

  actions: {
    setGender(gender: GenderFilter) {
      this.activeGender = gender;
      this.checkAndLoad();
    },

    setSort(sort: SortOption) {
      this.activeSort = sort;
      this.checkAndLoad();
    },

    checkAndLoad() {
      if (!this.currentList.isLoaded && !this.currentList.isLoading) {
        this.fetchCharacters();
      }
    },

    async fetchCharacters() {
      const list = this.currentList;

      if (list.isLoading || (list.isLoaded && !list.nextCursor)) return;

      list.isLoading = true;
      this.error = null;

      try {
        const response = await getCharacters({
          gender: this.activeGender,
          sort: this.activeSort,
          cursor: list.nextCursor || undefined,
        });

        const newItems = response.items.filter((char) => {
          if (list.ids.has(char.id)) return false;
          list.ids.add(char.id);
          return true;
        });

        list.items.push(...newItems);
        list.nextCursor = response.next_cursor;
        list.isLoaded = true;
      } catch (e: any) {
        this.error = "Не удалось загрузить персонажей";
        console.error(e);
      } finally {
        list.isLoading = false;
      }
    },
  },
});
