<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useUserStore } from '@/store/user';
import { getSettingsInfo, updateProfile } from '@/api/userApi';
import router from "@/router";

const userStore = useUserStore();
const myCharacters = ref<any[]>([]);
const isEditing = ref(false);
const editName = ref("");
const isLoading = ref(true);
const error = ref("");

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
    error.value = e.response?.data?.error || "Ошибка при смене имени";
  }
};
</script>

<template>
  <div class="profile-page">
    <div class="nav-header">
      <button class="back-btn" @click="router.back()">✕</button>
      <span class="page-title">Ваш профиль</span>
    </div>

    <div v-if="isLoading" class="loader">
      <div class="spinner"></div>
    </div>

    <div v-else class="profile-body">
      <div class="profile-header">
        <div class="big-avatar">{{ editName[0]?.toUpperCase() }}</div>
        
        <div v-if="!isEditing" class="name-display">
          <h1>@{{ userStore.currentUser?.username }}</h1>
          <button class="edit-icon-btn" @click="isEditing = true">✎</button>
        </div>
        
        <div v-else class="name-edit-box">
          <input v-model="editName" @keyup.enter="saveName" auto-focus />
          <div class="edit-btns">
            <button class="save-btn" @click="saveName">✓</button>
            <button class="cancel-btn" @click="isEditing = false">✕</button>
          </div>
        </div>
        <p v-if="error" class="error-text">{{ error }}</p>

        <div class="balance-info">Баланс: {{ userStore.balance }} 💎</div>
      </div>

      <div class="chars-section">
        <div class="section-header">
          <h3>Мои персонажи ({{ myCharacters.length }})</h3>
        </div>
        
        <div v-if="myCharacters.length === 0" class="empty-state">
          Вы еще не создали ни одного персонажа
        </div>
        
        <div v-else class="chars-grid">
          <div v-for="c in myCharacters" :key="c.id" class="char-card" @click="router.push(`/chat/${c.id}`)">
            <div class="img-wrapper">
              <img :src="c.photo || '/default-avatar.png'" />
            </div>
            <div class="c-name">{{ c.name }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-page { padding: 0; color: white; background: #0e0e10; min-height: 100vh; }
.nav-header { display: flex; align-items: center; padding: 20px; gap: 15px; }
.back-btn { background: rgba(255,255,255,0.1); border: none; color: white; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; font-size: 18px; }
.page-title { font-weight: 700; font-size: 18px; }

.profile-header { display: flex; flex-direction: column; align-items: center; gap: 15px; padding: 20px 0 40px; background: linear-gradient(180deg, rgba(123, 97, 255, 0.1) 0%, transparent 100%); }
.big-avatar { width: 100px; height: 100px; border-radius: 50%; background: linear-gradient(135deg, #6366f1, #a855f7); display: flex; align-items: center; justify-content: center; font-size: 40px; font-weight: bold; box-shadow: 0 10px 20px rgba(0,0,0,0.3); }

.name-display { display: flex; align-items: center; gap: 10px; }
.name-display h1 { font-size: 24px; font-weight: 700; }
.edit-icon-btn { background: none; border: none; color: #8e8e93; font-size: 20px; cursor: pointer; }

.name-edit-box { display: flex; flex-direction: column; gap: 10px; align-items: center; }
.name-edit-box input { background: rgba(255,255,255,0.05); border: 1px solid #007aff; color: white; padding: 10px 15px; border-radius: 12px; font-size: 18px; text-align: center; outline: none; }
.edit-btns { display: flex; gap: 10px; }
.save-btn { background: #34c759; border: none; color: white; width: 40px; height: 40px; border-radius: 10px; font-size: 20px; }
.cancel-btn { background: #ff453a; border: none; color: white; width: 40px; height: 40px; border-radius: 10px; font-size: 20px; }
.error-text { color: #ff453a; font-size: 13px; margin: 0; }
.balance-info { background: rgba(129, 178, 255, 0.1); color: #81b2ff; padding: 6px 15px; border-radius: 20px; font-weight: 600; font-size: 14px; }

.chars-section { padding: 0 20px; }
.section-header h3 { color: #8e8e93; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 20px; }
.chars-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }
.char-card { cursor: pointer; }
.img-wrapper { width: 100%; aspect-ratio: 1/1; border-radius: 16px; overflow: hidden; background: #1c1c1e; }
.img-wrapper img { width: 100%; height: 100%; object-fit: cover; }
.c-name { font-size: 12px; text-align: center; margin-top: 8px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.empty-state { text-align: center; color: #444; padding: 40px 0; font-size: 14px; }
.loader { display: flex; justify-content: center; padding-top: 100px; }
.spinner { width: 30px; height: 30px; border: 3px solid rgba(255,255,255,0.1); border-top-color: #007aff; border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>