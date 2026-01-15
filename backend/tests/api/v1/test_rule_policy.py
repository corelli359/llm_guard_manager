import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_scenario_policies_lifecycle(authenticated_client: AsyncClient):
    scenario_id = "TEST_SCENARIO_POLICY_001"
    
    # Create
    policy_data = {
        "scenario_id": scenario_id,
        "match_type": "KEYWORD",
        "match_value": "test_policy_keyword",
        "rule_mode": 1,
        "strategy": "BLOCK",
        "is_active": True,
    }
    response = await authenticated_client.post("/api/v1/policies/scenario/", json=policy_data)
    assert response.status_code == 200
    data = response.json()
    assert data["scenario_id"] == scenario_id
    policy_id = data["id"]

    # Read by Scenario
    get_res = await authenticated_client.get(f"/api/v1/policies/scenario/{scenario_id}")
    assert get_res.status_code == 200
    assert len(get_res.json()) >= 1

    # Delete
    del_res = await authenticated_client.delete(f"/api/v1/policies/scenario/{policy_id}")
    assert del_res.status_code == 200

@pytest.mark.asyncio
async def test_scenario_policy_duplicate(authenticated_client: AsyncClient):
    scenario_id = "TEST_DUP_POLICY_001"
    policy_data = {
        "scenario_id": scenario_id,
        "match_type": "KEYWORD",
        "match_value": "dup_policy_val",
        "rule_mode": 1,
        "strategy": "BLOCK",
        "is_active": True,
    }

    # First creation - Success
    res1 = await authenticated_client.post("/api/v1/policies/scenario/", json=policy_data)
    assert res1.status_code == 200

    # Second creation - Duplicate Error
    res2 = await authenticated_client.post("/api/v1/policies/scenario/", json=policy_data)
    assert res2.status_code == 400
    assert "Duplicate policy" in res2.json()["detail"]

@pytest.mark.asyncio
async def test_global_defaults_lifecycle(authenticated_client: AsyncClient):
    # Create
    default_data = {
        "tag_code": "test_policy_tag",
        "strategy": "PASS",
        "is_active": True,
    }
    response = await authenticated_client.post("/api/v1/policies/defaults/", json=default_data)
    assert response.status_code == 200
    data = response.json()
    assert data["tag_code"] == "test_policy_tag"
    default_id = data["id"]

    # Read
    get_res = await authenticated_client.get("/api/v1/policies/defaults/")
    assert get_res.status_code == 200
    assert len(get_res.json()) >= 1
    
    # Delete
    del_res = await authenticated_client.delete(f"/api/v1/policies/defaults/{default_id}")
    assert del_res.status_code == 200

@pytest.mark.asyncio
async def test_global_default_duplicate(authenticated_client: AsyncClient):
    default_data = {
        "tag_code": "dup_tag_code",
        "strategy": "PASS",
        "is_active": True,
    }
    
    # First creation - Success
    res1 = await authenticated_client.post("/api/v1/policies/defaults/", json=default_data)
    assert res1.status_code == 200
    
    # Second creation - Duplicate Error
    res2 = await authenticated_client.post("/api/v1/policies/defaults/", json=default_data)
    assert res2.status_code == 400
    assert "Duplicate global default" in res2.json()["detail"]
