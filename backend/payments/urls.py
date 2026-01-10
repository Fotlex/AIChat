from rest_framework.routers import DefaultRouter

from .views import TariffViewSet, PaymentViewSet, YooKassaWebhookView

router = DefaultRouter()
router.register(r"tariffs", TariffViewSet, basename="tariffs")
router.register(r'payment', PaymentViewSet, basename='payment')
router.register(r'yookassa', YooKassaWebhookView, basename='yookassa')

urlpatterns = router.urls
