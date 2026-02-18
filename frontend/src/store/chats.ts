import { defineStore } from "pinia";
import { ref, computed } from "vue";
import apiClient from "@/api/apiClient";
import type { Message, ChatState } from "@/types";
import { useCharactersStore } from "./characters";

export const useChatsStore = defineStore("chats", () => {
  const chatCache = ref<Record<number, ChatState>>({});

  const activeCharacterId = ref<number | null>(null);
  const isSending = ref(false);
  const isLoadingHistory = ref(false);

  const activeChatState = computed(() => {
    if (activeCharacterId.value === null) return null;
    return chatCache.value[activeCharacterId.value] || null;
  });

  async function enterChat(characterId: number) {
    activeCharacterId.value = characterId;

    if (!chatCache.value[characterId]) {
      const charStore = useCharactersStore();
      const character = charStore.currentList.items.find(
        (c) => c.id === characterId,
      );

      const initialState: ChatState = {
        characterId,
        chatId: character?.chat_id || null,
        messages: [],
        nextCursor: null,
        isFullyLoaded: false,
      };

      if (!initialState.chatId && character?.welcome_message) {
        initialState.messages = [
          {
            id: `welcome_${characterId}`,
            role: "assistant",
            content: character.welcome_message,
            created_at: new Date().toISOString(),
          },
        ];
        initialState.isFullyLoaded = true;
      }

      chatCache.value[characterId] = initialState;
    }

    const state = chatCache.value[characterId];
    if (state.chatId && state.messages.length === 0) {
      loadHistory(characterId);
    }
  }

  async function loadHistory(charId: number): Promise<boolean> {
    const state = chatCache.value[charId];
    if (
      !state ||
      !state.chatId ||
      state.isFullyLoaded ||
      isLoadingHistory.value
    )
      return false;

    isLoadingHistory.value = true;
    try {
      const params = state.nextCursor ? { cursor: state.nextCursor } : {};
      const { data } = await apiClient.get(`/chats/${state.chatId}/messages/`, {
        params,
      });

      const historyMessages = data.items;

      state.messages = [...historyMessages, ...state.messages];
      state.nextCursor = data.next_cursor;

      if (!data.next_cursor) {
        state.isFullyLoaded = true;
      }

      return true;
    } catch (e) {
      console.error(e);
      return false;
    } finally {
      isLoadingHistory.value = false;
    }
  }

  async function sendMessage(content: string) {
    const charId = activeCharacterId.value;
    if (!charId || !content.trim()) return;

    const state = chatCache.value[charId];
    if (!state) return;

    isSending.value = true;
    const tempId = `temp_${Date.now()}`;

    const userMsg: Message = {
      id: tempId,
      role: "user",
      content,
      created_at: new Date().toISOString(),
      is_pending: true,
    };

    state.messages = [...state.messages, userMsg];

    try {
      const { data } = await apiClient.post<{ id: number; chat_id: number }>(
        `/chats/character/${charId}/send/`,
        { content },
      );

      const idx = state.messages.findIndex((m) => m.id === tempId);
      if (idx !== -1) {
        const newMsgs = [...state.messages];
        newMsgs[idx] = { ...userMsg, id: data.id, is_pending: false };
        state.messages = newMsgs;
      }

      if (!state.chatId) {
        state.chatId = data.chat_id;
        const charStore = useCharactersStore();
        const char = charStore.currentList.items.find((c) => c.id === charId);
        if (char) char.chat_id = data.chat_id;
      }
    } catch (e) {
      state.messages = state.messages.filter((m) => m.id !== tempId);
      console.error("Send failed", e);
    } finally {
      isSending.value = false;
    }
  }

  function handleIncomingMessage(payload: {
    chat_id: number;
    message: Message;
  }) {
    for (const charId in chatCache.value) {
      const state = chatCache.value[charId];
      if (state && state.chatId === payload.chat_id) {
        if (state.messages.some((m) => m.id === payload.message.id)) return;
        state.messages = [...state.messages, payload.message];
        break;
      }
    }
  }

  return {
    activeChatState,
    isLoadingHistory,
    isSending,
    enterChat,
    sendMessage,
    loadHistory,
    handleIncomingMessage,
  };
});
