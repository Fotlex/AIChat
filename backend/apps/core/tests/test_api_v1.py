import pytest
import orjson
from apps.core.models import Character

pytestmark = pytest.mark.django_db(transaction=True)

class TestUserAPI:
    
    async def test_current_user_me(self, api_client, test_user, auth_headers):
        response = await api_client.get("/api/v1/users/me/", headers=auth_headers)
        
        assert response.status_code == 200
        data = orjson.loads(response.content)
        assert data["username"] == "test_dev"

    async def test_unauthorized_access(self, api_client):
        response = await api_client.get("/api/v1/users/me/")
        assert response.status_code == 401

class TestCharacterAPI:

    async def test_get_characters_list(self, api_client, test_user, auth_headers):
        await Character.objects.acreate(
            name="Тестовая Девушка",
            gender="F",
            is_public=True,
            system_prompt="Ты тест"
        )
        
        response = await api_client.get("/api/v1/characters/", headers=auth_headers)
        assert response.status_code == 200
        data = orjson.loads(response.content)
        assert len(data["items"]) >= 1