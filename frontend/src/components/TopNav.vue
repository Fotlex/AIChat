<script setup lang="ts">
import { useUserStore } from "@/store/user";

defineProps<{
  title: string;
}>();

const userStore = useUserStore();
</script>

<template>
  <header class="top-nav">
    <div class="top-nav-content">
      <h1 class="page-title">{{ title }}</h1>
      <div class="user-balance">
        <i-local-crystal class="balance-icon" />
        <span>{{ userStore.balance }}</span>
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
  height: calc(50px + env(safe-area-inset-top));
  padding-top: env(safe-area-inset-top);
  background-color: rgba(26, 26, 26, 0.9);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(80, 80, 80, 0.5);
  z-index: 100;
  color: white;
}

.top-nav-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 50px;
  padding: 0 16px;
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
