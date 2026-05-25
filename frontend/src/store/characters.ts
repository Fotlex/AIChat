import { defineStore } from "pinia";
import { getCharacters, toggleFavoriteApi } from "@/api";
import type { Character } from "@/types";
import { shallowRef, computed, ref, triggerRef } from "vue";

export type TabFilter = "all" | "favorites";
export type SortOption = "recent" | "popular";

interface ListState {
  items: Character[];
  ids: Set<number>;
  nextCursor: string | null;
  isLoading: boolean;
  isLoaded: boolean;
}

function shouldInsertInFavorites(
  char: Character,
  lastItem: Character,
  sort: SortOption,
): boolean {
  if (sort === "popular") {
    if (char.likes_count > lastItem.likes_count) return true;
    if (char.likes_count === lastItem.likes_count) {
      return char.id > lastItem.id;
    }
    return false;
  } else {
    const charTime = new Date(char.created_at || 0).getTime();
    const lastTime = new Date(lastItem.created_at || 0).getTime();
    if (charTime > lastTime) return true;
    if (charTime === lastTime) {
      return char.id > lastItem.id;
    }
    return false;
  }
}

function findInsertionIndex(
  items: Character[],
  char: Character,
  sort: SortOption,
): number {
  if (sort === "popular") {
    const idx = items.findIndex((item) => {
      if (char.likes_count > item.likes_count) return true;
      if (char.likes_count === item.likes_count) {
        return char.id > item.id;
      }
      return false;
    });
    return idx === -1 ? items.length : idx;
  } else {
    const charTime = new Date(char.created_at || 0).getTime();
    const idx = items.findIndex((item) => {
      const itemTime = new Date(item.created_at || 0).getTime();
      if (charTime > itemTime) return true;
      if (charTime === itemTime) {
        return char.id > item.id;
      }
      return false;
    });
    return idx === -1 ? items.length : idx;
  }
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

  const activeTab = ref<TabFilter>("all");
  const activeSort = ref<SortOption>("popular");

  function syncCurrent() {
    const key = `${activeTab.value}_${activeSort.value}`;
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

  function setTab(tab: TabFilter) {
    activeTab.value = tab;
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

  async function toggleLike(characterId: number) {
    let targetChar: Character | null = null;
    for (const key in storage) {
      const found = storage[key]?.items.find((c) => c.id === characterId);
      if (found) {
        targetChar = found;
        break;
      }
    }

    if (!targetChar) return;

    const willBeFavorite = !targetChar.is_favorite;

    const backupStates = JSON.parse(JSON.stringify(storage));

    for (const key in storage) {
      const state = storage[key];
      if (!state) continue;

      const char = state.items.find((c) => c.id === characterId);
      if (char) {
        char.is_favorite = willBeFavorite;
        char.likes_count += willBeFavorite ? 1 : -1;
      }
    }

    if (willBeFavorite) {
      const clonedChar: Character = {
        ...targetChar,
        is_favorite: true,
        likes_count: targetChar.likes_count + (targetChar.is_favorite ? 0 : 1),
      };

      for (const sort of ["popular", "recent"] as SortOption[]) {
        const favKey = `favorites_${sort}`;
        const favState = storage[favKey];
        if (favState && favState.isLoaded) {
          if (!favState.ids.has(characterId)) {
            const lastItem = favState.items[favState.items.length - 1];

            const fitsInWindow =
              !lastItem ||
              shouldInsertInFavorites(clonedChar, lastItem, sort) ||
              favState.nextCursor === null;

            if (fitsInWindow) {
              const idx = findInsertionIndex(favState.items, clonedChar, sort);
              favState.items.splice(idx, 0, clonedChar);
              favState.ids.add(characterId);
            }
          }
        }
      }
    } else {
      for (const sort of ["popular", "recent"] as SortOption[]) {
        const favKey = `favorites_${sort}`;
        const favState = storage[favKey];
        if (favState) {
          favState.items = favState.items.filter((c) => c.id !== characterId);
          favState.ids.delete(characterId);
        }
      }
    }

    triggerRef(currentList);

    try {
      await toggleFavoriteApi(characterId);
    } catch (e) {
      for (const key in storage) {
        if (storage[key] && backupStates[key]) {
          storage[key].items = backupStates[key].items;
          storage[key].ids = new Set(backupStates[key].ids);
          storage[key].nextCursor = backupStates[key].nextCursor;
        }
      }
      triggerRef(currentList);
    }
  }

  async function fetchCharacters() {
    const list = currentList.value;
    if (list.isLoading || (list.isLoaded && !list.nextCursor)) return;

    list.isLoading = true;
    triggerRef(currentList);

    try {
      const response = await getCharacters({
        tab: activeTab.value,
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
    activeTab,
    activeSort,
    currentList,
    chunkedItems,
    setTab,
    setSort,
    fetchCharacters,
    checkAndLoad,
    toggleLike,
  };
});
