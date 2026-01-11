import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_scenarios_lifecycle(authenticated_client: AsyncClient):
    # Create
    scenario_data = {
        "app_id": "test_app_001",
        "app_name": "Test App",
        "description": "A test application scenario",
        "is_active": True,
        "enable_whitelist": True,
        "enable_blacklist": True,
        "enable_custom_policy": True
    }
    response = await authenticated_client.post("/api/v1/apps/", json=scenario_data)
    assert response.status_code == 200
    data = response.json()
    assert data["app_id"] == "test_app_001"
    scenario_id = data["id"]

    # Read by App ID
    get_res = await authenticated_client.get(f"/api/v1/apps/{data['app_id']}")
    assert get_res.status_code == 200
    assert get_res.json()["app_name"] == "Test App"
    
    # Read all
    get_all_res = await authenticated_client.get("/api/v1/apps/")
    assert get_all_res.status_code == 200
    assert len(get_all_res.json()) >= 1

    # Delete
    del_res = await authenticated_client.delete(f"/api/v1/apps/{scenario_id}")
    assert del_res.status_code == 200
