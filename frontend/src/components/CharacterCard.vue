<script setup lang="ts">
import type { Character } from "@/types";

defineProps<{ character: Character }>();

const emit = defineEmits<{
  (e: "select", id: number): void;
  (e: "favorite", id: number): void;
}>();

const isFavorite = false;
</script>

<template>
  <div class="card" @click="emit('select', character.id)">
    <img :src="character.photo" :alt="character.name" class="card-image" />
    <div class="card-overlay">
      <div class="card-info">
        <h3 class="card-name">{{ character.name }}</h3>
        <p class="card-description">{{ character.description }}</p>
      </div>
      <div class="card-actions">
        <button class="icon-button" @click.stop="emit('select', character.id)">
          <i-local-chat />
        </button>
        <button
          class="icon-button"
          @click.stop="emit('favorite', character.id)"
        >
          <i-local-heart :class="{ active: isFavorite }" />
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.icon-button .active {
  fill: #ff4d4d;
  stroke: #ff4d4d;
}
.card {
  position: relative;
  border-radius: 20px;
  overflow: hidden;
  cursor: pointer;
  aspect-ratio: 3 / 4;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  transition: transform 0.2s ease-in-out;
  background-color: #333;
}
.card:hover {
  transform: scale(1.03);
}
.card-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 1;
}
.card-overlay {
  position: relative;
  z-index: 2;
  padding: 16px;
  color: white;
  background: linear-gradient(
    180deg,
    rgba(0, 0, 0, 0) 0%,
    rgba(0, 0, 0, 0.7) 100%
  );
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  min-height: 120px;
}
.card-name {
  font-size: 24px;
  font-weight: bold;
  margin: 0 0 4px;
}
.card-description {
  font-size: 14px;
  margin: 0;
  opacity: 0.9;
}
.card-actions {
  display: flex;
  gap: 8px;
}
.icon-button {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;
}
</style>
