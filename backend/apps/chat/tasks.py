import time

from celery import shared_task

from apps.chat.models import Chat, Message
from apps.chat.services import centrifugo_service


@shared_task(
    bind=True,
    max_retries=3,
    rate_limit="1000/m",
    ignore_result=True,
)
def generate_ai_response_task(self, chat_id, user_telegram_id):
    try:
        time.sleep(1.5)
        chat = Chat.objects.select_related("character").get(id=chat_id)

        ai_content = (
            f"[{chat.character.name}]: Я получил твое сообщение! (Centrifugo Test)"
        )

        ai_message = Message.objects.create(
            chat=chat, role=Message.Role.ASSISTANT, content=ai_content
        )

        message_data = {
            "id": ai_message.id,
            "role": ai_message.role,
            "content": ai_message.content,
            "created_at": ai_message.created_at.isoformat(),
        }

        centrifugo_service.publish_personal_message(
            user_id=user_telegram_id,
            event_type="chat_message",
            payload={"chat_id": chat_id, "message": message_data},
        )

    except Exception as exc:
        raise self.retry(exc=exc, countdown=2**self.request.retries)
