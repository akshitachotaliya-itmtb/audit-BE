from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from fastapi import Request
from app.deps import extract_user_identity
from app.schemas.db import (
    CompanyIndustrySizeMaster,
    CompanyManufacturingList,
    CompanyMaster,
    CompanyTaxRegistration,
    Engagement,
    EngagementContext,
    RegulatoryMaster,
    get_db,
)
from app.schemas.company import (
    CompanyCreateRequest,
    CompanyDetail,
    CompanySearchResult,
    EngagementContextCreateRequest,
    EngagementCreateRequest,
    IndustrySizeUpsertRequest,
    ManufacturingReplaceRequest,
    RegulatoryUpsertRequest,
    TaxRegistrationReplaceRequest,
)

# Router-level auth is handled by AuthMiddleware in main.py
# All requests must have valid Authorization: Bearer <token> or X-Service-Token
router = APIRouter()


def _safe_int(value: object, default: int = 1) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


@router.get("/company-search", response_model=list[CompanySearchResult])
def search_company_master(
    request: Request,
    q: str | None = Query(default=None, description="Search by company name"),
    db: Session = Depends(get_db),
):
    # Extract user identity (reusable helper)
    _, tenant_id = extract_user_identity(request)
    query = (
        db.query(CompanyMaster, RegulatoryMaster, CompanyIndustrySizeMaster)
        .outerjoin(RegulatoryMaster, RegulatoryMaster.company_id == CompanyMaster.company_id)
        .outerjoin(CompanyIndustrySizeMaster, CompanyIndustrySizeMaster.company_id == CompanyMaster.company_id)
    )
    
    # Optional: Filter by tenant_id if available (for multi-tenant isolation)
    # Uncomment if your CompanyMaster has tenant_id column
    # if tenant_id:
    #     query = query.filter(CompanyMaster.tenant_id == tenant_id)
    
    if q:
        like = f"%{q}%"
        query = query.filter(or_(CompanyMaster.legal_name.ilike(like), CompanyMaster.display_name.ilike(like)))

    rows = query.all()
    results: list[CompanySearchResult] = []
    for company, regulatory, industry in rows:
        sector_val = None
        if industry and industry.industry_sector_id is not None:
            sector_val = str(industry.industry_sector_id)
        results.append(
            CompanySearchResult(
                company_id=company.company_id,
                legal_name=company.legal_name,
                country_id=company.country_id,
                cin=regulatory.cin if regulatory else None,
                sector=sector_val,
            )
        )
    return results


@router.get("/company-master", response_model=CompanyDetail)
def get_company_master_detail(
    request: Request,
    company_id: str = Query(...),
    db: Session = Depends(get_db),
):
    # Extract user identity (reusable helper)
    _, tenant_id = extract_user_identity(request)
    query = db.query(CompanyMaster).filter(CompanyMaster.company_id == company_id)
    
    # Optional: Add tenant filtering if needed
    # if tenant_id:
    #     query = query.filter(CompanyMaster.tenant_id == tenant_id)
    
    company = query.first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return CompanyDetail(
        company_id=company.company_id,
        legal_name=company.legal_name,
        display_name=company.display_name,
        entity_type_id=company.entity_type_id,
        country_id=company.country_id,
        registered_address=company.registered_address,
        operational_hq_address=company.operational_hq_address,
        is_part_of_group=company.is_part_of_group,
        parent_group_id=company.parent_group_id,
        status=company.status,
    )


