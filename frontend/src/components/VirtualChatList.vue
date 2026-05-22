<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import { useChatsStore } from "@/store/chats";
import { useRouter } from "vue-router";
import { useVirtualizer } from "@tanstack/vue-virtual";

const chatsStore = useChatsStore();
const router = useRouter();
const parentRef = ref<HTMLElement | null>(null);

onMounted(() => {
  if (!chatsStore.isChatsLoaded) {
    chatsStore.fetchChatsList();
  }
});

const openChat = (characterId: number) => {
  router.push({ name: "chat", params: { id: characterId } });
};

const rowVirtualizer = useVirtualizer(
  computed(() => ({
    count: chatsStore.chatsList.length,
    getScrollElement: () => parentRef.value,
    estimateSize: () => 76,
    overscan: 5,
  })),
);

const virtualRows = computed(() => rowVirtualizer.value.getVirtualItems());
const totalSize = computed(() => rowVirtualizer.value.getTotalSize());

watch(
  () => virtualRows.value,
  (newRows) => {
    if (!newRows.length) return;
    const lastItem = newRows[newRows.length - 1];
    if (lastItem && lastItem.index >= chatsStore.chatsList.length - 3) {
      chatsStore.fetchChatsList(true);
    }
  },
);
</script>

<template>
  <div ref="parentRef" class="virtual-scroll-container">
    <div
      v-if="!chatsStore.isChatsLoaded && chatsStore.isChatsLoading"
      class="status-message"
    >
      Загрузка чатов...
    </div>

    <div
      v-else-if="chatsStore.isChatsLoaded && chatsStore.chatsList.length === 0"
      class="status-message"
    >
      У вас пока нет чатов. Начните общение с персонажем!
    </div>

    <div v-else class="virtual-sizer" :style="{ height: `${totalSize}px` }">
      <div
        v-for="virtualRow in virtualRows"
        :key="virtualRow.key.toString()"
        class="virtual-row"
        :style="{
          transform: `translateY(${virtualRow.start}px)`,
          height: `${virtualRow.size}px`,
        }"
      >
        <template v-if="chatsStore.chatsList[virtualRow.index]">
          <div
            class="chat-item"
            @click="
              openChat(chatsStore.chatsList[virtualRow.index]!.character.id)
            "
          >
            <img
              :src="
                chatsStore.chatsList[virtualRow.index]!.character.photo ||
                '/default-avatar.png'
              "
              class="avatar"
            />
            <div class="chat-info">
              <div class="name">
                {{ chatsStore.chatsList[virtualRow.index]!.character.name }}
              </div>
              <div class="last-message">
                {{
                  chatsStore.chatsList[virtualRow.index]!.last_message
                    ?.content || "Нет сообщений"
                }}
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>

    <div
      v-if="chatsStore.chatsNextCursor && chatsStore.isChatsLoading"
      class="bottom-loader"
    >
      <div class="spinner"></div>
    </div>
  </div>
</template>

<style scoped>
.virtual-scroll-container {
  height: 100%;
  width: 100%;
  overflow-y: auto;
  padding: 16px;
  -webkit-overflow-scrolling: touch;
}

.virtual-sizer {
  position: relative;
  width: 100%;
}

.virtual-row {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  padding-bottom: 12px;
}

.chat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  cursor: pointer;
  height: 100%;
  box-sizing: border-box;
}

.avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
}

.chat-info {
  flex-grow: 1;
  overflow: hidden;
}

.name {
  font-weight: 600;
  font-size: 16px;
  color: #fff;
}

.last-message {
  font-size: 14px;
  color: #8e8e93;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.status-message {
  color: #8e8e93;
  text-align: center;
  padding-top: 50px;
}

.bottom-loader {
  display: flex;
  justify-content: center;
  padding: 20px 0;
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
