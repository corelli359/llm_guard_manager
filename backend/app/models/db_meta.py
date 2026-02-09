from typing import Optional, Any
from sqlalchemy import String, Integer, Boolean, CHAR, Text, JSON, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# 1. 定义新的 Base 类 (继承 DeclarativeBase)
class Base(DeclarativeBase):
    pass


# --- 数据库表映射 (SQLAlchemy 2.0 Models) ---

class Scenarios(Base):
    """场景/应用管理表"""
    __tablename__ = "scenarios"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True)
    app_id: Mapped[str] = mapped_column(String(64), unique=True, index=True) # 业务ID
    app_name: Mapped[str] = mapped_column(String(128))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 功能开关
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    enable_whitelist: Mapped[bool] = mapped_column(Boolean, default=True)
    enable_blacklist: Mapped[bool] = mapped_column(Boolean, default=True)
    enable_custom_policy: Mapped[bool] = mapped_column(Boolean, default=True)


class GlobalKeywords(Base):
    __tablename__ = "lib_global_keywords"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True)
    keyword: Mapped[str] = mapped_column(String(255))
    tag_code: Mapped[str] = mapped_column(String(64))
    risk_level: Mapped[str] = mapped_column(String(32))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class MetaTags(Base):
    """元数据标签表"""

    __tablename__ = "meta_tags"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True)
    tag_code: Mapped[str] = mapped_column(String(64), unique=True)
    tag_name: Mapped[str] = mapped_column(String(128))
    parent_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    level: Mapped[int] = mapped_column(Integer, default=2)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class ScenarioKeywords(Base):
    __tablename__ = "lib_scenario_keywords"

    CATEGORY_WHITE = 0
    CATEGORY_BLACK = 1

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True)
    scenario_id: Mapped[str] = mapped_column(String(64), index=True)
    keyword: Mapped[str] = mapped_column(String(255))
    tag_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    rule_mode: Mapped[int] = mapped_column(Integer, default=1, comment="0:Super, 1:Custom")
    risk_level: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    category: Mapped[int] = mapped_column(
        Integer, default=CATEGORY_BLACK, comment="0:白, 1:黑"
    )


class RuleScenarioPolicy(Base):
    __tablename__ = "rule_scenario_policy"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True)
    scenario_id: Mapped[str] = mapped_column(String(64))
    match_type: Mapped[str] = mapped_column(String(16))  # KEYWORD / TAG
    match_value: Mapped[str] = mapped_column(String(255))
    rule_mode: Mapped[int] = mapped_column(Integer, default=2)
    extra_condition: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    strategy: Mapped[str] = mapped_column(String(32))  # BLOCK / PASS / REWRITE
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class RuleGlobalDefaults(Base):
    __tablename__ = "rule_global_defaults"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True)
    tag_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    extra_condition: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    strategy: Mapped[str] = mapped_column(String(32))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class PlaygroundHistory(Base):
    __tablename__ = "playground_history"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True)
    request_id: Mapped[str] = mapped_column(String(64), index=True)
    playground_type: Mapped[str] = mapped_column(String(32), index=True)  # INPUT, OUTPUT, FULL
    app_id: Mapped[str] = mapped_column(String(64), index=True)
    
    # 使用 JSON 类型存储
    input_data: Mapped[Any] = mapped_column(JSON)
    config_snapshot: Mapped[Any] = mapped_column(JSON)
    output_data: Mapped[Any] = mapped_column(JSON)
    
    score: Mapped[int] = mapped_column(Integer, default=0)
    latency: Mapped[int] = mapped_column(Integer, nullable=True, comment="总请求耗时(ms)")
    upstream_latency: Mapped[int] = mapped_column(Integer, nullable=True, comment="上游服务耗时(ms)")
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    """用户表 - 扩展支持 RBAC 和 SSO"""
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(64), unique=True, index=True, nullable=True)  # USAP的UserID
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(128))
    role: Mapped[str] = mapped_column(String(32), default="ANNOTATOR")  # SYSTEM_ADMIN, SCENARIO_ADMIN, ANNOTATOR, AUDITOR
    display_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True
    )
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)


