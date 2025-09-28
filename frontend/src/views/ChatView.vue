<script setup lang="ts">
import { useRoute } from "vue-router";
const route = useRoute();
</script>

<template>
  <div class="page-placeholder">
    <h1>Страница чата с персонажем ID: {{ route.params.id }}</h1>
    <p>Здесь BlankLayout (без BottomNav)</p>
    <router-link to="/">Назад</router-link>
  </div>
</template>

<style scoped>
.page-placeholder {
  padding: 20px;
  color: white;
}
</style>
