<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { createCharacterApi } from "@/api/charactersApi";
import { useUserStore } from "@/store/user";

const router = useRouter();
const userStore = useUserStore();

const formData = ref({
  name: "",
  tagline: "",
  system_prompt: "",
  greeting_message: "",
  avatar: "" as string | null,
});
const isLoading = ref(false);
const errorMsg = ref("");

const onFileChange = (e: Event) => {
  const file = (e.target as HTMLInputElement).files?.[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = (ev) => {
    formData.value.avatar = ev.target?.result as string;
  };
  reader.readAsDataURL(file);
};

const submit = async () => {
  if (!formData.value.name || !formData.value.system_prompt) {
    errorMsg.value = "Имя и системный промпт обязательны";
    return;
  }

  isLoading.value = true;
  errorMsg.value = "";
  try {
    const res = await createCharacterApi(formData.value);

    if (userStore.currentUser) {
      userStore.currentUser.balance = res.new_balance;
    }
    userStore.isSettingsLoaded = false;
    router.push("/settings");
  } catch (e: any) {
    errorMsg.value = e.response?.data?.error || "Ошибка создания";
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="create-container">
    <div class="avatar-upload">
      <label class="avatar-circle">
        <img v-if="formData.avatar" :src="formData.avatar" />
        <span v-else>+ Фото</span>
        <input type="file" accept="image/*" @change="onFileChange" hidden />
      </label>
    </div>

    <div class="form-group">
      <label>Имя персонажа *</label>
      <input v-model="formData.name" placeholder="Джон Уик" />
    </div>

    <div class="form-group">
      <label>Краткое описание (Tagline)</label>
      <input
        v-model="formData.tagline"
        placeholder="Мужчина, который любит собак"
      />
    </div>

    <div class="form-group">
      <label>Системный промпт (Инструкция для ИИ) *</label>
      <textarea
        v-model="formData.system_prompt"
        rows="4"
        placeholder="Ты Джон Уик. Говори коротко..."
      ></textarea>
    </div>

    <div class="form-group">
      <label>Приветственное сообщение</label>
      <textarea
        v-model="formData.greeting_message"
        rows="2"
        placeholder="Давно не виделись..."
      ></textarea>
    </div>

    <p v-if="errorMsg" class="error-text">{{ errorMsg }}</p>

    <button class="btn-submit" @click="submit" :disabled="isLoading">
      {{ isLoading ? "Создание..." : "Создать персонажа (100 💎)" }}
    </button>
  </div>
</template>

<style scoped>
.create-container {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding-bottom: 30px;
}
.avatar-upload {
  display: flex;
  justify-content: center;
}
.avatar-circle {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  border: 2px dashed rgba(255, 255, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #8e8e93;
  cursor: pointer;
  overflow: hidden;
}
.avatar-circle img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.form-group label {
  font-size: 13px;
  color: #8e8e93;
  font-weight: 600;
}
.form-group input,
.form-group textarea {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 14px;
  border-radius: 12px;
  color: white;
  font-size: 15px;
  outline: none;
  resize: none;
}
.btn-submit {
  background: linear-gradient(135deg, #7b61ff, #6366f1);
  color: white;
  border: none;
  padding: 16px;
  border-radius: 16px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
}
.btn-submit:disabled {
  opacity: 0.7;
}
.error-text {
  color: #ff4d4d;
  font-size: 14px;
  text-align: center;
}
</style>
