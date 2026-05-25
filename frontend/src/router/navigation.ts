import type { FunctionalComponent, SVGAttributes } from "vue";

import ILocalHome from "virtual:icons/local/home";
import ILocalChat from "virtual:icons/local/chat";
import ILocalStore from "virtual:icons/local/store";
import ILocalSettings from "virtual:icons/local/settings";
import ILocalGenerate from "virtual:icons/local/generate";

interface NavLink {
  to: string;
  name: string;
  icon: FunctionalComponent<SVGAttributes>;
}

export const navLinks: NavLink[] = [
  {
    to: "/",
    name: "Персонажи",
    icon: ILocalHome,
  },
  {
    to: "/chats",
    name: "Чаты",
    icon: ILocalChat,
  },
  {
    to: "/create",
    name: "Создать",
    icon: ILocalGenerate,
  },
  {
    to: "/store",
    name: "Магазин",
    icon: ILocalStore,
  },
  {
    to: "/settings",
    name: "Настройки",
    icon: ILocalSettings,
  },
];
