import asyncio

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.bot.engine import bot


class Command(BaseCommand):
    help = "Регистрация или удаление вебхука Telegram"

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Удалить вебхук",
        )

    def handle(self, *args, **options):
        asyncio.run(self.run_command(options["delete"]))

    async def run_command(self, delete: bool):
        try:
            if delete:
                await self.delete_webhook()
            else:
                await self.set_webhook()
        finally:
            await bot.session.close()

    async def set_webhook(self):
        webhook_url = f"{settings.APP_URL}/api/v1/bot/webhook/"
        secret_token = getattr(settings, "TELEGRAM_BOT_WEBHOOK_SECRET", None)

        self.stdout.write(f"Установка вебхука на адрес: {webhook_url}...")

        success = await bot.set_webhook(
            url=webhook_url,
            secret_token=secret_token,
            allowed_updates=["message"],
            drop_pending_updates=False,
        )

        if success:
            self.stdout.write(self.style.SUCCESS("Вебхук успешно установлен!"))
        else:
            self.stdout.write(self.style.ERROR("Ошибка установки вебхука."))

    async def delete_webhook(self):
        self.stdout.write("Удаление вебхука...")
        success = await bot.delete_webhook()
        if success:
            self.stdout.write(self.style.SUCCESS("Вебхук успешно удален!"))
        else:
            self.stdout.write(self.style.ERROR("Ошибка при удалении вебхука."))
