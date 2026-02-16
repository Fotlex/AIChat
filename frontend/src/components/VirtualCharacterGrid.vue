<script setup lang="ts">
import { computed, ref, watch, onMounted } from "vue";
import { useVirtualizer } from "@tanstack/vue-virtual";
import { useCharactersStore } from "@/store/characters";
import CharacterCard from "./CharacterCard.vue";
import GenderFilter from "./GenderFilter.vue";
import SortDropdown from "./SortDropdown.vue";
import { useRouter } from "vue-router";

const store = useCharactersStore();
const router = useRouter();

const parentRef = ref<HTMLElement | null>(null);
const chunkedItems = computed(() => store.chunkedItems);

onMounted(() => {
  if (store.currentList.items.length === 0) {
    store.fetchCharacters();
  }
});

const rowVirtualizer = useVirtualizer(
  computed(() => ({
    count: chunkedItems.value.length,
    getScrollElement: () => parentRef.value,
    estimateSize: () => 260,
    overscan: 5,
    scrollMargin: 10,
  })),
);

const virtualRows = computed(() => rowVirtualizer.value.getVirtualItems());
const totalSize = computed(() => rowVirtualizer.value.getTotalSize());

const handleSelect = (id: number) => {
  router.push({ name: "chat", params: { id } });
};

watch(
  () => rowVirtualizer.value.getVirtualItems(),
  (virtualItems) => {
    if (!virtualItems.length) return;
    const lastItem = virtualItems[virtualItems.length - 1];
    if (lastItem && lastItem.index >= chunkedItems.value.length - 2) {
      store.fetchCharacters();
    }
  },
);
</script>

<template>
  <div ref="parentRef" class="virtual-scroll-container">
    <div class="scrolling-header">
      <GenderFilter />
      <SortDropdown />
    </div>

    <div
      class="virtual-sizer"
      :style="{
        height: `${totalSize}px`,
        width: '100%',
        position: 'relative',
      }"
    >
      <div
        v-for="virtualRow in virtualRows"
        :key="virtualRow.key.toString()"
        class="virtual-row"
        :style="{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: `${virtualRow.size}px`,
          transform: `translateY(${virtualRow.start}px)`,
        }"
      >
        <div class="row-cols">
          <CharacterCard
            class="row-item"
            :character="chunkedItems[virtualRow.index]?.[0] ?? null"
            @select="handleSelect"
          />
          <CharacterCard
            class="row-item"
            :character="chunkedItems[virtualRow.index]?.[1] ?? null"
            @select="handleSelect"
          />
        </div>
      </div>
    </div>

    <div v-if="store.currentList.isLoading" class="bottom-loader">
      <div class="spinner"></div>
    </div>
  </div>
</template>

<style scoped>
.virtual-scroll-container {
  height: 100%;
  width: 100%;
  overflow-y: auto;
  padding: 0 16px;
  -webkit-overflow-scrolling: touch;
}

.scrolling-header {
  width: 100%;
  min-height: 85px;
  background: transparent;
  display: flex;
  flex-direction: column;
}

.virtual-sizer {
  width: 100%;
}

.virtual-row {
  padding-bottom: 12px;
  box-sizing: border-box;
}

.row-cols {
  display: flex;
  gap: 12px;
  height: 100%;
  width: 100%;
}

.row-item {
  flex: 1;
  min-width: 0;
}

.bottom-loader {
  height: 60px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 90px;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-top-color: #007aff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
