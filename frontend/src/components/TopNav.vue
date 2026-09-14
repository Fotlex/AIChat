<script setup lang="ts">
import { onMounted } from "vue";
import { useUserStore } from "@/store/user";

defineProps<{
  title: string;
}>();

const userStore = useUserStore();
onMounted(() => {
  userStore.fetchUser();
});
</script>

<template>
  <header class="top-nav">
    <div class="top-nav-inner">
      <h1 class="page-title">{{ title }}</h1>

      <div class="header-right">
        <button
          v-if="userStore.canClaimBonus"
          class="daily-bonus-btn bounce-animation"
          @click="userStore.claimDailyBonus"
          aria-label="Забрать бонус"
        >
          🎁
        </button>

        <div class="user-balance">
          <i-local-crystal class="balance-icon" />
          <span>{{ userStore.balance }}</span>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
.top-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background-color: rgba(26, 26, 26, 0.9);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(80, 80, 80, 0.5);
  z-index: 100;
  color: white;
  padding-top: env(safe-area-inset-top);
}
.top-nav-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 50px;
  padding: 0 16px;
  width: 100%;
  max-width: var(--app-max-width);
  margin: 0 auto;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.daily-bonus-btn {
  background: rgba(255, 215, 0, 0.15);
  border: 1px solid rgba(255, 215, 0, 0.3);
  font-size: 20px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  outline: none;
  -webkit-tap-highlight-color: transparent;
  will-change: transform;
}

.bounce-animation {
  animation: jump 2.5s infinite ease-in-out;
}

@keyframes jump {
  0%,
  20%,
  50%,
  80%,
  100% {
    transform: translate3d(0, 0, 0) scale(1);
  }
  40% {
    transform: translate3d(0, -6px, 0) scale(1.1);
  }
  60% {
    transform: translate3d(0, -3px, 0) scale(1.05);
  }
}

.page-title {
  font-size: 18px;
  font-weight: 600;
}
.user-balance {
  display: flex;
  align-items: center;
  gap: 6px;
  background-color: rgba(255, 255, 255, 0.1);
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 16px;
  font-weight: 500;
}
.balance-icon {
  width: 18px;
  height: 18px;
  color: #a9a9b2;
}
.balance-icon :deep(path) {
  stroke: #81b2ff;
}
</style>
