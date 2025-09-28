<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import DefaultLayout from "@/layouts/DefaultLayout.vue";
import BlankLayout from "@/layouts/BlankLayout.vue";

const route = useRoute();

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
  <component :is="layoutComponent"> </component>
</template>

<style></style>
