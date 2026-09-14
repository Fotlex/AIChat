from asgiref.sync import sync_to_async
from django.db import IntegrityError, transaction
from django.db.models import F

from apps.core.models import Referral, User


def _process_telegram_referral_sync(
    referred_id: int, referrer_id: int, reward: int = 100
) -> None:
    if referred_id == referrer_id:
        return

    try:
        with transaction.atomic():
            Referral.objects.create(
                referrer_id=referrer_id, referred_id=referred_id, reward_amount=reward
            )
            User.objects.filter(id=referrer_id).update(balance=F("balance") + reward)

    except IntegrityError:
        pass


process_referral_async = sync_to_async(
    _process_telegram_referral_sync, thread_sensitive=False
)
