<script setup lang="ts">
import type { Character } from "@/types";

defineProps<{
  character: Character | null;
  balance: number;
}>();

const emit = defineEmits<{
  (e: "back"): void;
}>();
</script>

<template>
  <header class="chat-header">
    <div class="chat-header-content">
      <button @click="emit('back')" class="back-button">
        <i-local-arrow-left />
      </button>

      <div v-if="character" class="character-info">
        <img
          :src="character.photo || '/default-avatar.png'"
          :alt="character.name"
          class="header-avatar"
        />
        <span class="character-name">{{ character.name }}</span>
      </div>

      <div class="user-balance">
        <i-local-crystal class="balance-icon" />
        <span>{{ balance }}</span>
      </div>
    </div>
  </header>
</template>

<style scoped>
.chat-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: calc(50px + env(safe-area-inset-top));
  padding-top: env(safe-area-inset-top);
  background-color: rgba(26, 26, 26, 0.9);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(80, 80, 80, 0.5);
  z-index: 100;
  color: white;
}

.chat-header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 50px;
  padding: 0 16px;
  position: relative;
}

.back-button {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  transition: background-color 0.2s;
  z-index: 5;
}
.back-button:hover {
  background-color: rgba(255, 255, 255, 0.1);
}
.back-button > :deep(svg) {
  width: 24px;
  height: 24px;
  fill: #fff;
}

.character-info {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
}

.header-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  object-fit: cover;
}

.character-name {
  font-size: 17px;
}

.user-balance {
  display: flex;
  align-items: center;
  gap: 6px;
  background-color: rgba(255, 255, 255, 0.1);
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 16px;
  font-weight: 500;
  margin-left: auto;
  z-index: 5;
}

.balance-icon {
  width: 18px;
  height: 18px;
  color: #a9a9b2;
}
.balance-icon :deep(path) {
  stroke: #81b2ff;
}
</style>
