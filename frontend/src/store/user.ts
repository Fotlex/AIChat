import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { User } from "@/types/index";
import { getUser, getSettingsInfo } from "@/api";

export const useUserStore = defineStore("user", () => {
  const currentUser = ref<User | null>(null);
  const isLoading = ref<boolean>(false);

  const llms = ref<any[]>([]);
  const myCharacters = ref<any[]>([]);
  const isSettingsLoaded = ref(false);

  const balance = computed(() => currentUser.value?.balance ?? 0);

  async function fetchUser() {
    isLoading.value = true;
    try {
      const userData = await getUser();
      const llm_id = currentUser.value?.preferred_llm_id;
      currentUser.value = { ...userData, preferred_llm_id: llm_id };
    } catch (e) {
    } finally {
      isLoading.value = false;
    }
  }

  async function loadSettingsInfo(force = false) {
    if (isSettingsLoaded.value && !force) {
      getSettingsInfo()
        .then((data) => {
          llms.value = data.llms;
          myCharacters.value = data.my_characters;
          if (currentUser.value) {
            currentUser.value.preferred_llm_id = data.user.preferred_llm_id;
            currentUser.value.username = data.user.username;
          }
        })
        .catch(() => {});
      return;
    }

    try {
      const data = await getSettingsInfo();
      llms.value = data.llms;
      myCharacters.value = data.my_characters;
      if (currentUser.value) {
        currentUser.value.preferred_llm_id = data.user.preferred_llm_id;
        currentUser.value.username = data.user.username;
      }
      isSettingsLoaded.value = true;
    } catch (e) {}
  }

  return {
    currentUser,
    isLoading,
    balance,
    llms,
    myCharacters,
    isSettingsLoaded,
    fetchUser,
    loadSettingsInfo,
  };
});
