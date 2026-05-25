<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useCharactersStore } from "@/store/characters";
import { useUserStore } from "@/store/user";
import { getCharacterById } from "@/api/charactersApi";
import type { Character } from "@/types";

const route = useRoute();
const router = useRouter();
const charStore = useCharactersStore();
const userStore = useUserStore();
const charId = Number(route.params.id);

const character = ref<Character | null>(null);

onMounted(async () => {
  if (!userStore.currentUser) await userStore.fetchUser();

  let found = charStore.currentList.items.find((c) => c.id === charId);
  if (found) {
    character.value = found;
  } else {
    try {
      const fetched = await getCharacterById(charId);
      character.value = fetched;
      charStore.currentList.items.push(fetched);
    } catch (e) {
      router.back();
    }
  }
});

const startChat = () => {
  router.push({ name: "chat", params: { id: charId } });
};

const openAuthor = () => {
  const id = character.value?.author_id || 0;
  router.push({ name: "profile", params: { id } });
};
</script>

<template>
  <div class="preview-page" v-if="character">
    <div class="hero-section">
      <img :src="character.photo || '/default-avatar.png'" class="hero-image" />
      <div class="hero-overlay"></div>

      <button class="close-btn" @click="router.back()">
        <i-local-arrow-left style="transform: rotate(0deg)" />
      </button>
    </div>

    <div class="content-section">
      <div class="main-info">
        <h1 class="character-name">{{ character.name }}</h1>
        <div class="divider-line"></div>
        <div class="description-scroll">
          <p class="tagline">
            {{
              character.user_story ||
              character.tagline ||
              "Этот персонаж пока не рассказал свою историю..."
            }}
          </p>
        </div>
      </div>

      <footer class="footer-actions">
        <div class="author-info" @click="openAuthor">
          <span class="created-by">Создатель:</span>
          <span class="author-name"
            >@{{ character.author_name || "Система" }}</span
          >
        </div>

        <div class="button-stack">
          <button class="btn-primary" @click="startChat">
            Чат с персонажем
          </button>
        </div>
      </footer>
    </div>
  </div>
</template>

<style scoped>
.preview-page {
  height: 100vh;
  height: 100dvh;
  background: #09090b;
  color: white;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  width: 100%;
  max-width: var(--app-max-width);
  margin: 0 auto;
  position: relative;
  border-left: 1px solid rgba(255, 255, 255, 0.03);
  border-right: 1px solid rgba(255, 255, 255, 0.03);
}

.hero-section {
  position: relative;
  height: 45vh;
  width: 100%;
}

.hero-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to bottom,
    transparent 0%,
    rgba(9, 9, 11, 0.4) 60%,
    rgba(9, 9, 11, 1) 100%
  );
}

.close-btn {
  position: absolute;
  top: calc(20px + env(safe-area-inset-top));
  left: 20px;
  width: 40px;
  height: 40px;
  border-radius: 14px;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 10;
}

.content-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0 24px;
  margin-top: -20px;
  position: relative;
  z-index: 5;
}

.main-info {
  text-align: center;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.character-name {
  font-size: 34px;
  font-weight: 900;
  letter-spacing: -1px;
  margin-bottom: 15px;
  background: linear-gradient(to bottom, #fff, #a1a1aa);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.divider-line {
  width: 40px;
  height: 4px;
  background: #7b61ff;
  border-radius: 2px;
  margin: 0 auto 25px;
}

.description-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 0 10px;
}

.tagline {
  font-size: 17px;
  line-height: 1.6;
  color: #d4d4d8;
  font-weight: 400;
}

.footer-actions {
  flex-shrink: 0;
  padding: 20px 0 calc(20px + env(safe-area-inset-bottom));
  background: #09090b;
}

.author-info {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
  margin-bottom: 25px;
  cursor: pointer;
  opacity: 0.8;
}

.created-by {
  font-size: 13px;
  color: #71717a;
}

.author-name {
  font-size: 13px;
  font-weight: 700;
  color: #7b61ff;
}

.button-stack {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.btn-primary {
  width: 100%;
  padding: 18px;
  border-radius: 20px;
  border: none;
  background: linear-gradient(135deg, #7b61ff 0%, #6366f1 100%);
  color: white;
  font-size: 17px;
  font-weight: 800;
  box-shadow: 0 10px 20px rgba(123, 97, 255, 0.3);
  cursor: pointer;
  transition: transform 0.1s;
}

.btn-primary:active {
  transform: scale(0.98);
}

.btn-secondary {
  width: 100%;
  padding: 14px;
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.btn-secondary:active {
  background: rgba(255, 255, 255, 0.1);
}
</style>
