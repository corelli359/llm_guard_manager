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
    tag_code: Mapped[str] = mapped_column(String(64))
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