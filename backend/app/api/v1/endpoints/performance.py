from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import List
from app.schemas.performance import (
    PerformanceTestStartRequest, 
    PerformanceStatusResponse, 
    GuardrailConfig,
    PerformanceHistoryMeta,
    PerformanceHistoryDetail
)
from app.services.performance import runner_instance

router = APIRouter()

@router.post("/dry-run")
async def dry_run(config: GuardrailConfig):
    """
    Perform a connectivity test (single request).
    """
    if runner_instance.running:
         raise HTTPException(status_code=400, detail="A performance test is currently running.")
    return await runner_instance.dry_run(config)

@router.post("/start")
async def start_performance_test(
    request: PerformanceTestStartRequest, 
    background_tasks: BackgroundTasks
):
    """
    Start a performance test in the background.
    """
    if runner_instance.running:
        raise HTTPException(status_code=400, detail="Test already running")
    
    background_tasks.add_task(runner_instance.start_test, request)
    return {"message": "Performance test started", "test_type": request.test_type}

@router.post("/stop")
async def stop_performance_test():
    """
    Stop the current performance test.
    """
    await runner_instance.stop()
    return {"message": "Stop signal sent"}

@router.get("/status", response_model=PerformanceStatusResponse)
async def get_performance_status():
    """
    Get real-time statistics of the running test.
    """
    return runner_instance.get_status()

@router.get("/history", response_model=List[PerformanceHistoryMeta])
async def get_performance_history():
    """
    Get list of past performance tests.
    """
    return runner_instance.get_history_list()

@router.get("/history/{test_id}", response_model=PerformanceHistoryDetail)
async def get_performance_history_detail(test_id: str):
    """
    Get full details of a past performance test.
    """
    detail = runner_instance.get_history_detail(test_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Test history not found")
    return detail

@router.delete("/history/{test_id}")
async def delete_performance_history(test_id: str):
    """
    Delete a performance test history record.
    """
    runner_instance.delete_history(test_id)
    return {"message": "History deleted"}

