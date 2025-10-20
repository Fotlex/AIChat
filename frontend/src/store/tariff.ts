import { defineStore } from "pinia";
import { ref } from "vue";
import type { Tariff } from "@/types";
import { getTariffs } from "@/api";

export const useTariffStore = defineStore("tariffs", () => {
  const tariffs = ref<Tariff[]>([]);
  const isLoading = ref<boolean>(false);
  const error = ref<string | null>(null);

  async function loadTariffs() {
    isLoading.value = true;
    error.value = null;
    try {
      const data = await getTariffs();
      tariffs.value = data;
    } catch (e: any) {
      error.value = "Не удалось загрузить список тарифов.";
    } finally {
      isLoading.value = false;
    }
  }

  function selectTariff(selectedTariff: Tariff) {
    console.log("Выбран тариф:", selectedTariff);
    alert(
      `Вы выбрали тариф "${selectedTariff.name}" за ${selectedTariff.cost} руб.`
    );
  }

  return {
    tariffs,
    isLoading,
    error,
    loadTariffs,
    selectTariff,
  };
});
