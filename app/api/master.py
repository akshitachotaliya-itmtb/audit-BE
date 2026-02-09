from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.deps import get_current_user
from app.schemas.db import (
    AnnualTurnoverMaster,
    BusinessModelMaster,
    CountryMaster,
    EmployeeMaster,
    EntityTypeMaster,
    GroupMaster,
    IndustryCodeMaster,
    IndustryMaster,
    NatureOfOperationMaster,
    SubIndustryMaster,
    TransactionIndicator,
    get_db,
)

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/entity-types")
def get_entity_types(db: Session = Depends(get_db)):
    rows = db.query(EntityTypeMaster).order_by(EntityTypeMaster.entity_type_id).all()
    return [{"id": r.entity_type_id, "name": r.name} for r in rows]


@router.get("/groups")
def get_groups(db: Session = Depends(get_db)):
    rows = db.query(GroupMaster).order_by(GroupMaster.group_id).all()
    return [{"id": r.group_id, "name": r.name} for r in rows]


@router.get("/industries")
def get_industries(db: Session = Depends(get_db)):
    rows = db.query(IndustryMaster).order_by(IndustryMaster.industry_id).all()
    return [{"id": r.industry_id, "name": r.name} for r in rows]


@router.get("/sub-industries")
def get_sub_industries(sector_id: int | None = Query(default=None), db: Session = Depends(get_db)):
    query = db.query(SubIndustryMaster)
    if sector_id:
        query = query.filter(SubIndustryMaster.industry_id == sector_id)
    rows = query.order_by(SubIndustryMaster.sub_industry_id).all()
    return [{"id": r.sub_industry_id, "sector_id": r.industry_id, "name": r.sub_industry_name} for r in rows]


@router.get("/industry-codes")
def get_industry_codes(code_type: str | None = Query(default=None), db: Session = Depends(get_db)):
    query = db.query(IndustryCodeMaster)
    if code_type:
        query = query.filter(IndustryCodeMaster.code_type == code_type)
    rows = query.order_by(IndustryCodeMaster.industry_code_id).all()
    return [
        {"id": r.industry_code_id, "code_type": r.code_type, "description": r.code_description}
        for r in rows
    ]


@router.get("/nature-operations")
def get_nature_of_operations(db: Session = Depends(get_db)):
    rows = db.query(NatureOfOperationMaster).order_by(NatureOfOperationMaster.nature_of_operation_id).all()
    return [{"id": r.nature_of_operation_id, "name": r.name} for r in rows]


@router.get("/business-models")
def get_business_models(db: Session = Depends(get_db)):
    rows = db.query(BusinessModelMaster).order_by(BusinessModelMaster.business_model_id).all()
    return [{"id": r.business_model_id, "name": r.name} for r in rows]


@router.get("/annual-turnovers")
def get_annual_turnovers(db: Session = Depends(get_db)):
    rows = db.query(AnnualTurnoverMaster).order_by(AnnualTurnoverMaster.annual_turnover_id).all()
    return [{"id": r.annual_turnover_id, "label": r.band_label} for r in rows]


@router.get("/employees")
def get_employee_bands(db: Session = Depends(get_db)):
    rows = db.query(EmployeeMaster).order_by(EmployeeMaster.employee_band_id).all()
    return [{"id": r.employee_band_id, "label": r.band_label} for r in rows]


@router.get("/transaction-indicators")
def get_transaction_indicators(db: Session = Depends(get_db)):
    rows = db.query(TransactionIndicator).order_by(TransactionIndicator.indicator_id).all()
    return [{"id": r.indicator_id, "type": r.indicator_type, "label": r.indicator_label} for r in rows]


@router.get("/countries")
def get_countries(db: Session = Depends(get_db)):
    now = func.now()
    rows = (
        db.query(CountryMaster)
        .filter(
            CountryMaster.active.is_(True),
            CountryMaster.is_active.is_(True),
            CountryMaster.st_dt <= now,
            CountryMaster.e_dt > now,
        )
        .order_by(CountryMaster.country_name)
        .all()
    )
    return [
        {
            "id": r.country_id,
            "name": r.country_name,
            "code": r.country_code,
            "currency_code": r.currency_code,
            "currency_name": r.currency_name,
        }
        for r in rows
    ]
