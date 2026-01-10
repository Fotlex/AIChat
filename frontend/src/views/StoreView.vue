    
<template>
  <div class="store-page">
    <!-- Показываем лоадер загрузки списка тарифов -->
    <div v-if="tariffStore.isLoading" class="loader">
      Загрузка тарифов...
    </div>

    <!-- Показываем ошибку, если есть -->
    <div v-else-if="tariffStore.error" class="error-message">
      {{ tariffStore.error }}
    </div>

    <!-- Сетка тарифов -->
    <div v-else-if="tariffStore.tariffs.length > 0" class="tariffs-grid">
      <TariffCard
        v-for="tariff in tariffStore.tariffs"
        :key="tariff.id"
        :tariff="tariff"
        @select="handleTariffSelect"
      />
    </div>
    
    <!-- Если пусто -->
    <div v-else class="empty-message">
      Тарифы не найдены.
    </div>

    <!-- Оверлей загрузки (появляется при нажатии на оплату) -->
    <div v-if="isProcessing" class="processing-overlay">
      <div class="spinner"></div>
      <span>Создание платежа...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useTariffStore } from '@/store/tariff';
import { createPayment } from '@/api/yookassaApi';
import TariffCard from '@/components/TariffCard.vue';
import type { Tariff } from '@/types';

const tariffStore = useTariffStore();
const isProcessing = ref(false);

onMounted(() => {
  if (tariffStore.tariffs.length === 0) {
    tariffStore.loadTariffs();
  }
});

async function handleTariffSelect(selectedTariff: Tariff) {
  if (isProcessing.value) return;
  
  isProcessing.value = true;

  try {
    const tgUser = window.Telegram?.WebApp?.initDataUnsafe?.user;
    const userEmail = tgUser 
      ? `${tgUser.id}@telegram.placeholder.com` 
      : 'unknown@example.com';

    const data = await createPayment(selectedTariff.id, userEmail);

    if (data.payment_url) {
      if (window.Telegram?.WebApp) {
        window.Telegram.WebApp.openLink(data.payment_url);
      } else {
        window.location.href = data.payment_url;
      }
    } else {
      alert('Ошибка: ссылка на оплату не получена.');
    }
  } catch (error) {
    console.error('Ошибка оплаты:', error);
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.showAlert('Не удалось создать платеж. Попробуйте позже.');
    } else {
      alert('Ошибка при создании платежа');
    }
  } finally {
    isProcessing.value = false;
  }
}
</script>

<style scoped>
.store-page {
  padding: 16px;
  max-width: 600px;
  margin: 0 auto;
  min-height: 100vh; /* Чтобы оверлей перекрывал весь экран */
}

.tariffs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 12px;
}

.loader, .error-message, .empty-message {
  color: #aaa;
  text-align: center;
  padding: 40px 20px;
}

.error-message {
  color: #ff453a;
}

/* Стили для оверлея загрузки */
.processing-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  color: white;
  gap: 15px;
  backdrop-filter: blur(3px);
}

.spinner {
  width: 30px;
  height: 30px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>

  