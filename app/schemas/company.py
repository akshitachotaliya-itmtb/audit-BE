from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CompanySearchResult(BaseModel):
    company_id: str
    legal_name: str
    country_id: str
    cin: str | None = None
    sector: str | None = None


class CompanyDetail(BaseModel):
    company_id: str
    legal_name: str
    display_name: str | None = None
    entity_type_id: str
    country_id: str
    registered_address: str
    operational_hq_address: str | None = None
    is_part_of_group: bool = False
    parent_group_id: str | None = None
    status: str = "Draft"


class CompanyCreateRequest(BaseModel):
    legal_name: str
    display_name: str | None = None
    entity_type_id: str
    country_id: str
    registered_address: str
    operational_hq_address: str | None = None
    is_part_of_group: bool = False
    parent_group_id: str | None = None
    cin: str | None = None


class RegulatoryUpsertRequest(BaseModel):
    company_id: str
    cin: str | None = None
    pan: str
    lei: str | None = None
    listed_status: str = Field(..., pattern="^(Listed|Unlisted)$")
    exchange_list: list[str] | None = None
    ticker_symbol: str | None = None


class IndustrySizeUpsertRequest(BaseModel):
    company_id: str
    industry_sector_id: str
    sub_industry_id: str
    industry_code_id: str
    annual_turnover_id: str | None = None
    employee_band_id: str | None = None
    manufacturing_plants_count: int | None = None
    sez_eou_presence: bool | None = None
    revenue_indicator_id: str
    spend_indicator_id: str


class TaxRegistrationItem(BaseModel):
    tax_type: str
    tax_id: str
    country_id: str | None = None


class TaxRegistrationReplaceRequest(BaseModel):
    company_id: str
    items: list[TaxRegistrationItem]


class ManufacturingItem(BaseModel):
    plant_name: str | None = None
    city: str | None = None
    state: str | None = None
    country_id: str | None = None


class ManufacturingReplaceRequest(BaseModel):
    company_id: str
    items: list[ManufacturingItem]


class EngagementCreateRequest(BaseModel):
    company_id: str
    engagement_name: str
    engagement_code: str
    audit_type: str
    reporting_currency: list[str]
    audit_fy: str


class EngagementContextCreateRequest(BaseModel):
    engagement_id: str
    context: dict[str, Any]
