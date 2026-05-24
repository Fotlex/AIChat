import { createRouter, createWebHistory } from "vue-router";
import LoginView from "@/views/LoginView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/login",
      name: "login",
      component: LoginView,
      meta: { layout: "BlankLayout" },
    },
    {
      path: "/",
      name: "characters",
      component: () => import("@/views/CharactersView.vue"),
      meta: { layout: "DefaultLayout", title: "Персонажи" },
    },
    {
      path: "/character/:id",
      name: "character-detail",
      component: () => import("@/views/CharacterDetailView.vue"),
      meta: { layout: "BlankLayout" },
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
      path: "/profile/:id",
      name: "profile",
      component: () => import("@/views/ProfileView.vue"),
      meta: { layout: "BlankLayout" },
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

router.beforeEach((to) => {
  const isAuthenticated = !!localStorage.getItem("access_token");

  if (to.name !== "login" && !isAuthenticated) {
    return { name: "login" };
  }
  if (to.name === "login" && isAuthenticated) {
    return { name: "characters" };
  }
});

export default router;
