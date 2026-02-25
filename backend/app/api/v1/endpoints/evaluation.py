from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.deps import get_db
from app.services.evaluation import EvaluationService
from app.schemas.evaluation import EvalTestCaseCreate, EvalTestCaseUpdate, EvalTaskCreate

router = APIRouter()


@router.get("/test-cases")
async def list_test_cases(
    skip: int = 0, limit: int = 50, keyword: Optional[str] = None,
    tag_code: Optional[str] = None, expected_result: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    svc = EvaluationService(db)
    items, total = await svc.get_test_cases(skip, limit, keyword, tag_code, expected_result)
    return {"items": items, "total": total}


@router.post("/test-cases")
async def create_test_case(data: EvalTestCaseCreate, db: AsyncSession = Depends(get_db)):
    svc = EvaluationService(db)
    case = await svc.create_test_case(data.model_dump())
    return case


@router.put("/test-cases/{case_id}")
async def update_test_case(case_id: str, data: EvalTestCaseUpdate, db: AsyncSession = Depends(get_db)):
    svc = EvaluationService(db)
    try:
        return await svc.update_test_case(case_id, data.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/test-cases/{case_id}")
async def delete_test_case(case_id: str, db: AsyncSession = Depends(get_db)):
    svc = EvaluationService(db)
    await svc.delete_test_case(case_id)
    return {"ok": True}
# PLACEHOLDER_MORE_ENDPOINTS


@router.post("/test-cases/import")
async def import_test_cases(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    svc = EvaluationService(db)
    content = await file.read()
    try:
        count = await svc.import_test_cases(content, file.filename or "upload.csv")
        return {"imported": count}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/test-cases/count")
async def count_test_cases(
    tag_codes: Optional[str] = None, expected_result: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    svc = EvaluationService(db)
    tags = [t.strip() for t in tag_codes.split(",") if t.strip()] if tag_codes else None
    count = await svc.count_test_cases(tags, expected_result)
    return {"count": count}


@router.post("/tasks")
async def create_task(data: EvalTaskCreate, db: AsyncSession = Depends(get_db)):
    svc = EvaluationService(db)
    try:
        task = await svc.create_task(data.model_dump())
        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tasks")
async def list_tasks(
    skip: int = 0, limit: int = 20, status: Optional[str] = None, app_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    svc = EvaluationService(db)
    items, total = await svc.get_tasks(skip, limit, status, app_id)
    return {"items": items, "total": total}


@router.get("/tasks/{task_id}")
async def get_task(task_id: str, db: AsyncSession = Depends(get_db)):
    svc = EvaluationService(db)
    task = await svc.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@router.get("/tasks/{task_id}/results")
async def get_task_results(
    task_id: str, skip: int = 0, limit: int = 50,
    guardrail_result: Optional[str] = None, is_correct: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
):
    svc = EvaluationService(db)
    items, total = await svc.get_task_results(task_id, skip, limit, guardrail_result, is_correct)
    return {"items": items, "total": total}


@router.get("/tasks/{task_id}/metrics")
async def get_metrics(task_id: str, db: AsyncSession = Depends(get_db)):
    svc = EvaluationService(db)
    try:
        return await svc.get_metrics(task_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str, db: AsyncSession = Depends(get_db)):
    svc = EvaluationService(db)
    try:
        return await svc.cancel_task(task_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str, db: AsyncSession = Depends(get_db)):
    svc = EvaluationService(db)
    try:
        await svc.delete_task(task_id)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
