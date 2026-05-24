<script setup lang="ts">
import type { Character } from "@/types";

const props = defineProps<{
  character: Character | null;
}>();

const emit = defineEmits<{
  (e: "select", id: number): void;
}>();

function formatLikes(count: number): string {
  if (count >= 1000) return (count / 1000).toFixed(1) + "K";
  return count.toString();
}
</script>

<template>
  <div v-if="character" class="card" @click="emit('select', character.id)">
    <img
      :src="character.photo || '/default-avatar.png'"
      alt=""
      class="card-image"
      loading="lazy"
      decoding="async"
    />

    <div class="card-overlay">
      <div class="likes-badge">
        <i-local-heart class="heart-icon" />
        <span>{{ formatLikes(character.likes_count) }}</span>
      </div>

      <div class="card-info">
        <div class="card-name">{{ character.name }}</div>
        <div class="card-desc">{{ character.tagline }}</div>
      </div>
    </div>
  </div>

  <div v-else class="card-placeholder"></div>
</template>

<style scoped>
.card {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 16px;
  overflow: hidden;
  background-color: #2c2c2e;
  transform: translateZ(0);
  cursor: pointer;
}

.card-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.card-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    180deg,
    rgba(0, 0, 0, 0) 50%,
    rgba(0, 0, 0, 0.85) 100%
  );
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 12px;
}

.likes-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  border-radius: 12px;
  padding: 4px 8px;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
}

.heart-icon {
  width: 14px;
  height: 14px;
  fill: #ff4d4d;
}

.card-name {
  font-weight: 700;
  font-size: 16px;
  margin-bottom: 4px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
}

.card-desc {
  font-size: 12px;
  color: #d1d1d6;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  opacity: 0.9;
}
</style>
