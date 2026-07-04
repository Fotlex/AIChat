import pytest
import uuid
from django.test import AsyncClient
from apps.core.models import User
from apps.core.services.auth import generate_tokens

@pytest.fixture
async def api_client():
    return AsyncClient()

@pytest.fixture
async def test_user(db):
    unique_name = f"user_{uuid.uuid4().hex[:8]}"
    user = await User.objects.acreate(
        id=123456789,
        username=unique_name,
        balance=1000
    )
    return user

@pytest.fixture
async def auth_headers(test_user):
    tokens = generate_tokens(test_user.id)
    return {"Authorization": f"Bearer {tokens['access']}"}