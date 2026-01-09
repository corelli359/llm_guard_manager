import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_scenario_keywords_lifecycle(client: AsyncClient):
    scenario_id = "TEST_SCENARIO_001"
    
    # Create
    kw_data = {
        "scenario_id": scenario_id,
        "keyword": "test_scenario_word",
        "category": 1 # Blacklist
    }
    response = await client.post("/api/v1/keywords/scenario/", json=kw_data)
    assert response.status_code == 200
    data = response.json()
    assert data["scenario_id"] == scenario_id
    kw_id = data["id"]

    # Read by Scenario
    get_res = await client.get(f"/api/v1/keywords/scenario/{scenario_id}")
    assert get_res.status_code == 200
    assert len(get_res.json()) >= 1

    # Delete
    del_res = await client.delete(f"/api/v1/keywords/scenario/{kw_id}")
    assert del_res.status_code == 200
