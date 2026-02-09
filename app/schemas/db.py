from __future__ import annotations

from datetime import date, datetime
from typing import Generator, Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    create_engine,
    func,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from urllib.parse import quote_plus
from app.config.db_config import get_db_config

db = get_db_config()

DATABASE_URL = (
    f"mysql+pymysql://"
    f"{db['user']}:{quote_plus(db['password'])}"
    f"@{db['host']}:{db['port']}/{db['database']}"
)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def uuid_str() -> str:
    return str(uuid4())


class CompanyMaster(Base):
    __tablename__ = "company_master"

    company_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(255))
    entity_type_id: Mapped[str] = mapped_column(String(36), nullable=False)
    country_id: Mapped[str] = mapped_column(String(36), nullable=False)
    registered_address: Mapped[str] = mapped_column(Text, nullable=False)
    operational_hq_address: Mapped[Optional[str]] = mapped_column(Text)
    is_part_of_group: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    parent_group_id: Mapped[Optional[str]] = mapped_column(String(36))
    status: Mapped[str] = mapped_column(
        Enum("Draft", "Confirmed", "Archived", name="company_status"),
        nullable=False,
        default="Draft",
    )
    created_by: Mapped[str] = mapped_column(String(36), nullable=False)
    updated_by: Mapped[Optional[str]] = mapped_column(String(36))
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        Index("idx_legal_name", "legal_name"),
        Index("idx_country", "country_id"),
        Index("idx_entity_type", "entity_type_id"),
        Index("idx_parent_group", "parent_group_id"),
    )


class RegulatoryMaster(Base):
    __tablename__ = "regulatory_master"

    registration_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    company_id: Mapped[str] = mapped_column(String(36), nullable=False)
    country_id: Mapped[Optional[str]] = mapped_column(String(36))
    cin: Mapped[Optional[str]] = mapped_column(String(25))
    pan: Mapped[str] = mapped_column(String(15), nullable=False)
    lei: Mapped[Optional[str]] = mapped_column(String(30))
    listed_status: Mapped[str] = mapped_column(Enum("Listed", "Unlisted", name="listed_status"), nullable=False)
    exchange_list: Mapped[Optional[list[str]]] = mapped_column(JSON)
    ticker_symbol: Mapped[Optional[str]] = mapped_column(String(30))
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        UniqueConstraint("company_id", name="uniq_company_reg"),
        Index("idx_company", "company_id"),
        Index("idx_country", "country_id"),
    )


class CompanyTaxRegistration(Base):
    __tablename__ = "company_tax_registration"

    tax_reg_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    company_id: Mapped[str] = mapped_column(String(36), nullable=False)
    tax_type: Mapped[str] = mapped_column(String(30), nullable=False)
    tax_id: Mapped[str] = mapped_column(String(50), nullable=False)
    country_id: Mapped[Optional[str]] = mapped_column(String(36))
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (Index("idx_company", "company_id"), Index("idx_tax_id", "tax_id"))


class CompanyIndustrySizeMaster(Base):
    __tablename__ = "company_industry_size_master"

    industry_size_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    company_id: Mapped[str] = mapped_column(String(36), nullable=False)
    industry_sector_id: Mapped[str] = mapped_column(String(36), nullable=False)
    sub_industry_id: Mapped[str] = mapped_column(String(36), nullable=False)
    industry_code_id: Mapped[str] = mapped_column(String(36), nullable=False)
    annual_turnover_id: Mapped[Optional[str]] = mapped_column(String(36))
    employee_band_id: Mapped[Optional[str]] = mapped_column(String(36))
    manufacturing_plants_count: Mapped[Optional[int]] = mapped_column(Integer)
    sez_eou_presence: Mapped[Optional[bool]] = mapped_column(Boolean)
    revenue_indicator_id: Mapped[str] = mapped_column(String(36), nullable=False)
    spend_indicator_id: Mapped[str] = mapped_column(String(36), nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        UniqueConstraint("company_id", name="uniq_company_industry"),
        Index("idx_sector", "industry_sector_id"),
        Index("idx_sub_sector", "sub_industry_id"),
    )


class EntityTypeMaster(Base):
    __tablename__ = "entity_type_master"

    entity_type_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class GroupMaster(Base):
    __tablename__ = "group_master"

    group_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class IndustryMaster(Base):
    __tablename__ = "industry_master"

    industry_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class SubIndustryMaster(Base):
    __tablename__ = "sub_industry_master"

    sub_industry_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    industry_id: Mapped[str] = mapped_column(String(36), nullable=False)
    sub_industry_name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (Index("ix_sub_industry_industry", "industry_id"),)


