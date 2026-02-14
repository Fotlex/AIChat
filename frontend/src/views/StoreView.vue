<template>
  <div class="store-page">
    <div v-if="tariffStore.isLoading" class="loader">
      Загрузка тарифов...
    </div>

    <div v-else-if="tariffStore.error" class="error-message">
      {{ tariffStore.error }}
    </div>

    <div v-else-if="tariffStore.tariffs.length > 0" class="tariffs-grid">
      <TariffCard
        v-for="tariff in tariffStore.tariffs"
        :key="tariff.id"
        :tariff="tariff"
        @select="handleTariffSelect"
      />
    </div>
    
    <div v-else class="empty-message">
      Тарифы не найдены.
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useTariffStore } from '@/store/tariff';
import TariffCard from '@/components/TariffCard.vue';
import type { Tariff } from '@/types';

const tariffStore = useTariffStore();

onMounted(() => {
  if (tariffStore.tariffs.length === 0) {
    tariffStore.loadTariffs();
  }
});

function handleTariffSelect(selectedTariff: Tariff) {
  tariffStore.selectTariff(selectedTariff);
}
</script>

<style scoped>
.store-page {
  padding: 16px;
  max-width: 600px;
  margin: 0 auto;
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
</style>