@router.post("/company-create")
def create_company_master(
    payload: CompanyCreateRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    # Extract user identity (reusable helper)
    actor_user_id, tenant_id = extract_user_identity(request)
    
    if not actor_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User authentication required",
        )
    
    created_by = actor_user_id
    if payload.cin:
        duplicate = (
            db.query(CompanyMaster.company_id)
            .join(RegulatoryMaster, RegulatoryMaster.company_id == CompanyMaster.company_id)
            .filter(func.lower(CompanyMaster.legal_name) == func.lower(payload.legal_name))
            .filter(RegulatoryMaster.cin == payload.cin)
            .first()
        )
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Company with same legal name and CIN already exists",
            )

    created_by = str(actor_user_id)
    company = CompanyMaster(
        legal_name=payload.legal_name,
        display_name=payload.display_name,
        entity_type_id=payload.entity_type_id,
        country_id=payload.country_id,
        registered_address=payload.registered_address,
        operational_hq_address=payload.operational_hq_address,
        is_part_of_group=payload.is_part_of_group,
        parent_group_id=payload.parent_group_id,
        created_by=created_by,
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return {"message": "Company created", "company_id": company.company_id}


@router.post("/regulatory-upsert")
def upsert_regulatory_master(
    payload: RegulatoryUpsertRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    # Extract user identity (reusable helper)
    actor_user_id, _ = extract_user_identity(request)
    company = db.query(CompanyMaster).filter(CompanyMaster.company_id == payload.company_id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    if payload.cin:
        duplicate = (
            db.query(RegulatoryMaster.company_id)
            .join(CompanyMaster, CompanyMaster.company_id == RegulatoryMaster.company_id)
            .filter(func.lower(CompanyMaster.legal_name) == func.lower(company.legal_name))
            .filter(RegulatoryMaster.cin == payload.cin)
            .filter(RegulatoryMaster.company_id != payload.company_id)
            .first()
        )
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Company with same legal name and CIN already exists",
            )

    record = db.query(RegulatoryMaster).filter(RegulatoryMaster.company_id == payload.company_id).first()
    if record:
        record.cin = payload.cin
        record.pan = payload.pan
        record.lei = payload.lei
        record.listed_status = payload.listed_status
        record.exchange_list = payload.exchange_list
        record.ticker_symbol = payload.ticker_symbol
    else:
        record = RegulatoryMaster(
            company_id=payload.company_id,
            cin=payload.cin,
            pan=payload.pan,
            lei=payload.lei,
            listed_status=payload.listed_status,
            exchange_list=payload.exchange_list,
            ticker_symbol=payload.ticker_symbol,
        )
        db.add(record)
    db.commit()
    return {"message": "Regulatory data upserted", "company_id": payload.company_id}


@router.post("/industry-size-upsert")
def upsert_industry_size_profile(
    payload: IndustrySizeUpsertRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    # Extract user identity (reusable helper)
    actor_user_id, _ = extract_user_identity(request)
    record = (
        db.query(CompanyIndustrySizeMaster)
        .filter(CompanyIndustrySizeMaster.company_id == payload.company_id)
        .first()
    )
    if record:
        record.industry_sector_id = payload.industry_sector_id
        record.sub_industry_id = payload.sub_industry_id
        record.industry_code_id = payload.industry_code_id
        record.annual_turnover_id = payload.annual_turnover_id
        record.employee_band_id = payload.employee_band_id
        record.manufacturing_plants_count = payload.manufacturing_plants_count
        record.sez_eou_presence = payload.sez_eou_presence
        record.revenue_indicator_id = payload.revenue_indicator_id
        record.spend_indicator_id = payload.spend_indicator_id
    else:
        record = CompanyIndustrySizeMaster(
            company_id=payload.company_id,
            industry_sector_id=payload.industry_sector_id,
            sub_industry_id=payload.sub_industry_id,
            industry_code_id=payload.industry_code_id,
            annual_turnover_id=payload.annual_turnover_id,
            employee_band_id=payload.employee_band_id,
            manufacturing_plants_count=payload.manufacturing_plants_count,
            sez_eou_presence=payload.sez_eou_presence,
            revenue_indicator_id=payload.revenue_indicator_id,
            spend_indicator_id=payload.spend_indicator_id,
        )
        db.add(record)
    db.commit()
    return {"message": "Industry/size profile upserted", "company_id": payload.company_id}


@router.post("/tax-registration-replace")
def replace_tax_registrations_for_company(
    payload: TaxRegistrationReplaceRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    # Extract user identity (reusable helper)
    actor_user_id, _ = extract_user_identity(request)
    db.query(CompanyTaxRegistration).filter(CompanyTaxRegistration.company_id == payload.company_id).delete()
    for item in payload.items:
        db.add(
            CompanyTaxRegistration(
                company_id=payload.company_id,
                tax_type=item.tax_type,
                tax_id=item.tax_id,
                country_id=item.country_id,
            )
        )
    db.commit()
    return {"message": "Tax registrations replaced", "company_id": payload.company_id, "count": len(payload.items)}


@router.post("/manufacturing-replace")
def replace_manufacturing_for_company(
    payload: ManufacturingReplaceRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    # Extract user identity (reusable helper)
    actor_user_id, _ = extract_user_identity(request)
    db.query(CompanyManufacturingList).filter(CompanyManufacturingList.company_id == payload.company_id).delete()
    for item in payload.items:
        db.add(
            CompanyManufacturingList(
                company_id=payload.company_id,
                plant_name=item.plant_name,
                city=item.city,
                state=item.state,
                country_id=item.country_id,
            )
        )
    db.commit()
    return {"message": "Manufacturing list replaced", "company_id": payload.company_id, "count": len(payload.items)}


@router.post("/engagement-create")
def create_engagement(
    payload: EngagementCreateRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    # Extract user identity (reusable helper)
    actor_user_id, tenant_id = extract_user_identity(request)
    engagement = Engagement(
        company_id=payload.company_id,
        engagement_name=payload.engagement_name,
        engagement_code=payload.engagement_code,
        audit_type=payload.audit_type,
        reporting_currency=payload.reporting_currency,
        audit_fy=payload.audit_fy,
    )
    db.add(engagement)
    db.commit()
    db.refresh(engagement)
    return {"message": "Engagement created", "engagement_id": engagement.engagement_id}


@router.post("/engagement-context")
def create_engagement_context(
    payload: EngagementContextCreateRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    # Extract user identity (reusable helper)
    actor_user_id, _ = extract_user_identity(request)
    engagement = db.query(Engagement).filter(Engagement.engagement_id == payload.engagement_id).first()
    if not engagement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Engagement not found")

    db.query(EngagementContext).filter(
        EngagementContext.engagement_id == payload.engagement_id,
        EngagementContext.e_dt > func.now(),
        EngagementContext.is_active.is_(True),
    ).update(
        {EngagementContext.e_dt: func.now(), EngagementContext.is_active: False},
        synchronize_session=False,
    )

    record = EngagementContext(
        engagement_context_id=str(uuid4()),
        engagement_id=payload.engagement_id,
        context_json=payload.context,
    )
    db.add(record)
    db.commit()
    return {"message": "Engagement context saved", "engagement_id": payload.engagement_id}
