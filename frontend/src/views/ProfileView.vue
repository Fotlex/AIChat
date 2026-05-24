<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useUserStore } from '@/store/user';
import { getSettingsInfo, updateProfile } from '@/api/userApi';
import { useRoute, useRouter } from "vue-router";

const userStore = useUserStore();
const route = useRoute();
const router = useRouter();

const myCharacters = ref<any[]>([]);
const isEditing = ref(false);
const editName = ref("");
const isLoading = ref(true);
const error = ref("");

const isMyProfile = computed(() => {
  return Number(route.params.id) === userStore.currentUser?.id;
});

onMounted(async () => {
  try {
    if (!userStore.currentUser) {
      await userStore.fetchUser();
    }
    
    const data = await getSettingsInfo();
    myCharacters.value = data.my_characters;
    editName.value = data.user.username;
  } finally {
    isLoading.value = false;
  }
});

const saveName = async () => {
  if (!isMyProfile.value) return;
  
  if (!editName.value.trim() || editName.value === userStore.currentUser?.username) {
    isEditing.value = false;
    return;
  }
  try {
    error.value = "";
    await updateProfile(editName.value);
    await userStore.fetchUser();
    isEditing.value = false;
  } catch (e: any) {
    error.value = e.response?.data?.error || "Ник занят";
  }
};

const goToChat = (id: number) => {
  router.push({ name: 'character-detail', params: { id } });
};
</script>

<template>
  <div class="profile-page">
    <header class="top-bar">
      <button class="icon-btn back" @click="router.back()">
        <i-local-arrow-left />
      </button>
      <h1 class="page-title">{{ isMyProfile ? 'Ваш аккаунт' : 'Профиль автора' }}</h1>
      <div class="spacer"></div>
    </header>

    <div v-if="isLoading" class="loading-container">
      <div class="spinner"></div>
    </div>

    <div v-else class="profile-scroll-area">
      <section class="user-hero">
        <div class="avatar-wrapper">
          <div class="main-avatar">
            {{ editName[0]?.toUpperCase() }}
          </div>
          <div class="avatar-shadow"></div>
        </div>

        <div class="name-section">
          <!-- Если мой профиль — можно кликнуть и редактировать -->
          <div v-if="!isEditing" class="name-display" :class="{ 'clickable': isMyProfile }" @click="isMyProfile && (isEditing = true)">
            <span class="user-handle">@{{ isMyProfile ? userStore.currentUser?.username : editName }}</span>
            <span v-if="isMyProfile" class="edit-hint">Нажмите, чтобы изменить</span>
          </div>
          
          <!-- Поле ввода только если владелец нажал на ник -->
          <div v-else-if="isMyProfile" class="name-edit-field">
            <input 
              v-model="editName" 
              @blur="saveName" 
              @keyup.enter="saveName"
              maxlength="20"
              auto-focus
            />
          </div>
        </div>

        <div class="stats-container">
          <!-- Блок с кристаллами показывается ТОЛЬКО если профиль мой -->
          <div class="stat-item" v-if="isMyProfile">
            <span class="val">{{ userStore.balance }}</span>
            <span class="lab">Кристаллов 💎</span>
          </div>
          
          <!-- Разделитель тоже только если мой профиль (чтобы не висел один) -->
          <div class="vertical-divider" v-if="isMyProfile"></div>
          
          <div class="stat-item">
            <span class="val">{{ myCharacters.length }}</span>
            <span class="lab">Публикаций 🎭</span>
          </div>
        </div>
      </section>

      <section class="characters-section">
        <h2 class="section-title">Герои автора</h2>
        
        <div v-if="myCharacters.length === 0" class="empty-state">
          <p>Пока нет созданных персонажей</p>
        </div>

        <div v-else class="compact-grid">
          <div 
            v-for="c in myCharacters" 
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
  background: linear-gradient(160deg, #1e1e2e 0%, #000000 100%);
  color: white;
  display: flex;
  flex-direction: column;
}

.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: calc(20px + env(safe-area-inset-top)) 20px 20px;
  z-index: 10;
}

.icon-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  width: 42px;
  height: 42px;
  border-radius: 14px;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

.page-title { font-size: 18px; font-weight: 800; }
.spacer { width: 42px; }

.profile-scroll-area { flex: 1; overflow-y: auto; padding-bottom: 50px; }

.user-hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
}

.avatar-wrapper { position: relative; margin-bottom: 25px; }
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
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
  position: relative;
  z-index: 2;
}

.avatar-shadow {
  position: absolute;
  bottom: -10px;
  width: 80%;
  height: 20px;
  background: #7b61ff;
  filter: blur(20px);
  opacity: 0.5;
  z-index: 1;
}

.name-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.name-display.clickable { cursor: pointer; }

.user-handle { font-size: 28px; font-weight: 900; letter-spacing: -0.5px; }
.edit-hint { font-size: 12px; color: #8e8e93; font-weight: 600; opacity: 0.7; }

.name-edit-field input {
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid #7b61ff;
  border-radius: 15px;
  padding: 12px 20px;
  color: white;
  text-align: center;
  font-size: 22px;
  font-weight: 800;
  outline: none;
}

.stats-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 30px;
  margin-top: 35px;
  background: rgba(255, 255, 255, 0.03);
  padding: 20px 40px;
  border-radius: 25px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  min-width: 200px;
}

.stat-item { display: flex; flex-direction: column; align-items: center; }
.val { font-size: 22px; font-weight: 900; color: #fff; }
.lab { font-size: 11px; color: #8e8e93; text-transform: uppercase; font-weight: 700; margin-top: 4px; }
.vertical-divider { width: 1px; height: 30px; background: rgba(255, 255, 255, 0.1); }

.characters-section { padding: 20px; }
.section-title { font-size: 12px; font-weight: 800; color: rgba(255, 255, 255, 0.3); text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 20px; }

.compact-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
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
  aspect-ratio: 1/1;
  border-radius: 18px;
  overflow: hidden;
  background: #1c1c1e;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.icon-img-box img { width: 100%; height: 100%; object-fit: cover; }

.tiny-name {
  font-size: 11px;
  font-weight: 700;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  width: 100%;
  color: rgba(255, 255, 255, 0.7);
}

.loading-container { display: flex; justify-content: center; padding-top: 100px; }
.spinner { width: 30px; height: 30px; border: 3px solid rgba(255, 255, 255, 0.1); border-top-color: #7b61ff; border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>