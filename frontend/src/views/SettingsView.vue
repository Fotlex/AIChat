<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useUserStore } from "@/store/user";
import { useTelegram } from "@/composables/useTelegram";
import { updatePreferredLLm, redeemPromocode } from "@/api/userApi";
import router from "@/router";

const userStore = useUserStore();
const { openLink } = useTelegram();

const isModelsExpanded = ref(false);
const promoCode = ref("");
const promoStatus = ref({ text: "", isError: false });
const copyStatus = ref("Скопировать");

const isLoading = computed(() => !userStore.isSettingsLoaded);

const botBaseLink = import.meta.env.VITE_TELEGRAM_BOT_LINK;

const referralLink = computed(() => {
  const userId = userStore.currentUser?.id;
  return userId ? `${botBaseLink}?startapp=ref_${userId}` : "";
});

const selectedModel = computed(() => {
  return (
    userStore.llms.find(
      (l) => l.id === userStore.currentUser?.preferred_llm_id,
    ) || null
  );
});

const copyToClipboard = async () => {
  if (!referralLink.value) return;

  try {
    await navigator.clipboard.writeText(referralLink.value);
    copyStatus.value = "Скопировано✅";
    setTimeout(() => {
      copyStatus.value = "Скопировать";
    }, 2000);
  } catch (err) {
    copyStatus.value = "Ошибка ❌";
  }
};

const shareReferralLink = () => {
  if (!referralLink.value) return;

  const baseUrl = "https://t.me/share/url";
  const urlParam = `url=${encodeURIComponent(referralLink.value)}`;
  const textParam = `text=${encodeURIComponent("Присоединяйся к AIChat по моей ссылке! 💎")}`;

  openLink(`${baseUrl}?${urlParam}&${textParam}`);
};

onMounted(() => {
  userStore.loadSettingsInfo();
});

const toggleModels = () => {
  isModelsExpanded.value = !isModelsExpanded.value;
};

const handleModelChange = async (id: number) => {
  if (userStore.currentUser) {
    userStore.currentUser.preferred_llm_id = id;
  }
  await updatePreferredLLm(id);
  isModelsExpanded.value = false;
};

const handleRedeem = async () => {
  if (!promoCode.value.trim()) return;
  try {
    const res = await redeemPromocode(promoCode.value);
    promoStatus.value = { text: res.message, isError: false };
    promoCode.value = "";
    await userStore.fetchUser();
  } catch (e: any) {
    promoStatus.value = {
      text: e.response?.data?.error || "Ошибка",
      isError: true,
    };
  }
};

const openProfile = () => {
  const id = userStore.currentUser?.id;
  if (id) {
    router.push({ name: "profile", params: { id } });
  }
};

const logout = () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  router.push("/login");
};
</script>

