<script setup lang="ts">
import { onMounted } from "vue";
import { useCharactersStore } from "@/store/characters";
import VirtualCharacterGrid from "@/components/VirtualCharacterGrid.vue";
import GenderFilter from "@/components/GenderFilter.vue";
import SortDropdown from "@/components/SortDropdown.vue";

const store = useCharactersStore();

onMounted(() => {
  store.fetchCharacters();
});
</script>

<template>
  <div class="view-container">
    <div class="filters-header">
      <GenderFilter />
      <SortDropdown />
    </div>

    <div class="content-area">
      <div v-if="store.error" class="error-msg">{{ store.error }}</div>

      <VirtualCharacterGrid />
    </div>
  </div>
</template>

<style scoped>
.view-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  background-color: #1a1a1a;
  overflow: hidden;
}

.filters-header {
  flex-shrink: 0;
  background: rgba(26, 26, 26, 0.95);
  backdrop-filter: blur(10px);
  z-index: 10;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.content-area {
  flex-grow: 1;
  min-height: 0;
  position: relative;
}

.error-msg {
  color: #ff4d4d;
  text-align: center;
  padding: 20px;
}
</style>
