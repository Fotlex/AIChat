import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { User } from "@/types/index";
import { getUser, getSettingsInfo } from "@/api";
import apiClient from "@/api/apiClient";
import { useToast } from "@/composables/useToast";

export const useUserStore = defineStore("user", () => {
  const currentUser = ref<User | null>(null);
  const isLoading = ref<boolean>(false);
  const { showToast } = useToast();

  const llms = ref<any[]>([]);
  const myCharacters = ref<any[]>([]);
  const isSettingsLoaded = ref(false);

  const balance = computed(() => currentUser.value?.balance ?? 0);
  const canClaimBonus = computed(() => currentUser.value?.can_claim_daily_bonus ?? false);

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

  async function claimDailyBonus() {
    if (!currentUser.value || !currentUser.value.can_claim_daily_bonus) return;

    try {
      const response = await apiClient.post("/users/daily-bonus/claim/");

      if (response.status === 204) {
        currentUser.value.balance += 100;
        currentUser.value.can_claim_daily_bonus = false;
        showToast("Вы забрали ежедневную награду! +100 💎", "success");
      }
    } catch (e) {
      currentUser.value.can_claim_daily_bonus = false;
      showToast("Ошибка или награда уже получена", "error");
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
            currentUser.value.referrals_count = data.user.referrals_count;
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
        currentUser.value.referrals_count = data.user.referrals_count;
      }
      isSettingsLoaded.value = true;
    } catch (e) {}
  }

  return {
    currentUser,
    isLoading,
    balance,
    canClaimBonus,
    llms,
    myCharacters,
    isSettingsLoaded,
    fetchUser,
    claimDailyBonus,
    loadSettingsInfo,
  };
});
