import { defineStore } from "pinia";
import { getCharacters } from "@/api";
import type { Character } from "@/types";
import { shallowRef, computed, ref, triggerRef } from "vue";

export type GenderFilter = "F" | "M";
export type SortOption = "recent" | "popular";

interface ListState {
  items: Character[];
  ids: Set<number>;
  nextCursor: string | null;
  isLoading: boolean;
  isLoaded: boolean;
}

export const useCharactersStore = defineStore("characters", () => {
  const storage: Record<string, ListState> = {};

  const currentList = shallowRef<ListState>({
    items: [],
    ids: new Set(),
    nextCursor: null,
    isLoading: false,
    isLoaded: false,
  });

  const activeGender = ref<GenderFilter>("F");
  const activeSort = ref<SortOption>("popular");

  function syncCurrent() {
    const key = `${activeGender.value}_${activeSort.value}`;
    if (!storage[key]) {
      storage[key] = {
        items: [],
        ids: new Set(),
        nextCursor: null,
        isLoading: false,
        isLoaded: false,
      };
    }
    currentList.value = storage[key];
  }

  const chunkedItems = computed(() => {
    const items = currentList.value.items;
    const chunks: Character[][] = [];
    for (let i = 0; i < items.length; i += 2) {
      chunks.push(items.slice(i, i + 2));
    }
    return chunks;
  });

  function setGender(gender: GenderFilter) {
    activeGender.value = gender;
    syncCurrent();
    if (!currentList.value.isLoaded) fetchCharacters();
  }

  function setSort(sort: SortOption) {
    activeSort.value = sort;
    syncCurrent();
    if (!currentList.value.isLoaded) fetchCharacters();
  }

  function checkAndLoad() {
    if (!currentList.value.isLoaded) {
      fetchCharacters();
    }
  }

  async function fetchCharacters() {
    const list = currentList.value;
    if (list.isLoading || (list.isLoaded && !list.nextCursor)) return;

    list.isLoading = true;
    triggerRef(currentList);

    try {
      const response = await getCharacters({
        gender: activeGender.value,
        sort: activeSort.value,
        cursor: list.nextCursor || undefined,
      });

      for (const char of response.items) {
        if (!list.ids.has(char.id)) {
          list.ids.add(char.id);
          list.items.push(char);
        }
      }

      list.nextCursor = response.next_cursor;
      list.isLoaded = true;
    } finally {
      list.isLoading = false;
      triggerRef(currentList);
    }
  }

  syncCurrent();

  return {
    activeGender,
    activeSort,
    currentList,
    chunkedItems,
    setGender,
    setSort,
    fetchCharacters,
    checkAndLoad,
  };
});
