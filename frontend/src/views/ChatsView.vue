<script setup lang="ts">
import { onMounted } from "vue";
import { useChatsStore } from "@/store/chats";
import { useRouter } from "vue-router";

const chatsStore = useChatsStore();
const router = useRouter();

onMounted(() => {
  chatsStore.fetchChatsList();
});

const openChat = (characterId: number) => {
  router.push({ name: "chat", params: { id: characterId } });
};
</script>

<template>
  <div class="chats-view">
    <div v-if="chatsStore.isLoading" class="status-message">Загрузка...</div>
    <div v-else-if="chatsStore.error" class="status-message error">
      {{ chatsStore.error }}
    </div>
    <div
      v-else-if="!chatsStore.chatsList || chatsStore.chatsList.length === 0"
      class="status-message"
    >
      У вас пока нет чатов.
    </div>

    <ul v-else class="chat-list">
      <template v-for="chat in chatsStore.chatsList" :key="chat.id">
        <li
          v-if="chat.character"
          class="chat-item"
          @click="openChat(chat.character.id)"
        >
          <img
            :src="chat.character.photo || '/default-avatar.png'"
            :alt="chat.character.name"
            class="avatar"
          />

          <div class="chat-info">
            <div class="name">{{ chat.character.name }}</div>
            <div class="last-message">
              <span v-if="chat.last_message?.role === 'user'">Вы: </span>
              {{ chat.last_message?.content || "Нет сообщений" }}
            </div>
          </div>
        </li>
      </template>
    </ul>
  </div>
</template>

<style scoped>
.chats-view {
  padding: 16px;
  padding-bottom: 90px;
}
.chat-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.chat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}
.chat-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
}
.avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  object-fit: cover;
}
.chat-info {
  flex-grow: 1;
  overflow: hidden;
}
.name {
  font-weight: 600;
  font-size: 17px;
  color: #fff;
}
.last-message {
  font-size: 15px;
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
.status-message.error {
  color: #ff4d4d;
}
</style>
