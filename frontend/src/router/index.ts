import { createRouter, createWebHistory } from "vue-router";
import CharactersView from "@/views/CharactersView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "characters",
      component: CharactersView,
      meta: { layout: "DefaultLayout", title: "Персонажи" },
    },
    {
      path: "/chats",
      name: "chats",
      component: () => import("@/views/ChatsView.vue"),
      meta: { layout: "DefaultLayout", title: "Чаты" },
    },
    {
      path: "/generate",
      name: "generate",
      component: () => import("@/views/GenerateView.vue"),
      meta: { layout: "DefaultLayout", title: "Генератор" },
    },
    {
      path: "/store",
      name: "store",
      component: () => import("@/views/StoreView.vue"),
      meta: { layout: "DefaultLayout", title: "Магазин" },
    },
    {
      path: "/settings",
      name: "settings",
      component: () => import("@/views/SettingsView.vue"),
      meta: { layout: "DefaultLayout", title: "Настройки" },
    },
    {
      path: "/chat/:id",
      name: "chat",
      component: () => import("@/views/ChatView.vue"),
      meta: { layout: "BlankLayout" },
    },
  ],
});

export default router;
