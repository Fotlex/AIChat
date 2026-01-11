import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { getChats, getOrCreateChatWithMessages, getMessagesByUrl } from "@/api";
import type { Chat, Message } from "@/types";
import apiClient from "@/api/apiClient";
import { useCharactersStore } from "./characters";

export const useChatsStore = defineStore("chats", () => {
  const chatsList = ref<Chat[]>([]);
  const currentChatMessages = ref<Message[]>([]);
  const currentChatDetails = ref<Chat | null>(null);
  const isLoading = ref(false);
  const isLoadingMore = ref(false);
  const isSending = ref(false);
  const error = ref<string | null>(null);
  const nextMessagesUrl = ref<string | null>(null);

  const currentCharacter = computed(
    () => currentChatDetails.value?.character ?? null
  );
  const hasMoreMessages = computed(() => nextMessagesUrl.value !== null);

  async function fetchChatsList() {
    isLoading.value = true;
    error.value = null;
    try {
      chatsList.value = await getChats();
    } catch (e: any) {
      error.value = "Не удалось загрузить список чатов";
    } finally {
      isLoading.value = false;
    }
  }

  async function loadChat(characterId: number) {
    isLoading.value = true;
    error.value = null;
    currentChatMessages.value = [];
    currentChatDetails.value = null;
    nextMessagesUrl.value = null;

    const charactersStore = useCharactersStore();
    const existingCharacter = charactersStore.getCharacterById(characterId);
    if (existingCharacter) {
      currentChatDetails.value = {
        id: -1,
        character: existingCharacter,
        last_message: null,
        created_at: "",
      };
    }

    try {
      const response = await getOrCreateChatWithMessages(characterId);
      currentChatMessages.value = response.results.reverse();
      currentChatDetails.value = response.chat;
      nextMessagesUrl.value = response.next;
    } catch (e: any) {
      error.value = "Не удалось загрузить чат";
    } finally {
      isLoading.value = false;
    }
  }

  async function loadMoreMessages() {
    if (isLoadingMore.value || !nextMessagesUrl.value) return;

    isLoadingMore.value = true;
    try {
      const response = await getMessagesByUrl(nextMessagesUrl.value);
      currentChatMessages.value.unshift(...response.results.reverse());
      nextMessagesUrl.value = response.next;
    } catch (e: any) {
      console.error("Failed to load more messages", e);
    } finally {
      isLoadingMore.value = false;
    }
  }

  function handleIncomingMessage(payload: {
    chat_id: number;
    message: Message;
  }) {
    console.log("ChatsStore: handling message", payload);
    if (
      currentChatDetails.value &&
      currentChatDetails.value.id === payload.chat_id
    ) {
      currentChatMessages.value.push(payload.message);
    }

    const chatInList = chatsList.value.find((c) => c.id === payload.chat_id);
    if (chatInList) {
      chatInList.last_message = payload.message;
    }
  }

  async function sendUserMessage(content: string) {
    if (!content.trim() || !currentChatDetails.value) return;

    isSending.value = true;

    try {
      const response = await apiClient.post<Message>(
        `/chats/${currentChatDetails.value.id}/send_message/`,
        { content }
      );

      currentChatMessages.value.push(response.data);
    } catch (e) {
      console.error("Send error", e);
    } finally {
      isSending.value = false;
    }
  }

  return {
    chatsList,
    currentChatMessages,
    currentChatDetails,
    currentCharacter,
    isLoading,
    isLoadingMore,
    isSending,
    error,
    hasMoreMessages,
    fetchChatsList,
    loadChat,
    loadMoreMessages,
    handleIncomingMessage,
    sendUserMessage,
  };
});
