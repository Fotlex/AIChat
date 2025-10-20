import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { getChats, getOrCreateChatWithMessages, getMessagesByUrl } from "@/api";
import type { Chat, Message } from "@/types";
import { useCharactersStore } from "./characters";

export const useChatsStore = defineStore("chats", () => {
  const chatsList = ref<Chat[]>([]);
  const currentChatMessages = ref<Message[]>([]);
  const currentChatDetails = ref<Chat | null>(null);
  const isLoading = ref(false);
  const isLoadingMore = ref(false);
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

  function sendUserMessage(content: string) {
    if (!content.trim()) return;

    const userMessage: Message = {
      id: Date.now(),
      role: "user",
      content: content,
      created_at: new Date().toISOString(),
    };
    currentChatMessages.value.push(userMessage);

    setTimeout(() => {
      const aiMessage: Message = {
        id: Date.now() + 1,
        role: "assistant",
        content:
          "Это автоматический ответ-заглушка. Настоящая логика будет позже.",
        created_at: new Date().toISOString(),
      };
      currentChatMessages.value.push(aiMessage);
    }, 1500);
  }

  return {
    chatsList,
    currentChatMessages,
    currentChatDetails,
    currentCharacter,
    isLoading,
    isLoadingMore,
    error,
    hasMoreMessages,
    fetchChatsList,
    loadChat,
    loadMoreMessages,
    sendUserMessage,
  };
});
