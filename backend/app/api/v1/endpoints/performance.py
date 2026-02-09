from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, Request
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.api.v1.deps import get_current_user_full, require_role
from app.services.audit import AuditService
from app.models.db_meta import User
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
async def dry_run(
    config: GuardrailConfig,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_full)
):
    """
    执行连通性测试（单次请求）
    权限：SYSTEM_ADMIN 或有 performance_test 权限的 SCENARIO_ADMIN
    """
    # 权限检查
    if current_user.role == "SYSTEM_ADMIN":
        pass
    elif current_user.role == "SCENARIO_ADMIN":
        # 检查是否有 performance_test 权限
        from app.api.v1.permission_helpers import check_scenario_access_or_403
        await check_scenario_access_or_403(current_user, config.app_id, db, permission="performance_test")
    else:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    if runner_instance.running:
         raise HTTPException(status_code=400, detail="A performance test is currently running.")

    result = await runner_instance.dry_run(config)

    # 记录审计日志
    audit_service = AuditService(db)
    await audit_service.log_create(
        user_id=current_user.id,
        username=current_user.username,
        resource_type="PERFORMANCE_DRY_RUN",
        scenario_id=config.app_id,
        details={"app_id": config.app_id},
        request=request
    )

    return result

@router.post("/start")
async def start_performance_test(
    test_request: PerformanceTestStartRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_full)
):
    """
    启动性能测试（后台运行）
    权限：SYSTEM_ADMIN 或有 performance_test 权限的 SCENARIO_ADMIN
    """
    # 权限检查
    if current_user.role == "SYSTEM_ADMIN":
        pass
    elif current_user.role == "SCENARIO_ADMIN":
        # 检查是否有 performance_test 权限
        from app.api.v1.permission_helpers import check_scenario_access_or_403
        await check_scenario_access_or_403(current_user, test_request.config.app_id, db, permission="performance_test")
    else:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    if runner_instance.running:
        raise HTTPException(status_code=400, detail="Test already running")

    background_tasks.add_task(runner_instance.start_test, test_request)

    # 记录审计日志
    audit_service = AuditService(db)
    await audit_service.log_create(
        user_id=current_user.id,
        username=current_user.username,
        resource_type="PERFORMANCE_TEST_START",
        scenario_id=test_request.config.app_id,
        details={"test_type": test_request.test_type, "app_id": test_request.config.app_id},
        request=request
    )

    return {"message": "Performance test started", "test_type": test_request.test_type}

@router.post("/stop")
async def stop_performance_test(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["SYSTEM_ADMIN", "SCENARIO_ADMIN"]))
):
    """
    停止当前性能测试
    权限：SYSTEM_ADMIN 或 SCENARIO_ADMIN
    """
    await runner_instance.stop()

    # 记录审计日志
    audit_service = AuditService(db)
    await audit_service.log_create(
        user_id=current_user.id,
        username=current_user.username,
        resource_type="PERFORMANCE_TEST_STOP",
        details={},
        request=request
    )

    return {"message": "Stop signal sent"}

@router.get("/status", response_model=PerformanceStatusResponse)
async def get_performance_status(
    current_user: User = Depends(get_current_user_full)
):
    """
    获取运行中测试的实时统计
    权限：SYSTEM_ADMIN 或 SCENARIO_ADMIN
    """
    if current_user.role not in ["SYSTEM_ADMIN", "SCENARIO_ADMIN"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    return runner_instance.get_status()

@router.get("/history", response_model=List[PerformanceHistoryMeta])
async def get_performance_history(
    current_user: User = Depends(get_current_user_full)
):
    """
    获取历史性能测试列表
    权限：SYSTEM_ADMIN 或 SCENARIO_ADMIN
    """
    if current_user.role not in ["SYSTEM_ADMIN", "SCENARIO_ADMIN"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    return runner_instance.get_history_list()

@router.get("/history/{test_id}", response_model=PerformanceHistoryDetail)
async def get_performance_history_detail(
    test_id: str,
    current_user: User = Depends(get_current_user_full)
):
    """
    获取历史性能测试详情
    权限：SYSTEM_ADMIN 或 SCENARIO_ADMIN
    """
    if current_user.role not in ["SYSTEM_ADMIN", "SCENARIO_ADMIN"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    detail = runner_instance.get_history_detail(test_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Test history not found")
    return detail

@router.delete("/history/{test_id}")
async def delete_performance_history(
    test_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["SYSTEM_ADMIN"]))
):
    """
    删除性能测试历史记录
    权限：仅 SYSTEM_ADMIN
    """
    runner_instance.delete_history(test_id)

    # 记录审计日志
    audit_service = AuditService(db)
    await audit_service.log_delete(
        user_id=current_user.id,
        username=current_user.username,
        resource_type="PERFORMANCE_TEST_HISTORY",
        resource_id=test_id,
        request=request
    )

    return {"message": "History deleted"}
