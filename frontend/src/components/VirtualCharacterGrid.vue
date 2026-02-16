<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useVirtualizer } from "@tanstack/vue-virtual";
import { useCharactersStore } from "@/store/characters";
import CharacterCard from "./CharacterCard.vue";
import { useRouter } from "vue-router";

const store = useCharactersStore();
const router = useRouter();

const parentRef = ref<HTMLElement | null>(null);

const chunkedItems = computed(() => store.chunkedItems);

const rowVirtualizer = useVirtualizer(
  computed(() => ({
    count: chunkedItems.value.length,
    getScrollElement: () => parentRef.value,
    estimateSize: () => 260,
    overscan: 4,
  }))
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
    if (!lastItem) return;
    if (lastItem.index >= chunkedItems.value.length - 2) {
      store.fetchCharacters();
    }
  },
);
</script>

<template>
  <div ref="parentRef" class="virtual-scroll-container">
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
  padding-bottom: 90px;
}

.virtual-row {
  padding-bottom: 12px;
  box-sizing: border-box;
}

.row-cols {
  display: flex;
  gap: 12px;
  height: 100%;
}

.row-item {
  flex: 1;
  min-width: 0;
}

.bottom-loader {
  height: 50px;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 10px;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s infinite linear;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
