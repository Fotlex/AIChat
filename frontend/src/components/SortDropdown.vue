<script setup lang="ts">
import { useCharactersStore } from "@/store/characters";

const store = useCharactersStore();
</script>

<template>
  <div class="sort-wrapper">
    <label class="sort-label">Сортировка:</label>
    <select
      class="sort-select"
      :value="store.activeSort"
      @change="store.setSort(($event.target as HTMLSelectElement).value as any)"
    >
      <option value="popular">🔥 Популярные</option>
      <option value="recent">✨ Новые</option>
    </select>
  </div>
</template>

<style scoped>
.sort-wrapper {
  padding: 0 16px 10px 16px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
}
.sort-label {
  font-size: 13px;
  color: #8e8e93;
}
.sort-select {
  appearance: none;
  background-color: #2c2c2e;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  outline: none;
  cursor: pointer;
}
</style>
