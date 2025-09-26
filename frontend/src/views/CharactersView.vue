<script setup lang="ts">
import { onMounted } from 'vue';
import { useCharactersStore } from '@/store/characters';
import CharacterList from '@/components/CharacterList.vue';
import BottomNav from '@/components/BottomNav.vue';

const charactersStore = useCharactersStore();

onMounted(() => {
  charactersStore.fetchCharacters();
});

const handleSelectCharacter = (id: number) => {
  charactersStore.selectCharacter(id);
};

const handleToggleFavorite = (id: number) => {
  charactersStore.toggleFavorite(id);
};
</script>

<template>
  <div class="view-container">
    <div v-if="charactersStore.isLoading" class="status-message">
      Загрузка персонажей...
    </div>
    
    <div v-else-if="charactersStore.error" class="status-message error">
      Ошибка: {{ charactersStore.error }}
    </div>
    
    <CharacterList
      v-else-if="charactersStore.characters.length > 0"
      :characters="charactersStore.characters"
      @select-character="handleSelectCharacter"
      @toggle-favorite="handleToggleFavorite"
    />

    <div v-else class="status-message">
      Персонажи не найдены.
    </div>
    
    <BottomNav />
  </div>
</template>

<style scoped>
.view-container {
  min-height: 100vh;
  width: 100%;
  background: linear-gradient(160deg, #4c2a4e 0%, #2c2c40 100%);
}
.status-message {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 80vh;
  color: white;
  font-size: 18px;
}
.status-message.error {
  color: #ff8a8a;
}
</style>