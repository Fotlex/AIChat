export interface TelegramWebApp {
  openTelegramLink(url: string): void;
}

declare global {
  interface Window {
    Telegram?: {
      WebApp: TelegramWebApp;
    };
  }
}

export function useTelegram() {
  const tg =
    typeof window !== "undefined" ? window.Telegram?.WebApp : undefined;

  const openLink = (url: string) => {
    tg?.openTelegramLink(url);
  };

  return {
    openLink,
    isAvailable: !!tg,
  };
}
