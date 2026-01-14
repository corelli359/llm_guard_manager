import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_scenario_keywords_mode_separation(authenticated_client: AsyncClient):
    scenario_id = "TEST_MODE_SCENARIO"
    
    # 1. Create Keyword in Custom Mode (rule_mode=1) - Default
    kw_custom_data = {
        "scenario_id": scenario_id,
        "keyword": "sensitive_custom",
        "category": 1,
        "rule_mode": 1
    }
    res_custom = await authenticated_client.post("/api/v1/keywords/scenario/", json=kw_custom_data)
    assert res_custom.status_code == 200, res_custom.text
    
    # 2. Create Keyword in Super Mode (rule_mode=0)
    kw_super_data = {
        "scenario_id": scenario_id,
        "keyword": "sensitive_super",
        "category": 1,
        "rule_mode": 0
    }
    res_super = await authenticated_client.post("/api/v1/keywords/scenario/", json=kw_super_data)
    assert res_super.status_code == 200, res_super.text
    
    # 3. Fetch Custom Mode Keywords
    # API: /api/v1/keywords/scenario/{scenario_id}?rule_mode=1
    get_custom = await authenticated_client.get(f"/api/v1/keywords/scenario/{scenario_id}", params={"rule_mode": 1})
    assert get_custom.status_code == 200
    custom_list = get_custom.json()
    assert len(custom_list) == 1
    assert custom_list[0]["keyword"] == "sensitive_custom"
    assert custom_list[0]["rule_mode"] == 1

    # 4. Fetch Super Mode Keywords
    # API: /api/v1/keywords/scenario/{scenario_id}?rule_mode=0
    get_super = await authenticated_client.get(f"/api/v1/keywords/scenario/{scenario_id}", params={"rule_mode": 0})
    assert get_super.status_code == 200
    super_list = get_super.json()
    assert len(super_list) == 1
    assert super_list[0]["keyword"] == "sensitive_super"
    assert super_list[0]["rule_mode"] == 0

    # 5. Fetch All (if supported, or verify default behavior)
    # If rule_mode is omitted, behavior depends on implementation. 
    # My implementation: `if rule_mode is not None: query = query.where...`
    # So if omitted, it should return ALL.
    get_all = await authenticated_client.get(f"/api/v1/keywords/scenario/{scenario_id}")
    assert get_all.status_code == 200
    all_list = get_all.json()
    assert len(all_list) == 2

    # 6. Test Duplicate Check with Mode
    # Trying to add 'sensitive_custom' to Super Mode should be ALLOWED (different mode)
    kw_duplicate_test = {
        "scenario_id": scenario_id,
        "keyword": "sensitive_custom",
        "category": 1,
        "rule_mode": 0 # Different mode
    }
    res_dup = await authenticated_client.post("/api/v1/keywords/scenario/", json=kw_duplicate_test)
    assert res_dup.status_code == 200
    
    # Trying to add 'sensitive_custom' to Custom Mode again should FAIL
    kw_real_dup = {
        "scenario_id": scenario_id,
        "keyword": "sensitive_custom",
        "category": 1,
        "rule_mode": 1
    }
    res_fail = await authenticated_client.post("/api/v1/keywords/scenario/", json=kw_real_dup)
    assert res_fail.status_code == 400
    assert "already exists" in res_fail.json()["detail"]