class IndustryCodeMaster(Base):
    __tablename__ = "industry_code_master"

    industry_code_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    code_type: Mapped[str] = mapped_column(String(30), nullable=False)
    code_description: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (Index("ix_code_type", "code_type"),)


class NatureOfOperationMaster(Base):
    __tablename__ = "nature_of_operation_master"

    nature_of_operation_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class BusinessModelMaster(Base):
    __tablename__ = "business_model_master"

    business_model_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class AnnualTurnoverMaster(Base):
    __tablename__ = "annual_turnover_master"

    annual_turnover_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    band_label: Mapped[str] = mapped_column(String(50), nullable=False)
    is_indian: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class EmployeeMaster(Base):
    __tablename__ = "employee_master"

    employee_band_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    band_label: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class CountryMaster(Base):
    __tablename__ = "country_master"

    country_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    st_dt: Mapped[datetime] = mapped_column(DateTime, primary_key=True, server_default=func.now())
    e_dt: Mapped[datetime] = mapped_column(DateTime, server_default=text("'9999-12-31'"))
    country_name: Mapped[str] = mapped_column(String(100), nullable=False)
    country_code: Mapped[str] = mapped_column(String(3), nullable=False)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    currency_name: Mapped[str] = mapped_column(String(50), nullable=False)
    flag_link: Mapped[Optional[str]] = mapped_column(String(200))
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        Index("ix_country_id", "country_id"),
        Index("ix_country_code", "country_code"),
        Index("ix_country_active", "active"),
    )


class CompanyManufacturingList(Base):
    __tablename__ = "company_manufacturing_list"

    manufacturing_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    company_id: Mapped[str] = mapped_column(String(36), nullable=False)
    plant_name: Mapped[Optional[str]] = mapped_column(String(255))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    state: Mapped[Optional[str]] = mapped_column(String(100))
    country_id: Mapped[Optional[str]] = mapped_column(String(36))
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (Index("ix_mfg_company", "company_id"),)


class TransactionIndicator(Base):
    __tablename__ = "transaction_indicator"

    indicator_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    indicator_type: Mapped[str] = mapped_column(Enum("Revenue", "Spend", name="indicator_type"), nullable=False)
    indicator_label: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (Index("ix_indicator_type", "indicator_type"),)


class Engagement(Base):
    __tablename__ = "engagement"

    engagement_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, default=uuid_str)
    company_id: Mapped[str] = mapped_column(String(36), nullable=False)
    report_id: Mapped[Optional[str]] = mapped_column(String(36))
    engagement_name: Mapped[str] = mapped_column(String(255), nullable=False)
    engagement_code: Mapped[str] = mapped_column(String(50), nullable=False)
    audit_type: Mapped[str] = mapped_column(
        Enum("Full-scope IA", "IFC", "SOX", name="audit_type"), nullable=False
    )
    reporting_currency: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    audit_fy: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum(
            "Draft",
            "Confirmed",
            "Analysis_Running",
            "Analysis_Completed",
            "Locked",
            name="engagement_status",
        ),
        nullable=False,
        default="Draft",
    )
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    confirmed_by: Mapped[Optional[str]] = mapped_column(String(36))
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (UniqueConstraint("engagement_code", name="uniq_engagement_code"), Index("idx_company", "company_id"))


