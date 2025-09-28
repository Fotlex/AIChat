<script setup lang="ts">
import { computed } from "vue";
import { useCharactersStore } from "@/store/characters";

const charactersStore = useCharactersStore();

const gliderStyle = computed(() => {
  const filter = charactersStore.activeFilter;

  let transformValue = 'translateX(200%)'; 

  if (filter === 'F') {
    transformValue = 'translateX(0%)';
  } else if (filter === 'M') {
    transformValue = 'translateX(100%)';
  }
  
  return {
    transform: transformValue,
  };
});
</script>

<template>
  <div class="filter-wrapper">
    <div class="gender-filter">
      <span class="glider" :style="gliderStyle"></span>
      
      <button
        :class="{ active: charactersStore.activeFilter === 'F' }"
        @click="charactersStore.setFilter('F')"
      >
        Девушки
      </button>
      <button
        :class="{ active: charactersStore.activeFilter === 'M' }"
        @click="charactersStore.setFilter('M')"
      >
        Парни
      </button>
      <button
        :class="{ active: charactersStore.activeFilter === 'yours' }"
        @click="charactersStore.setFilter('yours')"
      >
        Твои
      </button>
    </div>
  </div>
</template>

<style scoped>
.filter-wrapper {
  display: flex;
  justify-content: center;
  padding: 16px;
  width: 100%;
}

.gender-filter {
  display: flex;
  position: relative;
  background-color: var(--tg-theme-secondary-bg-color, #2c2c2e);
  border-radius: 12px;
  padding: 4px;
  width: 100%;
  max-width: 400px;
}

.gender-filter button {
  flex: 1;
  padding: 8px 12px;
  background: none;
  border: none;
  color: var(--tg-theme-hint-color, #999999);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: color 0.3s ease;
  z-index: 2;
  position: relative;
  border-radius: 9px;
}

.gender-filter button.active {
  color: var(--tg-theme-button-text-color, #ffffff);
}

.glider {
  position: absolute;
  top: 4px;
  left: 4px;
  height: calc(100% - 8px);
  width: calc((100% - 8px) / 3);
  background-color: var(--tg-theme-button-color, #007aff);
  border-radius: 9px;
  transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  z-index: 1;
}
</style>