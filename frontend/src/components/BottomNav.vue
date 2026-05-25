<script setup lang="ts">
import { navLinks } from "@/router/navigation";
</script>

<template>
  <nav class="bottom-nav">
    <div class="bottom-nav-inner">
      <router-link
        v-for="link in navLinks"
        :key="link.to"
        :to="link.to"
        class="nav-button"
        active-class="active"
      >
        <component :is="link.icon" />
        <span>{{ link.name }}</span>
      </router-link>
    </div>
  </nav>
</template>

<style scoped>
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: rgba(26, 26, 26, 0.9);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(80, 80, 80, 0.5);
  z-index: 100;
  padding-bottom: env(safe-area-inset-bottom);
}
.bottom-nav-inner {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  align-items: flex-start;
  padding-top: 8px;
  height: 70px;
  width: 100%;
  max-width: var(--app-max-width);
  margin: 0 auto;
}
.nav-button {
  background: none;
  border: none;
  color: #8e8e93;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  font-size: 10px;
  text-decoration: none;
  padding: 0 5px;
  transition: color 0.2s ease;
}
.nav-button :deep(svg) {
  width: 24px;
  height: 24px;
}
.nav-button.active {
  color: #ffffff;
}
</style>
