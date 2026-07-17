import uuid

from asgiref.sync import sync_to_async
from django.conf import settings
from yookassa import Configuration, Payment

Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


@sync_to_async
def create_yookassa_payment(amount: float, transaction_id: str, description: str):
    payment = Payment.create(
        {
            "amount": {"value": f"{amount:.2f}", "currency": "RUB"},
            "confirmation": {"type": "redirect", "return_url": settings.APP_URL},
            "capture": True,
            "description": description,
            "metadata": {"transaction_id": str(transaction_id)},
        },
        str(uuid.uuid4()),
    )

    return payment


@sync_to_async
def get_yookassa_payment(payment_id: str):
    return Payment.find_one(payment_id)
