<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useTariffStore } from "@/store/tariff";
import { createPayment } from "@/api/tariffApi";
import TariffCard from "@/components/TariffCard.vue";

const tariffStore = useTariffStore();
const isPaying = ref(false);

onMounted(() => {
  tariffStore.loadTariffs();
});

const handleSelectTariff = async (tariff: any) => {
  if (isPaying.value) return;
  isPaying.value = true;
  try {
    const res = await createPayment(tariff.id);
    window.location.href = res.payment_url;
  } catch (e) {
    alert("Ошибка при создании платежа");
  } finally {
    isPaying.value = false;
  }
};
</script>

<template>
  <div class="store-container">
    <div
      v-if="tariffStore.isLoading && tariffStore.tariffs.length === 0"
      class="loader"
    >
      <div class="spinner"></div>
    </div>

    <div v-else class="tariffs-grid">
      <TariffCard
        v-for="(t, index) in tariffStore.tariffs"
        :key="t.id"
        :tariff="t"
        :isPopular="index === 1"
        @select="handleSelectTariff"
      />
    </div>
  </div>
</template>

<style scoped>
.store-container {
  padding: 16px;
  height: 100%;
  overflow-y: auto;
}
.tariffs-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  padding-bottom: 20px;
}
.loader {
  display: flex;
  justify-content: center;
  padding-top: 100px;
}
.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: #007aff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
