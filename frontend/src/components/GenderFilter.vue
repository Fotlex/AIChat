<script setup lang="ts">
import { computed } from "vue";
import { useCharactersStore } from "@/store/characters";

const store = useCharactersStore();

const gliderStyle = computed(() => {
  return {
    transform:
      store.activeGender === "F" ? "translateX(0%)" : "translateX(100%)",
  };
});
</script>

<template>
  <div class="filter-wrapper">
    <div class="gender-filter">
      <span class="glider" :style="gliderStyle"></span>
      <button
        :class="{ active: store.activeGender === 'F' }"
        @click="store.setGender('F')"
      >
        Девушки
      </button>
      <button
        :class="{ active: store.activeGender === 'M' }"
        @click="store.setGender('M')"
      >
        Парни
      </button>
    </div>
  </div>
</template>

<style scoped>
.filter-wrapper {
  padding: 10px 16px;
  width: 100%;
}
.gender-filter {
  display: flex;
  position: relative;
  background-color: #2c2c2e;
  border-radius: 12px;
  padding: 4px;
  width: 100%;
}
.gender-filter button {
  flex: 1;
  padding: 8px 0;
  background: none;
  border: none;
  color: #999;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  z-index: 2;
  transition: color 0.3s ease;
}
.gender-filter button.active {
  color: white;
}
.glider {
  position: absolute;
  top: 4px;
  left: 4px;
  height: calc(100% - 8px);
  width: calc((100% - 8px) / 2);
  background-color: #007aff;
  border-radius: 9px;
  transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  z-index: 1;
}
</style>