class EngagementContext(Base):
    __tablename__ = "engagement_context"

    engagement_context_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    engagement_id: Mapped[str] = mapped_column(String(36), nullable=False)
    context_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    st_dt: Mapped[datetime] = mapped_column(DateTime, primary_key=True, server_default=func.now())
    e_dt: Mapped[datetime] = mapped_column(DateTime, server_default=text("'9999-12-31'"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (Index("ix_engagement_context_engagement", "engagement_id"), Index("ix_engagement_context_active", "is_active"))


class BeDimensionMaster(Base):
    __tablename__ = "be_dimension_master"

    dimension_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    dimension_name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class VaMetricGroupMaster(Base):
    __tablename__ = "va_metric_group_master"

    metric_group_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    group_name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class RelevanceReasonMaster(Base):
    __tablename__ = "relevance_reason_master"

    reason_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    reason_label: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class OverrideTypeMaster(Base):
    __tablename__ = "override_type_master"

    override_type_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    override_label: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class RiskThemeMaster(Base):
    __tablename__ = "risk_theme_master"

    risk_theme_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    risk_theme_name: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class RiskLevelMaster(Base):
    __tablename__ = "risk_level_master"

    risk_level_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    risk_level_label: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class AnalysisJob(Base):
    __tablename__ = "analysis_job"

    job_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    engagement_id: Mapped[str] = mapped_column(String(36), nullable=False)
    job_type: Mapped[str] = mapped_column(Enum("BE", "VA", name="analysis_job_type"), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("Running", "Completed", "Failed", "Partial", name="analysis_job_status"),
        nullable=False,
        default="Running",
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (Index("idx_engagement", "engagement_id"), Index("idx_job_type", "job_type"))


class BeInsight(Base):
    __tablename__ = "be_insight"

    be_insight_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    engagement_id: Mapped[str] = mapped_column(String(36), nullable=False)
    dimension_id: Mapped[str] = mapped_column(String(36), nullable=False)
    insight_title: Mapped[str] = mapped_column(String(255), nullable=False)
    insight_statement: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (Index("idx_be_engagement", "engagement_id"), Index("idx_dimension", "dimension_id"))


class BeInsightDriver(Base):
    __tablename__ = "be_insight_driver"

    driver_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    be_insight_id: Mapped[str] = mapped_column(String(36), nullable=False)
    driver_text: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (Index("idx_be_insight", "be_insight_id"),)


class BeInsightValidation(Base):
    __tablename__ = "be_insight_validation"

    be_validation_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    be_insight_id: Mapped[str] = mapped_column(String(36), nullable=False)
    relevance_status: Mapped[str] = mapped_column(
        Enum("Relevant", "Not Relevant", name="insight_relevance_status"),
        nullable=False,
    )
    not_relevant_reason_id: Mapped[Optional[str]] = mapped_column(String(36))
    override_type_id: Mapped[Optional[str]] = mapped_column(String(36))
    user_comment: Mapped[Optional[str]] = mapped_column(Text)
    validated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        UniqueConstraint("be_insight_id", name="uniq_be_validation"),
        Index("idx_be_valid", "be_insight_id"),
    )


class VaInsight(Base):
    __tablename__ = "va_insight"

    va_insight_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    engagement_id: Mapped[str] = mapped_column(String(36), nullable=False)
    metric_group_id: Mapped[str] = mapped_column(String(36), nullable=False)
    metric_code: Mapped[str] = mapped_column(String(50), nullable=False)
    insight_statement: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    trend_direction: Mapped[Optional[str]] = mapped_column(String(20))
    deviation_magnitude: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (Index("idx_va_engagement", "engagement_id"), Index("idx_metric_group", "metric_group_id"))


class VaInsightMetric(Base):
    __tablename__ = "va_insight_metric"

    metric_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    va_insight_id: Mapped[str] = mapped_column(String(36), nullable=False)
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    current_value: Mapped[Optional[float]] = mapped_column(Numeric(18, 4))
    prior_value: Mapped[Optional[float]] = mapped_column(Numeric(18, 4))
    peer_median: Mapped[Optional[float]] = mapped_column(Numeric(18, 4))
    unit: Mapped[Optional[str]] = mapped_column(String(20))
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (Index("idx_va_metric", "va_insight_id"),)


class VaInsightValidation(Base):
    __tablename__ = "va_insight_validation"

    va_validation_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    va_insight_id: Mapped[str] = mapped_column(String(36), nullable=False)
    relevance_status: Mapped[str] = mapped_column(
        Enum("Relevant", "Not Relevant", name="va_insight_relevance_status"),
        nullable=False,
    )
    not_relevant_reason_id: Mapped[Optional[str]] = mapped_column(String(36))
    override_type_id: Mapped[Optional[str]] = mapped_column(String(36))
    user_comment: Mapped[Optional[str]] = mapped_column(Text)
    validated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        UniqueConstraint("va_insight_id", name="uniq_va_validation"),
        Index("idx_va_valid", "va_insight_id"),
    )


class ConsolidatedRiskSignal(Base):
    __tablename__ = "consolidated_risk_signal"

    signal_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    engagement_id: Mapped[str] = mapped_column(String(36), nullable=False)
    risk_theme_id: Mapped[str] = mapped_column(String(36), nullable=False)
    system_score_id: Mapped[str] = mapped_column(String(36), nullable=False)
    user_score_id: Mapped[str] = mapped_column(String(36), nullable=False)
    trend_label: Mapped[Optional[str]] = mapped_column(String(50))
    impact_note: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        Index("idx_signal_eng", "engagement_id"),
        Index("idx_signal_theme", "risk_theme_id"),
    )


