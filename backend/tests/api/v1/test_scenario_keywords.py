import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_scenario_keywords_lifecycle(authenticated_client: AsyncClient):
    scenario_id = "TEST_SCENARIO_001"
    
    # Create
    kw_data = {
        "scenario_id": scenario_id,
        "keyword": "test_scenario_word",
        "category": 1, # Blacklist
        "tag_code": "POLITICAL" # Required
    }
    response = await authenticated_client.post("/api/v1/keywords/scenario/", json=kw_data)
    assert response.status_code == 200
    data = response.json()
    assert data["scenario_id"] == scenario_id
    kw_id = data["id"]

    # Read by Scenario
    get_res = await authenticated_client.get(f"/api/v1/keywords/scenario/{scenario_id}")
    assert get_res.status_code == 200
    assert len(get_res.json()) >= 1

    # Delete
    del_res = await authenticated_client.delete(f"/api/v1/keywords/scenario/{kw_id}")
    assert del_res.status_code == 200

@pytest.mark.asyncio
async def test_scenario_keyword_duplicate(authenticated_client: AsyncClient):
    scenario_id = "TEST_DUP_001"
    kw_data = {
        "scenario_id": scenario_id,
        "keyword": "unique_word",
        "category": 1,
        "tag_code": "POLITICAL"
    }
    
    # First creation - Success
    res1 = await authenticated_client.post("/api/v1/keywords/scenario/", json=kw_data)
    assert res1.status_code == 200
    
    # Second creation - Duplicate Error (400)
    res2 = await authenticated_client.post("/api/v1/keywords/scenario/", json=kw_data)
    assert res2.status_code == 400
    assert "already exists in scenario" in res2.json()["detail"]

@pytest.mark.asyncio
async def test_scenario_keyword_requires_tag(authenticated_client: AsyncClient):
    scenario_id = "TEST_TAG_REQ_001"
    
    # Test Blacklist - Should fail without tag
    kw_data_black = {
        "scenario_id": scenario_id,
        "keyword": "no_tag_black",
        "category": 1, # Blacklist
        "tag_code": None
    }
    res_black = await authenticated_client.post("/api/v1/keywords/scenario/", json=kw_data_black)
    assert res_black.status_code == 400
    assert "Tag Code is required" in res_black.json()["detail"]

    # Test Whitelist - Should also fail without tag
    kw_data_white = {
        "scenario_id": scenario_id,
        "keyword": "no_tag_white",
        "category": 0, # Whitelist
        "tag_code": None
    }
    res_white = await authenticated_client.post("/api/v1/keywords/scenario/", json=kw_data_white)
    assert res_white.status_code == 400
    assert "Tag Code is required" in res_white.json()["detail"]

