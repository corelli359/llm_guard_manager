import pytest
from httpx import AsyncClient, Response, Request
from unittest.mock import patch, AsyncMock
import asyncio

# Mock response data
MOCK_GUARDRAIL_RESPONSE = {
    "uuid": "req-perf",
    "final_decision": {"score": 0}
}

@pytest.mark.asyncio
async def test_performance_dry_run(authenticated_client: AsyncClient):
    payload = {
        "app_id": "test_app",
        "input_prompt": "test",
        "use_customize_white": False
    }
    
    # Mock httpx in LoadRunner
    with patch("app.services.performance.httpx.AsyncClient") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.__aenter__.return_value = mock_instance
        
        dummy_req = Request("POST", "http://test")
        mock_instance.post = AsyncMock(return_value=Response(200, json=MOCK_GUARDRAIL_RESPONSE, request=dummy_req))
        
        response = await authenticated_client.post("/api/v1/performance/dry-run", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "latency" in data

@pytest.mark.asyncio
async def test_performance_start_stop(authenticated_client: AsyncClient):
    # Start Test
    payload = {
        "test_type": "FATIGUE",
        "target_config": {
            "app_id": "test_app",
            "input_prompt": "test"
        },
        "fatigue_config": {
            "concurrency": 2,
            "duration": 10
        }
    }

    # Mock httpx to avoid actual network calls
    with patch("app.services.performance.httpx.AsyncClient") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.__aenter__.return_value = mock_instance
        
        dummy_req = Request("POST", "http://test")
        mock_instance.post = AsyncMock(return_value=Response(200, json=MOCK_GUARDRAIL_RESPONSE, request=dummy_req))
    
        response = await authenticated_client.post("/api/v1/performance/start", json=payload)
        
        if response.status_code != 200:
            print(f"DEBUG Error: {response.json()}")

        assert response.status_code == 200
        assert response.json()["message"] == "Performance test started"

        # Check Status
        status_res = await authenticated_client.get("/api/v1/performance/status")
        assert status_res.status_code == 200
        
        # Stop Test
        stop_res = await authenticated_client.post("/api/v1/performance/stop")
        assert stop_res.status_code == 200

        # Wait a bit
        await asyncio.sleep(0.1)
        
        status_res_after = await authenticated_client.get("/api/v1/performance/status")
        assert status_res_after.json()["is_running"] is False