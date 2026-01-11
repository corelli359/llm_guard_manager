import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_read_global_keywords(authenticated_client: AsyncClient):
    response = await authenticated_client.get("/api/v1/keywords/global/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_create_global_keyword(authenticated_client: AsyncClient):
    # Create
    kw_data = {
        "keyword": "test_sensitive_word",
        "tag_code": "POLITICAL", # Assuming this tag might exist or is just a string
        "risk_level": "High",
        "is_active": True
    }
    response = await authenticated_client.post("/api/v1/keywords/global/", json=kw_data)
    assert response.status_code == 200
    data = response.json()
    assert data["keyword"] == "test_sensitive_word"
    kw_id = data["id"]

    # Delete
    del_res = await authenticated_client.delete(f"/api/v1/keywords/global/{kw_id}")
    assert del_res.status_code == 200
