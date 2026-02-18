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
  const lists = shallowRef<Record<string, ListState>>({});

  const activeGender = ref<GenderFilter>("F");
  const activeSort = ref<SortOption>("popular");
  const error = ref<string | null>(null);

  const currentKey = computed(
    () => `${activeGender.value}_${activeSort.value}`,
  );

  const currentList = computed(() => {
    const key = currentKey.value;
    if (!lists.value[key]) {
      lists.value[key] = {
        items: [],
        ids: new Set(),
        nextCursor: null,
        isLoading: false,
        isLoaded: false,
      };
    }
    return lists.value[key];
  });

  const chunkedItems = computed(() => {
    const items = currentList.value.items;
    const chunks: Character[][] = [];
    const len = items?.length || 0;
    for (let i = 0; i < len; i += 2) {
      chunks.push(items.slice(i, i + 2));
    }
    return chunks;
  });

  function setGender(gender: GenderFilter) {
    if (activeGender.value === gender) return;
    activeGender.value = gender;
    checkAndLoad();
  }

  function setSort(sort: SortOption) {
    if (activeSort.value === sort) return;
    activeSort.value = sort;
    checkAndLoad();
  }

  function checkAndLoad() {
    if (!currentList.value.isLoaded && !currentList.value.isLoading) {
      fetchCharacters();
    }
  }

  async function fetchCharacters() {
    const key = currentKey.value;
    const list = lists.value[key];

    if (!list || list.isLoading || (list.isLoaded && !list.nextCursor)) return;

    list.isLoading = true;
    error.value = null;

    try {
      const response = await getCharacters({
        gender: activeGender.value,
        sort: activeSort.value,
        cursor: list.nextCursor || undefined,
      });

      const newItems: Character[] = [];
      for (const char of response.items) {
        if (!list.ids.has(char.id)) {
          list.ids.add(char.id);
          newItems.push(char);
        }
      }

      list.items = [...list.items, ...newItems];

      list.nextCursor = response.next_cursor;
      list.isLoaded = true;

      triggerRef(lists);
    } catch (e: any) {
      error.value = "Не удалось загрузить персонажей";
      console.error(e);
    } finally {
      list.isLoading = false;
    }
  }

  return {
    activeGender,
    activeSort,
    error,
    currentList,
    chunkedItems,
    setGender,
    setSort,
    fetchCharacters,
    checkAndLoad,
  };
});
