<script setup lang="ts">
import { ref, onMounted, computed, watch, nextTick } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useVirtualizer } from "@tanstack/vue-virtual";
import { useChatsStore } from "@/store/chats";
import { useUserStore } from "@/store/user";
import { useCharactersStore } from "@/store/characters";
import ChatHeader from "@/components/ChatHeader.vue";

const route = useRoute();
const router = useRouter();
const chatsStore = useChatsStore();
const userStore = useUserStore();
const charStore = useCharactersStore();

const characterId = Number(route.params.id);
const parentRef = ref<HTMLElement | null>(null);
const messageInput = ref("");

const character = computed(
  () => charStore.currentList.items.find((c) => c.id === characterId) || null,
);

const chatState = computed(() => chatsStore.activeChatState);
const messages = computed(() => chatState.value?.messages || []);

const rowVirtualizer = useVirtualizer(
  computed(() => ({
    count: messages.value.length,
    getScrollElement: () => parentRef.value,
    estimateSize: () => 70,
    overscan: 10,
    getItemKey: (index) => messages.value[index]?.id ?? index,
    initialOffset: 0,
  })),
);

const virtualRows = computed(() => rowVirtualizer.value.getVirtualItems());
const totalSize = computed(() => rowVirtualizer.value.getTotalSize());

const scrollToBottom = (behavior: ScrollBehavior = "auto") => {
  if (!parentRef.value) return;
  parentRef.value.scrollTo({
    top: parentRef.value.scrollHeight,
    behavior,
  });
};

onMounted(() => {
  chatsStore.enterChat(characterId);

  nextTick(() => {
    scrollToBottom("auto");
  });
});

watch(
  () => messages.value.length,
  (newLen, oldLen) => {
    if (newLen === 0) return;

    if (oldLen === 0) {
      nextTick(() => scrollToBottom("auto"));
      return;
    }

    if (!chatsStore.isLoadingHistory) {
      nextTick(() => scrollToBottom("smooth"));
    }
  },
  { flush: "post" },
);

const handleScroll = (e: Event) => {
  const el = e.target as HTMLElement;

  if (
    el.scrollTop < 100 &&
    !chatsStore.isLoadingHistory &&
    chatState.value?.nextCursor
  ) {
    const oldHeight = el.scrollHeight;
    const oldTop = el.scrollTop;

    chatsStore.loadHistory(characterId).then((hasNew) => {
      if (hasNew) {
        nextTick(() => {
          const newHeight = el.scrollHeight;
          el.scrollTop = oldTop + (newHeight - oldHeight);
        });
      }
    });
  }
};

const sendMessage = async () => {
  if (!messageInput.value.trim() || chatsStore.isSending) return;
  const text = messageInput.value;
  messageInput.value = "";

  scrollToBottom("smooth");

  await chatsStore.sendMessage(text);
};

const retry = (msg: Message) => {
  chatsStore.retryMessage(msg);
};

const formatTime = (iso: string) => {
  return new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
};
</script>

<template>
  <div class="chat-layout">
    <ChatHeader
      :character="character"
      :balance="userStore.balance"
      @back="router.back()"
    />

    <main ref="parentRef" class="messages-container" @scroll="handleScroll">
      <div
        class="virtual-sizer"
        :style="{
          height: `${totalSize}px`,
        }"
      >
        <div
          v-for="virtualRow in virtualRows"
          :key="virtualRow.key"
          class="virtual-row-wrapper"
          :style="{
            transform: `translateY(${virtualRow.start}px)`,
          }"
        >
          <div
            v-if="messages[virtualRow.index]"
            class="message-row"
            :class="{
              'row-user': messages[virtualRow.index].role === 'user',
              'row-assistant': messages[virtualRow.index].role === 'assistant',
            }"
          >
            <div class="bubble">
              <div class="bubble-text">
                {{ messages[virtualRow.index].content }}
              </div>
              <div class="bubble-meta">
                {{ formatTime(messages[virtualRow.index].created_at) }}
                <span
                  v-if="messages[virtualRow.index].is_pending"
                  class="status-icon pending"
                  >🕒</span
                >
                <span
                  v-else-if="messages[virtualRow.index].is_error"
                  class="status-icon error"
                  @click="retry(messages[virtualRow.index])"
                  >⚠️</span
                >
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="chatsStore.isLoadingHistory" class="history-loader">
        <div class="spinner-small"></div>
      </div>
    </main>

    <footer class="chat-footer">
      <div class="input-wrapper">
        <textarea
          v-model="messageInput"
          placeholder="Написать..."
          class="message-input"
          rows="1"
          @keydown.enter.prevent="sendMessage"
        ></textarea>
        <button
          @click="sendMessage"
          class="send-button"
          :disabled="!messageInput.trim() || chatsStore.isSending"
        >
          <i-local-send />
        </button>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.chat-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #0e0e10;
  /* GPU acceleration hack for layout */
  transform: translateZ(0);
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  /* Для iOS инерционный скролл */
  -webkit-overflow-scrolling: touch;
  padding: 0 12px;
  padding-top: calc(60px + env(safe-area-inset-top));
  /* Важно для производительности скролла */
  contain: strict;
  will-change: scroll-position;
}

.virtual-sizer {
  width: 100%;
  position: relative;
}

.virtual-row-wrapper {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  padding: 4px 0;
  box-sizing: border-box;
  will-change: transform;
}

.message-row {
  display: flex;
  width: 100%;
}

.row-user {
  justify-content: flex-end;
}

.row-assistant {
  justify-content: flex-start;
}

.bubble {
  max-width: 85%;
  padding: 10px 14px;
  border-radius: 18px;
  font-size: 15px;
  line-height: 1.4;
  word-wrap: break-word;
  white-space: pre-wrap;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  /* Оптимизация текста */
  text-rendering: optimizeLegibility;
}

.row-user .bubble {
  background: #5844b3;
  color: #fff;
  border-bottom-right-radius: 4px;
}

.row-assistant .bubble {
  background: #262629;
  color: #e3e3e3;
  border-bottom-left-radius: 4px;
}

.bubble-meta {
  font-size: 10px;
  opacity: 0.6;
  text-align: right;
  margin-top: 4px;
  display: flex;
  justify-content: flex-end;
  gap: 4px;
}

.chat-footer {
  padding: 10px;
  background: #18181b;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  padding-bottom: calc(10px + env(safe-area-inset-bottom));
  z-index: 10;
}

.input-wrapper {
  display: flex;
  background: #2c2c2e;
  border-radius: 20px;
  padding: 8px 12px;
  align-items: center;
}

.message-input {
  flex: 1;
  background: transparent;
  border: none;
  color: #fff;
  padding: 0;
  outline: none;
  resize: none;
  height: 24px;
  line-height: 24px;
  font-family: inherit;
  font-size: 16px;
  overflow: hidden;
}

.send-button {
  background: #7b61ff;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 8px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.send-button:disabled {
  opacity: 0.5;
}

.history-loader {
  position: absolute;
  top: 60px; /* Сразу под хедером */
  left: 0;
  width: 100%;
  display: flex;
  justify-content: center;
  padding: 10px;
  z-index: 5;
  pointer-events: none;
}

.spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-top-color: #7b61ff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.status-icon {
  font-size: 10px;
  margin-left: 4px;
}
.pending {
  animation: pulse 1.5s infinite;
  opacity: 0.6;
}
.error {
  color: #ff4d4d;
  cursor: pointer;
  opacity: 1;
}
@keyframes pulse {
  0% {
    opacity: 0.3;
  }
  50% {
    opacity: 0.8;
  }
  100% {
    opacity: 0.3;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
