import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { User } from "@/types/index";
import { getUser } from "@/api";

export const useUserStore = defineStore("user", () => {
  const currentUser = ref<User | null>(null);
  const isLoading = ref<boolean>(false);
  const error = ref<string | null>(null);

  const balance = computed(() => currentUser.value?.balance ?? 0);
  const userFirstName = computed(
    () => currentUser.value?.first_name ?? "Гость"
  );

  async function fetchUser() {
    console.log("Store action: fetchUser вызван.");
    isLoading.value = true;
    error.value = null;

    try {
      const userData = await getUser();

      currentUser.value = userData;
      console.log(
        "Store state: данные пользователя обновлены.",
        currentUser.value
      );
    } catch (e: any) {
      const errorMessage =
        e.response?.data?.detail || e.message || "Произошла неизвестная ошибка";
      error.value = errorMessage;
      console.error("Не удалось загрузить данные пользователя:", errorMessage);
    } finally {
      isLoading.value = false;
    }
  }

  return {
    currentUser,
    isLoading,
    error,

    balance,
    userFirstName,

    fetchUser,
  };
});
