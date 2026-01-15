import pytest
from httpx import Response
from unittest.mock import patch
from sqlalchemy import select
from app.models.db_meta import PlaygroundHistory

# Mock response data from the guardrail service
MOCK_GUARDRAIL_RESPONSE = {
    "uuid": "req-123",
    "app_id": "test_app",
    "final_decision": {
        "score": 100,
        "action": "PASS",
        "suggestion": "No sensitive content found."
    },
    "all_decision_dict": {}
}

@pytest.mark.asyncio
async def test_playground_input_success(authenticated_client, db_session):
    payload = {
        "app_id": "test_app_001",
        "input_prompt": "Hello world",
        "use_customize_white": True,
        "use_customize_words": True,
        "use_customize_rule": True,
        "use_vip_black": False,
        "use_vip_white": False
    }

    # Mock httpx.AsyncClient to handle context manager and post method
    with patch("app.services.playground.httpx.AsyncClient") as MockClient:
        mock_instance = MockClient.return_value
        # Async context manager
        mock_instance.__aenter__.return_value = mock_instance
        # Async post method
        from unittest.mock import AsyncMock
        from httpx import Request
        dummy_request = Request("POST", "http://test")
        mock_instance.post = AsyncMock(return_value=Response(200, json=MOCK_GUARDRAIL_RESPONSE, request=dummy_request))
        
        response = await authenticated_client.post("/api/v1/playground/input", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["final_decision"]["score"] == 100
        
        # Verify history saved
        stmt = select(PlaygroundHistory).where(PlaygroundHistory.app_id == "test_app_001")
        result = await db_session.execute(stmt)
        history = result.scalars().first()
        assert history is not None
        assert history.score == 100
        assert history.input_data["input_prompt"] == "Hello world"

@pytest.mark.asyncio
async def test_playground_input_error(authenticated_client, db_session):
    payload = {
        "app_id": "test_app_error",
        "input_prompt": "Error trigger",
        "use_customize_white": True
    }

    # Mock httpx.AsyncClient to raise an exception
    with patch("app.services.playground.httpx.AsyncClient") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.__aenter__.return_value = mock_instance
        
        from unittest.mock import AsyncMock
        mock_instance.post = AsyncMock(side_effect=Exception("Service Down"))
        
        response = await authenticated_client.post("/api/v1/playground/input", json=payload)
        
        # Controller catches generic Exception and returns 500
        assert response.status_code == 500
        assert "Service Down" in response.json()["detail"]

        # Verify history saved even on error (service code attempts to save even if error_occurred is True)
        stmt = select(PlaygroundHistory).where(PlaygroundHistory.app_id == "test_app_error")
        result = await db_session.execute(stmt)
        history = result.scalars().first()
        assert history is not None
        assert history.score == -1 # Logic sets score to -1 on error

@pytest.mark.asyncio
async def test_get_playground_history(authenticated_client, db_session):
    # Insert some dummy history
    history_item = PlaygroundHistory(
        id="hist-001",
        request_id="req-001",
        playground_type="INPUT",
        app_id="history_app",
        input_data={"prompt": "test"},
        config_snapshot={},
        output_data={},
        score=90,
        latency=100
    )
    db_session.add(history_item)
    await db_session.commit()

    response = await authenticated_client.get("/api/v1/playground/history")
    assert response.status_code == 200
    data = response.json()
    
    # Check if the inserted item is in the response
    found = False
    for item in data:
        if item["id"] == "hist-001":
            found = True
            assert item["app_id"] == "history_app"
            break
    assert found