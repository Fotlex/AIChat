<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import DefaultLayout from "@/layouts/DefaultLayout.vue";
import BlankLayout from "@/layouts/BlankLayout.vue";
import { useToast } from "@/composables/useToast";

const route = useRoute();
const { toasts } = useToast();

const layouts = {
  DefaultLayout,
  BlankLayout,
};

const layoutComponent = computed(() => {
  const layoutName = route.meta.layout as keyof typeof layouts | undefined;
  return layoutName && layouts[layoutName] ? layouts[layoutName] : BlankLayout;
});
</script>

<template>
  <component :is="layoutComponent"></component>

  <teleport to="body">
    <div class="toast-container">
      <transition-group name="toast">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          :class="['toast-item', toast.type]"
        >
          {{ toast.message }}
        </div>
      </transition-group>
    </div>
  </teleport>
</template>

<style>
.toast-container {
  position: fixed;
  top: calc(70px + env(safe-area-inset-top));
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 8px;
  pointer-events: none;
  width: 90%;
  max-width: 320px;
}
.toast-item {
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  text-align: center;
  backdrop-filter: blur(8px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  will-change: opacity, transform;
}
.toast-item.success {
  background-color: rgba(52, 199, 89, 0.9);
  color: white;
  border: 1px solid rgba(52, 199, 89, 0.2);
}
.toast-item.error {
  background-color: rgba(255, 69, 58, 0.9);
  color: white;
  border: 1px solid rgba(255, 69, 58, 0.2);
}

.toast-enter-active,
.toast-leave-active {
  transition:
    opacity 0.25s ease,
    transform 0.25s ease;
}
.toast-enter-from {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}
.toast-leave-to {
  opacity: 0;
  transform: translateY(-5px) scale(0.95);
}
</style>
