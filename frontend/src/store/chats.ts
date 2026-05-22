import { defineStore } from "pinia";
import { shallowRef, triggerRef, computed, ref } from "vue";
import apiClient from "@/api/apiClient";
import type { Message, ChatState, Chat } from "@/types";
import { useCharactersStore } from "./characters";
import { getChats } from "@/api/chatsApi";

const MAX_CACHE_SIZE = 5;

export const useChatsStore = defineStore("chats", () => {
  const chatsList = ref<Chat[]>([]);
  const chatsNextCursor = ref<string | null>(null);
  const isChatsLoading = ref(false);
  const isChatsLoaded = ref(false);

  const chatCache = shallowRef(new Map<number, ChatState>());
  const lruOrder: number[] = [];

  const activeCharacterId = shallowRef<number | null>(null);
  const isSending = shallowRef(false);
  const isLoadingHistory = shallowRef(false);

  const activeChatState = computed(() => {
    if (activeCharacterId.value === null) return null;
    return chatCache.value.get(activeCharacterId.value) || null;
  });

  async function fetchChatsList(loadMore = false) {
    if (isChatsLoading.value) return;
    if (loadMore && !chatsNextCursor.value) return;

    isChatsLoading.value = true;
    try {
      const data = await getChats(loadMore ? chatsNextCursor.value : null);
      if (loadMore) {
        chatsList.value.push(...data.items);
      } else {
        chatsList.value = data.items;
      }
      chatsNextCursor.value = data.next_cursor;
      isChatsLoaded.value = true;
    } finally {
      isChatsLoading.value = false;
    }
  }

  function touchCache(charId: number) {
    const idx = lruOrder.indexOf(charId);
    if (idx !== -1) lruOrder.splice(idx, 1);
    lruOrder.push(charId);
    if (lruOrder.length > MAX_CACHE_SIZE) {
      const toRemove = lruOrder.shift();
      if (toRemove !== undefined) {
        chatCache.value.delete(toRemove);
        triggerRef(chatCache);
      }
    }
  }

  async function enterChat(characterId: number) {
    activeCharacterId.value = characterId;

    if (chatCache.value.has(characterId)) {
      touchCache(characterId);
      return;
    }

    if (chatsList.value.length === 0 && !isChatsLoaded.value) {
      await fetchChatsList();
    }

    const charStore = useCharactersStore();
    if (charStore.currentList.items.length === 0) {
      await charStore.fetchCharacters();
    }

    let character = charStore.currentList.items.find(
      (c) => c.id === characterId,
    );
    let chatId = character?.chat_id || null;

    if (!chatId) {
      const existingChat = chatsList.value.find(
        (c) => c.character.id === characterId,
      );
      if (existingChat) {
        chatId = existingChat.id;
        if (!character) character = existingChat.character;
      }
    }

    const initialState: ChatState = {
      characterId,
      chatId,
      messages: [],
      nextCursor: null,
      isFullyLoaded: false,
    };

    if (!initialState.chatId && character?.greeting_message) {
      initialState.messages = [
        {
          id: `welcome_${characterId}`,
          role: "assistant",
          content: character.greeting_message,
          created_at: new Date().toISOString(),
        },
      ];
      initialState.isFullyLoaded = true;
    }

    chatCache.value.set(characterId, initialState);
    touchCache(characterId);
    triggerRef(chatCache);

    if (initialState.chatId) {
      await loadHistory(characterId);
    }
  }

  async function loadHistory(charId: number): Promise<boolean> {
    const state = chatCache.value.get(charId);
    if (
      !state ||
      !state.chatId ||
      state.isFullyLoaded ||
      isLoadingHistory.value
    )
      return false;

    isLoadingHistory.value = true;
    try {
      const { data } = await apiClient.get(`/chats/${state.chatId}/messages/`, {
        params: state.nextCursor ? { cursor: state.nextCursor } : {},
      });

      if (!data.items.length) {
        state.isFullyLoaded = true;
        return false;
      }

      const reversedItems = data.items.reverse();
      state.messages = reversedItems.concat(state.messages);
      state.nextCursor = data.next_cursor;
      if (!data.next_cursor) state.isFullyLoaded = true;

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
    isSending.value = true;
    triggerRef(chatCache);

    try {
      const { data } = await apiClient.post<{
        id: number;
        chat_id: number;
        ai_message: Message;
      }>(`/chats/character/${state.characterId}/send/`, {
        content: msg.content,
      });

      msg.id = data.id;
      msg.is_pending = false;

      let updatedMessages = [...state.messages];

      if (data.ai_message) {
        updatedMessages.push(data.ai_message);
      }

      state.messages = updatedMessages;

      if (!state.chatId) {
        state.chatId = data.chat_id;
        const charStore = useCharactersStore();
        const char = charStore.currentList.items.find(
          (c) => c.id === state.characterId,
        );
        if (char) char.chat_id = data.chat_id;
      }

      updateChatListLocally(
        state.characterId,
        data.chat_id,
        data.ai_message?.content || msg.content,
      );
    } catch {
      msg.is_error = true;
    } finally {
      msg.is_pending = false;
      isSending.value = false;
      triggerRef(chatCache);
    }
  }

  async function sendMessage(content: string) {
    const state = activeChatState.value;
    if (!state || !content.trim() || isSending.value) return;

    const userMsg: Message = {
      id: `temp_${Date.now()}`,
      role: "user",
      content,
      created_at: new Date().toISOString(),
      is_pending: true,
      is_error: false,
    };

    state.messages = [...state.messages, userMsg];
    await performSend(userMsg, state);
  }

  async function retryMessage(msg: Message) {
    const state = activeChatState.value;
    if (!state || isSending.value) return;
    await performSend(msg, state);
  }

  function updateChatListLocally(
    characterId: number,
    chatId: number,
    lastMessageContent: string,
  ) {
    const existingIdx = chatsList.value.findIndex(
      (c) => c.character.id === characterId,
    );

    if (existingIdx !== -1) {
      const chat = chatsList.value.splice(existingIdx, 1)[0]!;
      if (!chat.last_message) chat.last_message = { content: "" } as Message;
      chat.last_message.content = lastMessageContent;
      chat.created_at = new Date().toISOString();
      chatsList.value.unshift(chat);
    } else {
      const charStore = useCharactersStore();
      const character = charStore.currentList.items.find(
        (c) => c.id === characterId,
      );
      if (character) {
        character.chat_id = chatId;
        chatsList.value.unshift({
          id: chatId,
          character: character,
          last_message: { content: lastMessageContent } as Message,
          created_at: new Date().toISOString(),
        });
      }
    }
  }

  return {
    chatsList,
    chatsNextCursor,
    isChatsLoading,
    isChatsLoaded,
    fetchChatsList,

    chatCache,
    activeCharacterId,
    activeChatState,
    isLoadingHistory,
    isSending,
    enterChat,
    sendMessage,
    loadHistory,
    retryMessage,
  };
});
