from django.db import transaction

from .models import User


def get_or_create_user_with_referral(user_data, start_param: str):
    with transaction.atomic():
        user, created = User.objects.get_or_create(
            telegram_id=user_data.id,
            defaults={
                "username": user_data.username,
                "first_name": user_data.first_name,
                "last_name": user_data.last_name,
            },
        )

        if created and start_param and start_param.isdigit():
            referrer_id = int(start_param)
            if user.pk != referrer_id:
                if User.objects.filter(pk=referrer_id).exists():
                    User.objects.filter(pk=user.pk).update(referred_by_id=referrer_id)

    return user
