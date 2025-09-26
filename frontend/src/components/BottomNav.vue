<script setup lang="ts">

import HomeIcon from './icons/HomeIcon.vue';
import ProfileIcon from './icons/ProfileIcon.vue';
</script>

<template>
  <nav class="bottom-nav">
    <button class="nav-button active">
      <HomeIcon />
      <span>Главная</span>
    </button>
    <button class="nav-button">
      <ProfileIcon />
      <span>Профиль</span>
    </button>
  </nav>
</template>

<style scoped>
.bottom-nav { position: fixed; bottom: 0; left: 0; right: 0; height: 70px; background-color: rgba(26, 26, 26, 0.9); backdrop-filter: blur(10px); display: flex; justify-content: space-around; align-items: center; border-top: 1px solid #333; padding-bottom: env(safe-area-inset-bottom); z-index: 100; }
.nav-button { background: none; border: none; color: #8e8e93; display: flex; flex-direction: column; align-items: center; gap: 4px; font-size: 10px; }
.nav-button.active { color: #ffffff; }
</style>