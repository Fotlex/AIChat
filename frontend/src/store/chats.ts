import { defineStore } from "pinia";
import { shallowRef, triggerRef, computed } from "vue";
import apiClient from "@/api/apiClient";
import type { Message, ChatState } from "@/types";
import { useCharactersStore } from "./characters";

const MAX_CACHE_SIZE = 5;

export const useChatsStore = defineStore("chats", () => {
  const chatCache = shallowRef(new Map<number, ChatState>());

  const lruOrder: number[] = [];

  const activeCharacterId = shallowRef<number | null>(null);
  const isSending = shallowRef(false);
  const isLoadingHistory = shallowRef(false);

  const activeChatState = computed(() => {
    if (activeCharacterId.value === null) return null;
    return chatCache.value.get(activeCharacterId.value) || null;
  });

  function touchCache(charId: number) {
    const idx = lruOrder.indexOf(charId);
    if (idx !== -1) {
      lruOrder.splice(idx, 1);
    }
    lruOrder.push(charId);

    if (lruOrder.length > MAX_CACHE_SIZE) {
      const toRemove = lruOrder.shift();
      if (toRemove !== undefined) {
        chatCache.value.delete(toRemove);
        triggerRef(chatCache);
      }
    }
  }

  function enterChat(characterId: number) {
    activeCharacterId.value = characterId;

    if (chatCache.value.has(characterId)) {
      touchCache(characterId);
      return;
    }

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

    chatCache.value.set(characterId, initialState);
    touchCache(characterId);
    triggerRef(chatCache);

    if (initialState.chatId) {
      loadHistory(characterId);
    }
  }

  async function loadHistory(charId: number): Promise<boolean> {
    const state = chatCache.value.get(charId);

    if (
      !state ||
      !state.chatId ||
      state.isFullyLoaded ||
      isLoadingHistory.value
    ) {
      return false;
    }

    isLoadingHistory.value = true;
    try {
      const { data } = await apiClient.get(`/chats/${state.chatId}/messages/`, {
        params: state.nextCursor ? { cursor: state.nextCursor } : {},
      });

      if (!data.items.length) {
        state.isFullyLoaded = true;
        return false;
      }

      state.messages = data.items.concat(state.messages);
      state.nextCursor = data.next_cursor;

      if (!data.next_cursor) {
        state.isFullyLoaded = true;
      }

      triggerRef(chatCache);
      return true;
    } catch (e) {
      return false;
    } finally {
      isLoadingHistory.value = false;
    }
  }

  async function performSend(msg: Message, state: ChatState) {
    msg.is_pending = true;
    msg.is_error = false;
    triggerRef(chatCache);

    try {
      const { data } = await apiClient.post<{ id: number; chat_id: number }>(
        `/chats/character/${state.characterId}/send/`,
        { content: msg.content },
      );

      msg.id = data.id;
      msg.is_pending = false;

      if (!state.chatId) {
        state.chatId = data.chat_id;
        const charStore = useCharactersStore();
        const char = charStore.currentList.items.find(c => c.id === state.characterId);
        if (char) char.chat_id = data.chat_id;
      }
    } catch {
      msg.is_error = true;
      msg.is_pending = false;
    } finally {
      triggerRef(chatCache);
    }
  }

  async function sendMessage(content: string) {
    const state = activeChatState.value;
    if (!state || !content.trim()) return;

    const userMsg: Message = {
      id: `temp_${Date.now()}`,
      role: "user",
      content,
      created_at: new Date().toISOString(),
      is_pending: true,
      is_error: false,
    };

    state.messages.push(userMsg);
    await performSend(userMsg, state);
  }

  async function retryMessage(msg: Message) {
    const state = activeChatState.value;
    if (!state) return;

    await performSend(msg, state);
  }

  function handleIncomingMessage(payload: {
    chat_id: number;
    message: Message;
  }) {
    for (const state of chatCache.value.values()) {
      if (state.chatId === payload.chat_id) {
        const isDuplicate = state.messages
          .slice(-5)
          .some((m) => m.id === payload.message.id);
        if (isDuplicate) return;

        state.messages.push(payload.message);

        touchCache(state.characterId);
        triggerRef(chatCache);
        return;
      }
    }
  }

  return {
    activeChatState,
    isLoadingHistory,
    isSending,
    enterChat,
    sendMessage,
    retryMessage,
    loadHistory,
    handleIncomingMessage,
  };
});
