import pytest
from django.test import AsyncClient
from apps.core.models import User, LLMConfiguration
from apps.core.services.auth import hash_password_async

@pytest.fixture
async def api_client():
    return AsyncClient()

@pytest.fixture
async def test_user(db):
    hashed_pw = await hash_password_async("password123")
    user, created = await User.objects.aget_or_create(
        username="test_dev",
        defaults={"password_hash": hashed_pw, "balance": 1000}
    )
    return user

@pytest.fixture
async def auth_headers(test_user):
    from apps.core.services.auth import generate_tokens
    tokens = generate_tokens(test_user.id)
    return {"HTTP_AUTHORIZATION": f"Bearer {tokens['access']}"}