from apps.bot.loader import bot
from asgiref.sync import async_to_sync
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Sets the Telegram Bot Webhook"

    def handle(self, *args, **options):
        webhook_url = f"{settings.WEBAPP_URL}/api/v1/bot/webhook/"
        secret = settings.BOT_WEBHOOK_SECRET

        self.stdout.write("Configuring Webhook...")
        self.stdout.write(f"URL: {webhook_url}")

        async def _setup():
            try:
                current_info = await bot.get_webhook_info()

                if current_info.url == webhook_url:
                    self.stdout.write(self.style.SUCCESS("Webhook is already correct"))
                else:
                    self.stdout.write(f"Updating webhook from '{current_info.url}'...")
                    await bot.set_webhook(
                        url=webhook_url,
                        secret_token=secret,
                        allowed_updates=[
                            "message",
                            "callback_query",
                            "pre_checkout_query",
                        ],
                        drop_pending_updates=False,
                    )
                    self.stdout.write(
                        self.style.SUCCESS("Webhook updated successfully")
                    )

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to set webhook: {e}"))
            finally:
                await bot.session.close()

        async_to_sync(_setup)()
