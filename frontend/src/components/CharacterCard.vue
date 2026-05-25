<script setup lang="ts">
import { ref } from "vue";
import type { Character } from "@/types";

const props = defineProps<{
  character: Character | null;
}>();

const emit = defineEmits<{
  (e: "select", id: number): void;
  (e: "like", id: number): void;
}>();

const isAnimating = ref(false);

function formatLikes(count: number): string {
  if (count >= 1000) return (count / 1000).toFixed(1) + "K";
  return count.toString();
}

function handleLikeClick(e: Event) {
  e.stopPropagation();

  if (!props.character || isAnimating.value) return;

  isAnimating.value = true;
  emit("like", props.character.id);

  setTimeout(() => {
    isAnimating.value = false;
  }, 300);
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
      <button
        class="likes-badge"
        :class="{ 'is-liked': character.is_favorite, animating: isAnimating }"
        @click="handleLikeClick"
        aria-label="Toggle Like"
      >
        <i-local-heart class="heart-icon" />
        <span>{{ formatLikes(character.likes_count) }}</span>
      </button>

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
  will-change: transform;
}

.card-overlay {
  position: absolute;
  inset: 0;
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
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 6px 10px;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
  cursor: pointer;
  transform-origin: center;
  transition: transform 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  will-change: transform;
  -webkit-tap-highlight-color: transparent;
}

.heart-icon {
  width: 14px;
  height: 14px;
  fill: transparent;
  stroke: #fff;
  stroke-width: 2px;
  transition:
    fill 0.2s,
    stroke 0.2s;
}

.likes-badge.is-liked .heart-icon {
  fill: #ff4d4d;
  stroke: #ff4d4d;
}

.likes-badge.animating {
  transform: scale(0.85);
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

.card-placeholder {
  background: transparent;
  height: 100%;
  width: 100%;
  pointer-events: none;
  visibility: hidden;
}
</style>
