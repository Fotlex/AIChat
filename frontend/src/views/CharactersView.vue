<script setup lang="ts">
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import { useCharactersStore } from "@/store/characters";

import CharacterList from "@/components/CharacterList.vue"; 
import GenderFilter from "@/components/GenderFilter.vue";

const charactersStore = useCharactersStore();
const router = useRouter();

onMounted(() => {
  if (charactersStore.characters.length === 0) {
    charactersStore.fetchCharacters();
  }
});

const handleSelectCharacter = (id: number) => {
  router.push({ name: "chat", params: { id } });
};

const handleToggleFavorite = (id: number) => {
  charactersStore.toggleFavorite(id);
};
</script>

<template>
  <div class="view-container">
    <GenderFilter />

    <div v-if="charactersStore.isLoading" class="status-message">
      Загрузка персонажей...
    </div>

    <div v-else-if="charactersStore.error" class="status-message error">
      Ошибка: {{ charactersStore.error }}
    </div>

    <CharacterList
      v-else-if="charactersStore.filteredCharacters.length > 0"
      :characters="charactersStore.filteredCharacters" 
      @select-character="handleSelectCharacter"
      @toggle-favorite="handleToggleFavorite"
    />

    <div v-else class="status-message">Персонажи не найдены.</div>
  </div>
</template>

<style scoped>
.view-container {
  width: 100%;
  min-height: 100%;
  display: flex;
  flex-direction: column;
}
.status-message {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-grow: 1;
  color: white;
  font-size: 18px;
  padding: 20px;
  text-align: center;
}
.status-message.error {
  color: #ff8a8a;
}
</style>