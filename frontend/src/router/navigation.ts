import type { FunctionalComponent, SVGAttributes } from "vue";

import ILocalHome from "virtual:icons/local/home";
import ILocalChat from "virtual:icons/local/chat";
import ILocalGenerate from "virtual:icons/local/generate";
import ILocalStore from "virtual:icons/local/store";
import ILocalSettings from "virtual:icons/local/settings";

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
    to: "/generate",
    name: "Генератор",
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
