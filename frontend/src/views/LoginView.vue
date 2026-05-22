<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";

const router = useRouter();
const isLogin = ref(true);
const username = ref("");
const password = ref("");
const errorMsg = ref("");
const isLoading = ref(false);

const submit = async () => {
  if (!username.value || !password.value) {
    errorMsg.value = "Заполните все поля";
    return;
  }

  isLoading.value = true;
  errorMsg.value = "";

  try {
    const endpoint = isLogin.value
      ? "/api/v1/auth/login/"
      : "/api/v1/auth/register/";
    const res = await axios.post(endpoint, {
      username: username.value,
      password: password.value,
    });

    localStorage.setItem("access_token", res.data.access);

    router.push("/");
  } catch (e: any) {
    errorMsg.value = e.response?.data?.error || "Произошла ошибка";
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="auth-wrapper">
    <div class="auth-card">
      <div class="logo">
        <i-local-crystal class="logo-icon" />
        <h2>AIChat</h2>
      </div>

      <div class="tabs">
        <button :class="{ active: isLogin }" @click="isLogin = true">
          Вход
        </button>
        <button :class="{ active: !isLogin }" @click="isLogin = false">
          Регистрация
        </button>
      </div>

      <form @submit.prevent="submit" class="auth-form">
        <input
          v-model="username"
          type="text"
          placeholder="Логин"
          class="input-field"
        />
        <input
          v-model="password"
          type="password"
          placeholder="Пароль"
          class="input-field"
        />

        <p v-if="errorMsg" class="error-text">{{ errorMsg }}</p>

        <button type="submit" class="submit-btn" :disabled="isLoading">
          {{
            isLoading ? "Загрузка..." : isLogin ? "Войти" : "Создать аккаунт"
          }}
        </button>
      </form>
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
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(80, 80, 80, 0.5);
}
.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 25px;
}
.logo-icon {
  width: 32px;
  height: 32px;
  color: #81b2ff;
}
.tabs {
  display: flex;
  background: #2c2c2e;
  border-radius: 12px;
  padding: 4px;
  margin-bottom: 20px;
}
.tabs button {
  flex: 1;
  padding: 10px 0;
  background: none;
  border: none;
  color: #999;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}
.tabs button.active {
  background: #007aff;
  color: white;
}
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.input-field {
  background: #1c1c1e;
  border: 1px solid #3a3a3c;
  color: white;
  padding: 14px;
  border-radius: 12px;
  font-size: 15px;
  outline: none;
}
.input-field:focus {
  border-color: #007aff;
}
.submit-btn {
  background: #7b61ff;
  color: white;
  border: none;
  padding: 14px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  margin-top: 10px;
  cursor: pointer;
}
.submit-btn:disabled {
  opacity: 0.7;
}
.error-text {
  color: #ff4d4d;
  font-size: 13px;
  text-align: center;
  margin: 0;
}
</style>
