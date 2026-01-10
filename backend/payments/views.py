import uuid, json

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from yookassa import Payment as YookassaPayment, Configuration
from yookassa.domain.notification import WebhookNotificationFactory

from .models import Tariff, Payment
from .serializers import TariffListSerializer
from backend.core.config import config
from backend.users.models import User

Configuration.account_id = config.YOOKASSA_SHOP_ID
Configuration.secret_key = config.YOOKASSA_SECRET_KEY


class TariffViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TariffListSerializer

    def get_queryset(self):
        return Tariff.objects.all()
    
    
class PaymentViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'])
    def yookassa_create_payment(self, request):
        email = 'example@mail.ru'
        tariff_id = request.data.get('tariff_id')
        
        if not tariff_id or not email:
            return Response({"error": "tariff_id and email is required"}, status=status.HTTP_400_BAD_REQUEST)

        tariff = Tariff.objects.get(id=tariff_id)
        if not tariff:
            return Response({"error": "Tariff not found"}, status=status.HTTP_404_NOT_FOUND)
        
        user_id = request.user.telegram_id
        customer_name = f'{request.user.first_name}'
        return_url = config.APP_URL
        print("Find email in create payment:", email)

        try:
            yookassa_payment = YookassaPayment.create({
                "amount": {
                    "value": str(tariff.cost),
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect", 
                    "return_url": return_url
                },
                "capture": True,
                "description": f"Покупка валюты в количестве: {tariff.reward} шт.",
                "metadata": {
                    "user_id": user_id,
                    "tariff_id": tariff_id
                },
                "receipt": {
                    "customer": {
                        "full_name": customer_name,
                        "email": email,
                        "phone": "+79000000000"
                    },
                    "tax_system_code": 1,
                    "items": [
                        {
                            "description": "Пополнение баланса",
                            "quantity": "1.00",
                            "amount": {"value": str(tariff.cost), "currency": "RUB"},
                            "vat_code": 6,
                            "payment_subject": "service",
                            "payment_mode": "full_prepayment"
                        }
                    ],
                },
            }, idempotency_key=str(uuid.uuid4()))

            Payment.objects.create(
                payment_id = yookassa_payment.id,
                user=User.objects.get(telegram_id=user_id),
                tariff=Tariff.objects.get(id=tariff_id),
                create_at=timezone.now(),
            )
            
            return Response(
                {'payment_url': yookassa_payment.confirmation.confirmation_url},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            print(e)
            return Response({"error": "error creating payment"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class YooKassaWebhookView(viewsets.ViewSet):
    @action(detail=False, methods=['post'])
    def webhook(self, request):
        try:
            event_json = request.body.decode('utf-8')
            event_dict = json.loads(event_json)

            notification = WebhookNotificationFactory().create(event_dict)
            payment_id = notification.object.id
            
            if notification.object.status == "succeeded":
                payment = Payment.objects.select_related('user', 'tariff').filter(payment_id=payment_id).first()
                payment.status = "succeeded"
                user = payment.user
                user.balance += tariff.reward
                tariff = payment.tariff
                
                user.total_paid += tariff.cost
                
                referred_by = user.referrer
                if referred_by:
                    referred_by.refferal_balance += int(float(tariff.cost) * 0.1)
                    referred_by.save()
                
                user.save()
                
                
                payment.save()
                
            if notification.object.status == "canceled":
                payment.status = "canceled"
                payment.save()

            return Response({"status": "ok"}, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)