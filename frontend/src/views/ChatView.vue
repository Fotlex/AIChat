<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import WebApp from "@twa-dev/sdk";
import { useChatsStore } from "@/store/chats";
import { useUserStore } from "@/store/user";
import { useSocketStore } from "@/store/socket";
import ChatHeader from "@/components/ChatHeader.vue";

const route = useRoute();
const router = useRouter();
const chatsStore = useChatsStore();
const userStore = useUserStore();
const socketStore = useSocketStore();

const messageInput = ref("");
const messagesContainer = ref<HTMLElement | null>(null);
const textareaRef = ref<HTMLTextAreaElement | null>(null);
const chatLayout = ref<HTMLElement | null>(null);

const initialInputTop = ref(0);

const characterId = Number(route.params.id);

const handleInputFocus = () => {
  if (textareaRef.value) {
    initialInputTop.value = textareaRef.value.getBoundingClientRect().top;
  }
};

const adjustScrollAfterResize = () => {
  if (chatLayout.value) {
    chatLayout.value.style.setProperty(
      "--app-height",
      `${WebApp.viewportHeight}px`
    );
  }

  if (
    !initialInputTop.value ||
    !textareaRef.value ||
    !messagesContainer.value
  ) {
    return;
  }

  const finalInputTop = textareaRef.value.getBoundingClientRect().top;

  const shift = initialInputTop.value - finalInputTop;

  if (shift > 0) {
    messagesContainer.value.scrollTop += shift;
  }

  initialInputTop.value = 0;
};

const scrollToBottom = async (behavior: "smooth" | "auto" = "auto") => {
  await nextTick();
  if (messagesContainer.value) {
    messagesContainer.value.scrollTo({
      top: messagesContainer.value.scrollHeight,
      behavior: behavior,
    });
  }
};

onMounted(async () => {
  WebApp.expand();

  if (!userStore.currentUser) {
    userStore.fetchUser();
  }

  socketStore.connect();

  await chatsStore.loadChat(characterId);

  if (chatLayout.value) {
    chatLayout.value.style.setProperty(
      "--app-height",
      `${WebApp.viewportHeight}px`
    );
  }
  WebApp.onEvent("viewportChanged", adjustScrollAfterResize);

  scrollToBottom("auto");
});

onUnmounted(() => {
  WebApp.offEvent("viewportChanged", adjustScrollAfterResize);
});

watch(
  () => chatsStore.currentChatMessages.length,
  (newLength, oldLength) => {
    if (newLength > oldLength) {
      scrollToBottom("smooth");
    }
  }
);

const isSendButtonDisabled = computed(() => !messageInput.value.trim());

const adjustTextareaHeight = () => {
  const el = textareaRef.value;
  if (el) {
    el.style.height = "auto";
    el.style.height = `${el.scrollHeight}px`;
  }
};

const sendMessage = async () => {
  if (isSendButtonDisabled.value) return;

  const content = messageInput.value;
  messageInput.value = "";
  await chatsStore.sendUserMessage(content);

  nextTick(() => {
    adjustTextareaHeight();
  });
};

const goBack = () => {
  router.back();
};
</script>

<template>
  <div ref="chatLayout" class="chat-layout">
    <ChatHeader
      :character="chatsStore.currentCharacter"
      :balance="userStore.balance"
      @back="goBack"
    />

    <main ref="messagesContainer" class="messages-container">
      <div v-if="chatsStore.isLoading" class="loader">Загрузка чата...</div>
      <div v-else class="messages-list">
        <div
          v-if="chatsStore.hasMoreMessages && !chatsStore.isLoadingMore"
          class="load-more"
          @click="chatsStore.loadMoreMessages()"
        >
          Загрузить еще
        </div>
        <div v-if="chatsStore.isLoadingMore" class="loader">Загрузка...</div>

        <div
          v-for="msg in chatsStore.currentChatMessages"
          :key="msg.id"
          :class="['message-bubble', `is-${msg.role}`]"
        >
          <div class="message-content">{{ msg.content }}</div>
        </div>
      </div>
    </main>

    <footer class="chat-footer">
      <div class="input-wrapper">
        <textarea
          ref="textareaRef"
          v-model="messageInput"
          @focus="handleInputFocus"
          @input="messageInput = ($event.target as HTMLTextAreaElement).value"
          @keydown.enter.exact.prevent="sendMessage"
          placeholder="Введите сообщение..."
          class="message-input"
          rows="1"
          oninput="this.style.height = 'auto'; this.style.height = (this.scrollHeight) + 'px';"
        ></textarea>
        <button
          @click="sendMessage"
          :disabled="isSendButtonDisabled"
          class="send-button"
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
  height: var(--app-height, 100vh);
  width: 100%;
  background: #000;
  /* transition: height 0.2s ease-out; */
}
.messages-container {
  flex-grow: 1;
  overflow-y: auto;
  padding: 16px;
  /* display: flex;
  flex-direction: column; */
  padding-top: calc(66px + env(safe-area-inset-top));
  /* padding-bottom: calc(66px + env(safe-area-inset-bottom)); */
}
.messages-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  /* margin-top: auto; */
  /* padding-bottom: 8px; */
}
.loader,
.load-more {
  text-align: center;
  color: #8e8e93;
  padding: 10px;
}
.load-more {
  cursor: pointer;
  text-decoration: underline;
}
.message-bubble {
  max-width: 80%;
  padding: 10px 15px;
  word-wrap: break-word;
  line-height: 1.4;
  font-size: 15px;
}
.message-bubble.is-assistant {
  align-self: flex-start;
  background-color: #262629;
  color: #e3e3e3;
  border-radius: 20px 20px 20px 4px;
}
.message-bubble.is-user {
  align-self: flex-end;
  background-color: #5844b3;
  color: #fff;
  border-radius: 20px 20px 5px 20px;
}
.chat-footer {
  padding: 8px 16px;
  background-color: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  padding-bottom: calc(8px + env(safe-area-inset-bottom));
  border-top: 1px solid rgba(80, 80, 80, 0.5);
  flex-shrink: 0;
  /* position: fixed; */
  /* bottom: 0; */
  /* width: 100%; */
}
.input-wrapper {
  display: flex;
  align-items: center;
  background-color: #2c2c2e;
  border-radius: 22px;
  padding: 5px;
}
.message-input {
  flex-grow: 1;
  border: none;
  background: none;
  padding: 10px 15px;
  color: white;
  font-size: 16px;
  outline: none;
  resize: none;
  max-height: 100px;
  overflow-y: auto;
  line-height: 1.4;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica,
    Arial, sans-serif;
  letter-spacing: normal;
  word-spacing: normal;
}
.send-button {
  background: #7b61ff;
  border: none;
  border-radius: 50%;
  width: 38px;
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
  transition: background-color 0.2s ease;
  flex-shrink: 0;
}
.send-button:disabled {
  background-color: #555;
  cursor: not-allowed;
}
.send-button > :deep(svg) {
  width: 24px;
  height: 24px;
}
</style>
