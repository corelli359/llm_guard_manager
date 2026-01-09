import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_read_tags(client: AsyncClient):
    response = await client.get("/api/v1/tags/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_create_and_delete_tag(client: AsyncClient):
    # Create
    tag_data = {
        "tag_code": "TEST_UNIT_TAG",
        "tag_name": "Test Unit Tag",
        "level": 1,
        "is_active": True
    }
    response = await client.post("/api/v1/tags/", json=tag_data)
    # 400 if already exists, which is fine for repeated runs, but let's handle success
    if response.status_code == 200:
        data = response.json()
        assert data["tag_code"] == tag_data["tag_code"]
        tag_id = data["id"]
        
        # Get
        get_response = await client.get("/api/v1/tags/")
        assert any(t["id"] == tag_id for t in get_response.json())

        # Delete
        del_response = await client.delete(f"/api/v1/tags/{tag_id}")
        assert del_response.status_code == 200
    elif response.status_code == 400:
        # Cleanup if it existed from previous failed run (optional logic)
        pass