class ImpactTypeMaster(Base):
    __tablename__ = "impact_type_master"

    impact_type_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    impact_label: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class TimeHorizonMaster(Base):
    __tablename__ = "time_horizon_master"

    time_horizon_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    horizon_label: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class ProcessMaster(Base):
    __tablename__ = "process_master"

    process_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    process_name: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class SubProcessMaster(Base):
    __tablename__ = "sub_process_master"

    sub_process_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    process_id: Mapped[str] = mapped_column(String(36), nullable=False)
    sub_process_name: Mapped[str] = mapped_column(String(150), nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (Index("idx_sub_process", "process_id"),)


class ProblemStatement(Base):
    __tablename__ = "problem_statement"

    problem_statement_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    engagement_id: Mapped[str] = mapped_column(String(36), nullable=False)
    risk_theme_id: Mapped[str] = mapped_column(String(36), nullable=False)
    system_priority_id: Mapped[str] = mapped_column(String(36), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    statement_text: Mapped[str] = mapped_column(Text, nullable=False)
    value_proposition: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        Enum("Draft", "Reviewed", "Rejected", name="problem_statement_status"),
        nullable=False,
        default="Draft",
    )
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        Index("idx_ps_engagement", "engagement_id"),
        Index("idx_ps_theme", "risk_theme_id"),
    )


