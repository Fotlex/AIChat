import orjson
from config.utils import R400, fast_json
from django.db.models import F
from django.views.decorators.csrf import csrf_exempt

from apps.core.decorators import jwt_auth
from apps.core.models import Tariff, Transaction, User
from apps.core.services.payment import create_yookassa_payment, get_yookassa_payment


@jwt_auth(methods=["GET"])
async def tariff_list_view(request):
    tariffs = [
        {
            "id": t["id"],
            "name": t["name"],
            "cost": float(t["cost"]),
            "reward": t["reward"],
            "photo": f"/media/{t['photo']}" if t["photo"] else None,
        }
        async for t in Tariff.objects.filter(is_active=True)
        .order_by("sort_order", "cost")
        .values()
    ]
    return fast_json(tariffs)


@jwt_auth(methods=["POST"])
async def create_payment_view(request):
    try:
        data = orjson.loads(request.body)
        tariff_id = data.get("tariff_id")
    except orjson.JSONDecodeError:
        return R400

    tariff = await Tariff.objects.filter(id=tariff_id, is_active=True).afirst()
    if not tariff:
        return fast_json({"error": "Tariff not found"}, status=404)

    transaction = await Transaction.objects.acreate(
        user_id=request.user_id,
        tariff_id=tariff.id,
        amount=tariff.cost,
        reward=tariff.reward,
        status=Transaction.StatusChoices.PENDING,
    )

    description = f"Оплата тарифа «{tariff.name}» (ID: {request.user_id})"
    yk_payment = await create_yookassa_payment(
        float(tariff.cost), transaction.id, description
    )

    await Transaction.objects.filter(id=transaction.id).aupdate(
        provider_payment_id=yk_payment.id
    )

    return fast_json(
        {
            "transaction_id": str(transaction.id),
            "payment_url": yk_payment.confirmation.confirmation_url,
        }
    )


@csrf_exempt
async def yookassa_webhook_view(request):
    if request.method != "POST":
        return R400

    try:
        event_json = orjson.loads(request.body)

        yk_payment_id = event_json.get("object", {}).get("id")
        event_type = event_json.get("event")

        if not yk_payment_id:
            return R400

        actual_payment = await get_yookassa_payment(yk_payment_id)

        transaction = await Transaction.objects.filter(
            provider_payment_id=yk_payment_id
        ).afirst()

        if not transaction:
            return fast_json({"status": "not found"}, status=200)

        if transaction.status != Transaction.StatusChoices.PENDING:
            return fast_json({"status": "already processed"}, status=200)

        if actual_payment.status == "succeeded" and event_type == "payment.succeeded":
            await User.objects.filter(id=transaction.user_id).aupdate(
                balance=F("balance") + transaction.reward
            )
            await Transaction.objects.filter(id=transaction.id).aupdate(
                status=Transaction.StatusChoices.SUCCESS
            )

        elif actual_payment.status == "canceled" and event_type == "payment.canceled":
            await Transaction.objects.filter(id=transaction.id).aupdate(
                status=Transaction.StatusChoices.FAILED
            )

        return fast_json({"status": "ok"}, status=200)

    except Exception:
        return fast_json({"error": "bad request"}, status=400)
