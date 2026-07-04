<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";

const router = useRouter();
const errorMsg = ref("");

onMounted(async () => {
  const tg = (window as any).Telegram?.WebApp;
  
  if (tg && tg.initData) {
    tg.ready();
    tg.expand();

    try {
      const res = await axios.post("/api/v1/auth/telegram/", {
        initData: tg.initData,
      });

      localStorage.setItem("access_token", res.data.access);
      localStorage.setItem("refresh_token", res.data.refresh);
      router.push("/");
    } catch (e: any) {
      errorMsg.value = e.response?.data?.error || "Ошибка авторизации";
    }
  } else {
    errorMsg.value = "Пожалуйста, откройте приложение внутри Telegram.";
  }
});
</script>

<template>
  <div class="auth-wrapper">
    <div class="auth-card">
      <div class="logo">
        <i-local-crystal class="logo-icon" />
        <h2>AIChat</h2>
      </div>

      <div class="status-container">
        <div v-if="!errorMsg" class="loader">
          <div class="spinner"></div>
          <p>Вход через Telegram...</p>
        </div>
        <p v-else class="error-text">{{ errorMsg }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  width: 100vw;
  background: linear-gradient(160deg, #4c2a4e 0%, #2c2c40 100%);
}
.auth-card {
  background-color: rgba(26, 26, 26, 0.95);
  backdrop-filter: blur(10px);
  padding: 30px;
  border-radius: 20px;
  width: 90%;
  max-width: 400px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(80, 80, 80, 0.5);
}
.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 25px;
  color: white;
}
.logo-icon {
  width: 32px;
  height: 32px;
  color: #81b2ff;
}
.status-container {
  color: white;
  min-height: 80px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.loader {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}
.spinner {
  width: 30px;
  height: 30px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: #7b61ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
.error-text {
  color: #ff4d4d;
  font-size: 14px;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>