class ProblemStatementProcessMap(Base):
    __tablename__ = "problem_statement_process_map"

    map_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    problem_statement_id: Mapped[str] = mapped_column(String(36), nullable=False)
    process_id: Mapped[str] = mapped_column(String(36), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (UniqueConstraint("problem_statement_id", "process_id", name="uniq_ps_process"),)


class ProblemStatementImpactMap(Base):
    __tablename__ = "problem_statement_impact_map"

    map_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    problem_statement_id: Mapped[str] = mapped_column(String(36), nullable=False)
    impact_type_id: Mapped[str] = mapped_column(String(36), nullable=False)
    magnitude_level_id: Mapped[str] = mapped_column(String(36), nullable=False)
    time_horizon_id: Mapped[str] = mapped_column(String(36), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (UniqueConstraint("problem_statement_id", "impact_type_id", name="uniq_ps_impact"),)


class ProblemStatementBeLink(Base):
    __tablename__ = "problem_statement_be_link"

    link_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    problem_statement_id: Mapped[str] = mapped_column(String(36), nullable=False)
    be_insight_id: Mapped[str] = mapped_column(String(36), nullable=False)
    confidence_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (UniqueConstraint("problem_statement_id", "be_insight_id", name="uniq_ps_be"),)


class ProblemStatementVaLink(Base):
    __tablename__ = "problem_statement_va_link"

    link_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    problem_statement_id: Mapped[str] = mapped_column(String(36), nullable=False)
    va_insight_id: Mapped[str] = mapped_column(String(36), nullable=False)
    confidence_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (UniqueConstraint("problem_statement_id", "va_insight_id", name="uniq_ps_va"),)


class ProblemStatementReview(Base):
    __tablename__ = "problem_statement_review"

    review_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    problem_statement_id: Mapped[str] = mapped_column(String(36), nullable=False)
    relevance_status: Mapped[str] = mapped_column(
        Enum("Accepted", "Rejected", name="problem_statement_review_status"),
        nullable=False,
    )
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)
    priority_override_id: Mapped[Optional[str]] = mapped_column(String(36))
    override_comment: Mapped[Optional[str]] = mapped_column(Text)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (UniqueConstraint("problem_statement_id", name="uniq_ps_review"),)


class ScopeOverrideReasonMaster(Base):
    __tablename__ = "scope_override_reason_master"

    reason_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    reason_label: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class UniverseTemplate(Base):
    __tablename__ = "universe_template"

    template_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    template_name: Mapped[str] = mapped_column(String(150), nullable=False)
    industry_sector_id: Mapped[Optional[str]] = mapped_column(String(36))
    sub_industry_id: Mapped[Optional[str]] = mapped_column(String(36))
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class UniverseTemplateProcess(Base):
    __tablename__ = "universe_template_process"

    template_process_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    template_id: Mapped[str] = mapped_column(String(36), nullable=False)
    process_id: Mapped[str] = mapped_column(String(36), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (UniqueConstraint("template_id", "process_id", name="uniq_template_process"),)


class UniverseTemplateSubprocess(Base):
    __tablename__ = "universe_template_subprocess"

    template_subprocess_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    template_process_id: Mapped[str] = mapped_column(String(36), nullable=False)
    sub_process_id: Mapped[str] = mapped_column(String(36), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (UniqueConstraint("template_process_id", "sub_process_id", name="uniq_template_subprocess"),)


class EngagementProcessUniverse(Base):
    __tablename__ = "engagement_process_universe"

    eng_process_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    engagement_id: Mapped[str] = mapped_column(String(36), nullable=False)
    process_id: Mapped[str] = mapped_column(String(36), nullable=False)
    inherent_risk_id: Mapped[str] = mapped_column(String(36), nullable=False)
    system_recommended: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    final_in_scope: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    override_reason_id: Mapped[Optional[str]] = mapped_column(String(36))
    rationale: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (UniqueConstraint("engagement_id", "process_id", name="uniq_eng_process"),)


class EngagementSubprocessUniverse(Base):
    __tablename__ = "engagement_subprocess_universe"

    eng_subprocess_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    engagement_id: Mapped[str] = mapped_column(String(36), nullable=False)
    sub_process_id: Mapped[str] = mapped_column(String(36), nullable=False)
    inherent_risk_id: Mapped[str] = mapped_column(String(36), nullable=False)
    system_recommended: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    final_in_scope: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    override_reason_id: Mapped[Optional[str]] = mapped_column(String(36))
    rationale: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (UniqueConstraint("engagement_id", "sub_process_id", name="uniq_eng_subprocess"),)


class EngagementProcessProblemMap(Base):
    __tablename__ = "engagement_process_problem_map"

    map_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    engagement_id: Mapped[str] = mapped_column(String(36), nullable=False)
    process_id: Mapped[str] = mapped_column(String(36), nullable=False)
    problem_statement_id: Mapped[str] = mapped_column(String(36), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        UniqueConstraint("engagement_id", "process_id", "problem_statement_id", name="uniq_eng_proc_ps"),
    )


class AuditFrequencyMaster(Base):
    __tablename__ = "audit_frequency_master"

    frequency_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    frequency_label: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class AuditPlanTypeMaster(Base):
    __tablename__ = "audit_plan_type_master"

    plan_type_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    plan_type_label: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class AuditArea(Base):
    __tablename__ = "audit_area"

    audit_area_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    engagement_id: Mapped[str] = mapped_column(String(36), nullable=False)
    audit_area_name: Mapped[str] = mapped_column(String(150), nullable=False)
    scope_description: Mapped[Optional[str]] = mapped_column(Text)
    inherent_risk_id: Mapped[str] = mapped_column(String(36), nullable=False)
    system_suggested_frequency_id: Mapped[Optional[str]] = mapped_column(String(36))
    final_frequency_id: Mapped[Optional[str]] = mapped_column(String(36))
    plan_type_id: Mapped[Optional[str]] = mapped_column(String(36))
    planned_period: Mapped[Optional[str]] = mapped_column(String(30))
    planned_start: Mapped[Optional[date]] = mapped_column(Date)
    planned_end: Mapped[Optional[date]] = mapped_column(Date)
    assigned_team: Mapped[Optional[str]] = mapped_column(String(255))
    locations: Mapped[Optional[str]] = mapped_column(Text)
    dependencies: Mapped[Optional[str]] = mapped_column(Text)
    rationale: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (Index("idx_audit_area_eng", "engagement_id"),)


class AuditAreaProcessMap(Base):
    __tablename__ = "audit_area_process_map"

    map_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    audit_area_id: Mapped[str] = mapped_column(String(36), nullable=False)
    process_id: Mapped[str] = mapped_column(String(36), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (UniqueConstraint("audit_area_id", "process_id", name="uniq_audit_area_process"),)


class AuditAreaSubprocessMap(Base):
    __tablename__ = "audit_area_subprocess_map"

    map_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    audit_area_id: Mapped[str] = mapped_column(String(36), nullable=False)
    eng_subprocess_id: Mapped[str] = mapped_column(String(36), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (UniqueConstraint("audit_area_id", "eng_subprocess_id", name="uniq_audit_area_subprocess"),)


class AuditPlanStatus(Base):
    __tablename__ = "audit_plan_status"

    engagement_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    status: Mapped[str] = mapped_column(
        Enum("Draft", "Sent", "Approved", "Locked", name="audit_plan_status"),
        nullable=False,
        default="Draft",
    )
    locked_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