<template>
  <div class="settings-container">
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
    </div>

    <div v-else class="settings-content">
      <div class="settings-group">
        <div class="group-title">Аккаунт</div>
        <div class="profile-card" @click="openProfile">
          <div class="avatar-circle">
            {{ userStore.currentUser?.username?.[0]?.toUpperCase() }}
          </div>
          <div class="profile-main">
            <div class="user-header">
              <div class="username">@{{ userStore.currentUser?.username }}</div>
              <div class="balance-tag">
                <span>{{ userStore.balance }} 💎</span>
              </div>
            </div>
            <div class="open-profile-btn">Открыть профиль →</div>
          </div>
        </div>
      </div>

      <div class="settings-group">
        <div class="group-title">Реферальная программа</div>
        <div class="referral-card">
          <div class="ref-stats">
            <span class="ref-label">Приглашено друзей:</span>
            <span class="ref-count">{{
              userStore.currentUser?.referrals_count ?? 0
            }}</span>
          </div>
          <div class="ref-action-zone">
            <input
              type="text"
              readonly
              :value="referralLink"
              class="ref-link-input"
              @click="(e) => (e.target as HTMLInputElement).select()"
            />
            <div class="ref-buttons">
              <button class="btn-action copy" @click="copyToClipboard">
                {{ copyStatus }}
              </button>
              <button class="btn-action share" @click="shareReferralLink">
                Поделиться
              </button>
            </div>
          </div>
          <p class="ref-hint">
            За каждого приглашенного друга вы получаете 100 💎
          </p>
        </div>
      </div>

      <div class="settings-group">
        <div class="group-title">Текущая модель</div>
        <div class="accordion" :class="{ 'is-open': isModelsExpanded }">
          <div class="accordion-header" @click="toggleModels">
            <div class="current-selection">
              <span class="model-display-name">{{
                selectedModel?.name || "Не выбрана"
              }}</span>
            </div>
            <div class="chevron">
              <span v-if="!isModelsExpanded">▼</span>
              <span v-else>▲</span>
            </div>
          </div>

          <div class="accordion-content">
            <div class="model-options">
              <div
                v-for="llm in userStore.llms"
                :key="llm.id"
                class="model-option-row"
                :class="{
                  'is-selected':
                    userStore.currentUser?.preferred_llm_id === llm.id,
                }"
                @click="handleModelChange(llm.id)"
              >
                <div class="option-info">
                  <div class="option-name">{{ llm.name }}</div>
                  <div class="option-price">
                    {{ llm.cost_per_request }} 💎 за сообщение
                  </div>
                </div>
                <div
                  class="option-check"
                  v-if="userStore.currentUser?.preferred_llm_id === llm.id"
                >
                  <i-local-check />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="settings-group">
        <div class="group-title">Бонусы</div>
        <div class="promo-container">
          <div class="promo-input-box">
            <input
              v-model="promoCode"
              placeholder="Промокод"
              @keyup.enter="handleRedeem"
            />
            <button @click="handleRedeem" :disabled="!promoCode.trim()">
              ОК
            </button>
          </div>
          <p
            v-if="promoStatus.text"
            :class="['promo-status', { error: promoStatus.isError }]"
          >
            {{ promoStatus.text }}
          </p>
        </div>
      </div>

      <div class="settings-group actions">
        <button class="btn-logout" @click="logout">Выйти из системы</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.settings-container {
  padding: 24px 16px;
  padding-bottom: 100px;
}
.settings-content {
  display: flex;
  flex-direction: column;
  gap: 32px;
}
.settings-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.group-title {
  font-size: 12px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.4);
  text-transform: uppercase;
  letter-spacing: 1px;
  padding-left: 4px;
}
.profile-card {
  background: rgba(255, 255, 255, 0.06);
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 20px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  cursor: pointer;
  transition: transform 0.1s;
}
.profile-card:active {
  transform: scale(0.98);
}
.avatar-circle {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  font-weight: 800;
  color: white;
  flex-shrink: 0;
}
.profile-main {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.user-header {
  display: flex;
  align-items: center;
  gap: 12px;
}
.username {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
}
.balance-tag {
  color: #81b2ff;
  font-size: 14px;
  font-weight: 600;
  background: rgba(129, 178, 255, 0.1);
  padding: 2px 8px;
  border-radius: 8px;
}
.open-profile-btn {
  font-size: 12px;
  color: #fff;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.15);
  padding: 6px 12px;
  border-radius: 12px;
  display: inline-block;
  margin-top: 6px;
  width: max-content;
  transition: background 0.2s;
}
.profile-card:hover .open-profile-btn {
  background: rgba(255, 255, 255, 0.25);
}

.referral-card {
  background: rgba(255, 255, 255, 0.06);
  border-radius: 20px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}
.ref-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.ref-label {
  font-size: 15px;
  color: #fff;
  font-weight: 500;
}
.ref-count {
  font-size: 18px;
  font-weight: 800;
  color: #34c759;
  background: rgba(52, 199, 89, 0.1);
  padding: 4px 12px;
  border-radius: 10px;
}
.ref-action-zone {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.ref-link-input {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 12px;
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
  outline: none;
  text-overflow: ellipsis;
  white-space: nowrap;
  overflow: hidden;
  cursor: pointer;
}
.ref-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.btn-action {
  color: #fff;
  border: none;
  padding: 14px;
  border-radius: 14px;
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
  transition:
    background 0.2s,
    transform 0.1s;
}
.btn-action:active {
  transform: scale(0.98);
}
.btn-action.copy {
  background: rgba(255, 255, 255, 0.1);
}
.btn-action.copy:hover {
  background: rgba(255, 255, 255, 0.15);
}
.btn-action.share {
  background: #007aff;
}
.btn-action.share:hover {
  background: #0069d9;
}
.ref-hint {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.35);
  text-align: center;
}

.accordion {
  background: rgba(255, 255, 255, 0.06);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  overflow: hidden;
}
.accordion-header {
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}
.model-display-name {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}
.chevron {
  color: rgba(255, 255, 255, 0.3);
  font-size: 12px;
}
.accordion-content {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease-out;
  background: rgba(0, 0, 0, 0.1);
}
.accordion.is-open .accordion-content {
  max-height: 500px;
}
.model-option-row {
  padding: 14px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
  cursor: pointer;
}
.model-option-row:last-child {
  border-bottom: none;
}
.model-option-row.is-selected {
  background: rgba(0, 122, 255, 0.1);
  color: #007aff;
}
.option-name {
  font-size: 15px;
  font-weight: 600;
  color: #fff;
}
.option-price {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}
.option-check {
  color: #007aff;
}
.promo-container {
  background: rgba(255, 255, 255, 0.06);
  padding: 20px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}
.promo-input-box {
  display: flex;
  gap: 10px;
}
.promo-input-box input {
  flex: 1;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 14px;
  padding: 12px 16px;
  color: #fff;
  font-size: 15px;
  outline: none;
}
.promo-input-box button {
  background: #007aff;
  color: #fff;
  border: none;
  padding: 0 20px;
  border-radius: 14px;
  font-weight: 700;
  cursor: pointer;
}
.promo-status {
  margin-top: 12px;
  font-size: 13px;
  color: #34c759;
  text-align: center;
}
.promo-status.error {
  color: #ff453a;
}
.btn-logout {
  background: rgba(255, 69, 58, 0.1);
  color: #ff453a;
  border: 1px solid rgba(255, 69, 58, 0.2);
  padding: 16px;
  border-radius: 18px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  width: 100%;
}
.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
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
