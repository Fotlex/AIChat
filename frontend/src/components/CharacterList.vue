<script setup lang="ts">
import type { Character } from '@/types';
import CharacterCard from './CharacterCard.vue';

defineProps<{ characters: Character[] }>();

const emit = defineEmits<{
  (e: 'select-character', id: number): void;
  (e: 'toggle-favorite', id: number): void;
}>();
</script>

<template>
  <div class="character-grid">
    <CharacterCard
      v-for="character in characters"
      :key="character.id"
      :character="character"
      @select="id => emit('select-character', id)"
      @favorite="id => emit('toggle-favorite', id)"
    />
  </div>
</template>

<style scoped>
.character-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  padding: 16px;
  padding-bottom: 90px; 
}
</style>