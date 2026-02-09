from __future__ import annotations

from pydantic import BaseModel, Field


class CompanySearchResult(BaseModel):
    company_id: int
    legal_name: str
    country_id: int
    cin: str | None = None
    sector: str | None = None


class CompanyDetail(BaseModel):
    company_id: int
    legal_name: str
    display_name: str | None = None
    entity_type_id: int
    country_id: int
    registered_address: str
    operational_hq_address: str | None = None
    is_part_of_group: bool = False
    parent_group_id: int | None = None
    status: str = "Draft"


class CompanyCreateRequest(BaseModel):
    legal_name: str
    display_name: str | None = None
    entity_type_id: int
    country_id: int
    registered_address: str
    operational_hq_address: str | None = None
    is_part_of_group: bool = False
    parent_group_id: int | None = None
    cin: str | None = None


class RegulatoryUpsertRequest(BaseModel):
    company_id: int
    cin: str | None = None
    pan: str
    lei: str | None = None
    listed_status: str = Field(..., pattern="^(Listed|Unlisted)$")
    exchange_list: list[str] | None = None
    ticker_symbol: str | None = None


class IndustrySizeUpsertRequest(BaseModel):
    company_id: int
    industry_sector_id: int
    sub_industry_id: int
    industry_code_id: int
    annual_turnover_id: int | None = None
    employee_band_id: int | None = None
    manufacturing_plants_count: int | None = None
    sez_eou_presence: bool | None = None
    revenue_indicator_id: int
    spend_indicator_id: int


class TaxRegistrationItem(BaseModel):
    tax_type: str
    tax_id: str
    country_id: int | None = None


class TaxRegistrationReplaceRequest(BaseModel):
    company_id: int
    items: list[TaxRegistrationItem]


class ManufacturingItem(BaseModel):
    plant_name: str | None = None
    city: str | None = None
    state: str | None = None
    country_id: int | None = None


class ManufacturingReplaceRequest(BaseModel):
    company_id: int
    items: list[ManufacturingItem]


class EngagementCreateRequest(BaseModel):
    company_id: int
    engagement_name: str
    engagement_code: str
    audit_type: str
    reporting_currency: list[str]
    audit_fy: str
