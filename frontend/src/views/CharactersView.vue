<script setup lang="ts">
import VirtualCharacterGrid from "@/components/VirtualCharacterGrid.vue";
</script>

<template>
  <div class="view-container">
    <VirtualCharacterGrid />
  </div>
</template>

<style scoped>
.view-container {
  height: 100%;
  width: 100%;
  overflow: hidden;
}
</style>
