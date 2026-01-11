import { defineStore } from "pinia";
import { Centrifuge } from "centrifuge";
import apiClient from "@/api/apiClient";
import { useChatsStore } from "./chats";

export const useSocketStore = defineStore("socket", {
  state: () => ({
    client: null as Centrifuge | null,
    isConnected: false,
    isConnecting: false,
  }),

  actions: {
    async connect() {
      if (this.client || this.isConnecting) return;
      this.isConnecting = true;

      try {
        const { data } = await apiClient.get<{ token: string }>(
          "/users/ws-token/"
        );

        const protocol = window.location.protocol === "https:" ? "wss" : "ws";
        const host = window.location.host;
        const endpoint = `${protocol}://${host}/connection/websocket`;

        this.client = new Centrifuge(endpoint, {
          token: data.token,
          debug: import.meta.env.DEV,
        });

        this.client.on("connected", () => {
          this.isConnected = true;
          this.isConnecting = false;
          console.log("Socket connected");
        });

        this.client.on("disconnected", () => {
          this.isConnected = false;
          this.isConnecting = false;
          console.log("Socket disconnected");
        });

        this.client.on("publication", (ctx) => {
          console.log("Socket: received publication", ctx);
          this.handleMessage(ctx.data);
        });

        this.client.connect();
      } catch (error) {
        console.error("Socket connection failed:", error);
        this.isConnecting = false;
      }
    },

    handleMessage(data: any) {
      if (data && data.type === "chat_message") {
        const chatsStore = useChatsStore();
        chatsStore.handleIncomingMessage(data.payload);
      }
    },

    disconnect() {
      if (this.client) {
        this.client.disconnect();
        this.client = null;
        this.isConnected = false;
      }
    },
  },
});