class StagingGlobalKeywords(Base):
    __tablename__ = "staging_global_keywords"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True)
    keyword: Mapped[str] = mapped_column(String(255))
    predicted_tag: Mapped[str] = mapped_column(String(64))
    predicted_risk: Mapped[str] = mapped_column(String(32))
    
    final_tag: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    final_risk: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    
    status: Mapped[str] = mapped_column(String(32), default="PENDING", index=True) # PENDING, CLAIMED, REVIEWED, SYNCED, IGNORED
    is_modified: Mapped[bool] = mapped_column(Boolean, default=False)

    # 认领信息
    claimed_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    claimed_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    batch_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)

    # 标注信息
    annotator: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    annotated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# ============================================
# RBAC 相关模型 (V2 - 标准 RBAC)
# ============================================

class Role(Base):
    """角色表"""
    __tablename__ = "roles"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True)
    role_code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    role_name: Mapped[str] = mapped_column(String(128))
    role_type: Mapped[str] = mapped_column(String(16), default="SCENARIO")  # GLOBAL / SCENARIO
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)  # 系统预置角色不可删除
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True
    )


class Permission(Base):
    """权限表"""
    __tablename__ = "permissions"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True)
    permission_code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    permission_name: Mapped[str] = mapped_column(String(128))
    permission_type: Mapped[str] = mapped_column(String(16), default="MENU")  # MENU / ACTION
    scope: Mapped[str] = mapped_column(String(16), default="GLOBAL")  # GLOBAL / SCENARIO
    parent_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class RolePermission(Base):
    """角色-权限关联表"""
    __tablename__ = "role_permissions"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True)
    role_id: Mapped[str] = mapped_column(CHAR(36), index=True)
    permission_id: Mapped[str] = mapped_column(CHAR(36), index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class UserScenarioRole(Base):
    """用户-场景-角色关联表"""
    __tablename__ = "user_scenario_roles"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(CHAR(36), index=True)
    scenario_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)  # NULL=全局角色
    role_id: Mapped[str] = mapped_column(CHAR(36), index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)


# ============================================
# RBAC 相关模型 (V1 - 旧版，保留兼容)
# ============================================

class UserScenarioAssignment(Base):
    """用户场景关联表"""
    __tablename__ = "user_scenario_assignments"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(CHAR(36), index=True)
    scenario_id: Mapped[str] = mapped_column(String(64), index=True)
    role: Mapped[str] = mapped_column(String(32), index=True)  # SCENARIO_ADMIN, ANNOTATOR
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)


class ScenarioAdminPermission(Base):
    """场景管理员权限配置表"""
    __tablename__ = "scenario_admin_permissions"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(CHAR(36), index=True)
    scenario_id: Mapped[str] = mapped_column(String(64), index=True)

    # 5 种细粒度权限
    scenario_basic_info: Mapped[bool] = mapped_column(Boolean, default=True)
    scenario_keywords: Mapped[bool] = mapped_column(Boolean, default=True)
    scenario_policies: Mapped[bool] = mapped_column(Boolean, default=False)
    playground: Mapped[bool] = mapped_column(Boolean, default=True)
    performance_test: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True
    )
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)


class AuditLog(Base):
    """审计日志表"""
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(CHAR(36), index=True)
    username: Mapped[str] = mapped_column(String(64), index=True)
    action: Mapped[str] = mapped_column(String(64), index=True)  # CREATE, UPDATE, DELETE, VIEW, EXPORT
    resource_type: Mapped[str] = mapped_column(String(64), index=True)  # USER, SCENARIO, KEYWORD, POLICY, etc.
    resource_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    scenario_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    details: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


class StagingGlobalRules(Base):
    __tablename__ = "staging_global_rules"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True)
    tag_code: Mapped[str] = mapped_column(String(64))
    predicted_strategy: Mapped[str] = mapped_column(String(32))
    
    final_strategy: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    extra_condition: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    status: Mapped[str] = mapped_column(String(32), default="PENDING", index=True) # PENDING, CLAIMED, REVIEWED, SYNCED, IGNORED
    is_modified: Mapped[bool] = mapped_column(Boolean, default=False)

    # 认领信息
    claimed_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    claimed_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    batch_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)

    # 标注信息
    annotator: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    annotated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())