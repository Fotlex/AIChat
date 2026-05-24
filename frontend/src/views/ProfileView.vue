<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useUserStore } from "@/store/user";
import {
  getSettingsInfo,
  getAuthorProfile,
  updateProfile,
} from "@/api/userApi";
import { useRoute, useRouter } from "vue-router";

const userStore = useUserStore();
const route = useRoute();
const router = useRouter();

const profileData = ref<any>(null);
const profileCharacters = ref<any[]>([]);
const isEditing = ref(false);
const editName = ref("");
const isLoading = ref(true);

const targetId = Number(route.params.id);
const isMyProfile = computed(() => targetId === userStore.currentUser?.id);

onMounted(async () => {
  try {
    if (!userStore.currentUser) {
      await userStore.fetchUser();
    }

    if (isMyProfile.value) {
      const data = await getSettingsInfo();
      profileData.value = data.user;
      profileCharacters.value = data.my_characters;
      editName.value = data.user.username;
    } else {
      const data = await getAuthorProfile(targetId);
      profileData.value = data.user;
      profileCharacters.value = data.characters;
    }
  } catch (e) {
    console.error("Профиль не найден", e);
  } finally {
    isLoading.value = false;
  }
});

const saveName = async () => {
  if (
    !isMyProfile.value ||
    !editName.value.trim() ||
    editName.value === profileData.value.username
  ) {
    isEditing.value = false;
    return;
  }
  try {
    await updateProfile(editName.value);
    profileData.value.username = editName.value;
    await userStore.fetchUser();
    isEditing.value = false;
  } catch (e: any) {
    alert(e.response?.data?.error || "Ошибка");
  }
};

const goToChat = (id: number) => {
  router.push({ name: "character-detail", params: { id } });
};
</script>

<template>
  <div class="profile-page">
    <header class="top-bar">
      <button class="icon-btn back" @click="router.back()">
        <i-local-arrow-left />
      </button>
      <h1 class="page-title">
        {{ isMyProfile ? "Мой аккаунт" : "Профиль автора" }}
      </h1>
      <div class="spacer"></div>
    </header>

    <div v-if="isLoading" class="loader"><div class="spinner"></div></div>

    <div v-else-if="profileData" class="profile-scroll-area">
      <section class="user-hero">
        <div class="avatar-wrapper">
          <div class="main-avatar">
            {{ profileData.username?.[0]?.toUpperCase() }}
          </div>
        </div>

        <div class="name-section">
          <div
            v-if="!isEditing"
            class="name-display"
            :class="{ clickable: isMyProfile }"
            @click="isMyProfile && (isEditing = true)"
          >
            <span class="user-handle">@{{ profileData.username }}</span>
            <span v-if="isMyProfile" class="edit-hint"
              >Нажмите, чтобы изменить</span
            >
          </div>

          <div v-else-if="isMyProfile" class="name-edit-field">
            <input
              v-model="editName"
              @blur="saveName"
              @keyup.enter="saveName"
              maxlength="20"
              autofocus
            />
          </div>
        </div>

        <div class="stats-container">
          <div class="stat-item" v-if="isMyProfile">
            <span class="val">{{ userStore.balance }}</span>
            <span class="lab">Кристаллов 💎</span>
          </div>
          <div class="vertical-divider" v-if="isMyProfile"></div>
          <div class="stat-item">
            <span class="val">{{ profileCharacters.length }}</span>
            <span class="lab">Персонажей 🎭</span>
          </div>
        </div>
      </section>

      <section class="characters-section">
        <h2 class="section-title">Герои автора</h2>
        <div v-if="profileCharacters.length === 0" class="empty-state">
          Нет созданных персонажей
        </div>
        <div v-else class="compact-grid">
          <div
            v-for="c in profileCharacters"
            :key="c.id"
            class="mini-icon-card"
            @click="goToChat(c.id)"
          >
            <div class="icon-img-box">
              <img :src="c.photo || '/default-avatar.png'" alt="" />
            </div>
            <span class="tiny-name">{{ c.name }}</span>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.profile-page {
  height: 100vh;
  background: #0e0e10;
  color: white;
  display: flex;
  flex-direction: column;
}
.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: calc(20px + env(safe-area-inset-top)) 20px 20px;
}
.icon-btn {
  background: rgba(255, 255, 255, 0.05);
  width: 42px;
  height: 42px;
  border-radius: 14px;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: none;
}
.spacer {
  width: 42px;
}
.profile-scroll-area {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 50px;
}
.user-hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
}
.avatar-wrapper {
  margin-bottom: 20px;
}
.main-avatar {
  width: 110px;
  height: 110px;
  background: linear-gradient(135deg, #7b61ff, #007aff);
  border-radius: 35px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 46px;
  font-weight: 900;
  box-shadow: 0 10px 30px rgba(123, 97, 255, 0.3);
}
.name-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}
.name-display.clickable {
  cursor: pointer;
}
.user-handle {
  font-size: 28px;
  font-weight: 900;
}
.edit-hint {
  font-size: 12px;
  color: #8e8e93;
}
.name-edit-field input {
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid #7b61ff;
  border-radius: 12px;
  padding: 10px;
  color: white;
  text-align: center;
  font-size: 20px;
  outline: none;
}
.stats-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 30px;
  margin-top: 30px;
  background: rgba(255, 255, 255, 0.03);
  padding: 15px 30px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}
.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.val {
  font-size: 20px;
  font-weight: bold;
}
.lab {
  font-size: 11px;
  color: #8e8e93;
  text-transform: uppercase;
  margin-top: 4px;
}
.vertical-divider {
  width: 1px;
  height: 30px;
  background: rgba(255, 255, 255, 0.1);
}
.characters-section {
  padding: 20px;
}
.section-title {
  font-size: 12px;
  font-weight: bold;
  color: #8e8e93;
  text-transform: uppercase;
  margin-bottom: 15px;
}
.compact-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
}
.mini-icon-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}
.icon-img-box {
  width: 100%;
  aspect-ratio: 1;
  border-radius: 16px;
  background: #1c1c1e;
  overflow: hidden;
}
.icon-img-box img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.tiny-name {
  font-size: 12px;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  width: 100%;
}
.loader {
  display: flex;
  justify-content: center;
  padding-top: 100px;
}
.spinner {
  width: 30px;
  height: 30px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: #7b61ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
