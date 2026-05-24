import { defineStore } from "pinia";
import { ref } from "vue";
import type { Tariff } from "@/types";
import { getTariffs } from "@/api";

export const useTariffStore = defineStore("tariffs", () => {
  const tariffs = ref<Tariff[]>([]);
  const isLoading = ref<boolean>(false);

  async function loadTariffs(force = false) {
    if (tariffs.value.length > 0 && !force) {
      getTariffs()
        .then((data) => (tariffs.value = data))
        .catch(() => {});
      return;
    }

    isLoading.value = true;
    try {
      tariffs.value = await getTariffs();
    } catch (e: any) {
      console.error("Ошибка загрузки тарифов", e);
    } finally {
      isLoading.value = false;
    }
  }

  return { tariffs, isLoading, loadTariffs };
});
