from fastapi import APIRouter
from app.api.v1.endpoints import meta_tags, global_keywords, scenario_keywords, rule_policy, scenarios, auth, playground, performance, users, staging

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/login", tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(staging.router, prefix="/staging", tags=["staging"])
api_router.include_router(meta_tags.router, prefix="/tags", tags=["tags"])
api_router.include_router(global_keywords.router, prefix="/keywords/global", tags=["global-keywords"])
api_router.include_router(scenario_keywords.router, prefix="/keywords/scenario", tags=["scenario-keywords"])
api_router.include_router(rule_policy.router, prefix="/policies", tags=["rule-policies"])
api_router.include_router(scenarios.router, prefix="/apps", tags=["apps"])
api_router.include_router(playground.router, prefix="/playground", tags=["playground"])
api_router.include_router(performance.router, prefix="/performance", tags=["performance"])
