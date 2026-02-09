# Internal Audit - BE Codebase Analysis

## Executive Summary

The **Internal Audit - BE** is a FastAPI-based microservice designed to manage internal audit engagements, company master data, business environment (BE) insights, variance analysis (VA) insights, problem statements, risk universe, and audit planning. It's part of a larger microservices architecture with centralized authentication and authorization.

---

## 1. Architecture Overview

### 1.1 Technology Stack
- **Framework**: FastAPI 0.115.0
- **Database**: MySQL 8.x (via PyMySQL 1.1.2)
- **ORM**: SQLAlchemy 2.0.46
- **Validation**: Pydantic 2.9.2
- **Server**: Uvicorn 0.30.6
- **Authentication**: JWT-based with ITMTB Auth SDK
- **Language**: Python 3.12+

### 1.2 Architecture Pattern
- **Microservice Architecture**: Part of a distributed system
- **RESTful API**: Standard HTTP endpoints
- **Database-First Design**: SQLAlchemy ORM with declarative models
- **Dependency Injection**: FastAPI's dependency system for DB sessions and auth

### 1.3 Project Structure
```
Internal Audit - BE/
├── app/
│   ├── api/              # API route handlers
│   │   ├── company.py   # Company & engagement endpoints
│   │   └── master.py    # Master data endpoints
│   ├── auth/            # Authentication modules
│   │   ├── auth_middleware.py    # Request authentication middleware
│   │   ├── itmtb_auth_sdk.py    # Auth service client
│   │   └── rbac_guard.py        # Role-based access control
│   ├── config/          # Configuration
│   │   └── db_config.py # Database connection config
│   ├── schemas/         # Pydantic models & SQLAlchemy models
│   │   ├── company.py   # Company request/response schemas
│   │   ├── db.py        # SQLAlchemy ORM models (all tables)
│   │   └── payload.py   # Request payload schemas
│   └── deps.py          # FastAPI dependencies (auth, DB)
├── main.py              # FastAPI application entry point
├── ddl.sql              # Database schema definitions
├── seed.sql             # Initial data seeding
├── requirements.txt     # Python dependencies
└── README.md            # Setup instructions
```

---

## 2. Database Schema

### 2.1 Core Entities

#### **Company Master** (`company_master`)
- Primary entity for storing company information
- Fields: `company_id` (UUID), `legal_name`, `display_name`, `entity_type_id`, `country_id`, addresses, group relationships
- Status workflow: `Draft` → `Confirmed` → `Archived`
- Indexed on: `legal_name`, `country_id`, `entity_type_id`, `parent_group_id`

#### **Regulatory Master** (`regulatory_master`)
- One-to-one with `company_master`
- Stores: CIN, PAN, LEI, listing status, exchange list, ticker symbol
- Unique constraint on `company_id`

#### **Company Industry Size Master** (`company_industry_size_master`)
- One-to-one with `company_master`
- Stores industry classification, size metrics, manufacturing details
- Links to: `industry_sector_id`, `sub_industry_id`, `industry_code_id`, `annual_turnover_id`, `employee_band_id`
- Transaction indicators: `revenue_indicator_id`, `spend_indicator_id`

#### **Engagement** (`engagement`)
- Core audit engagement record
- Links to: `company_id`, `user_id`, `report_id`
- Fields: `engagement_name`, `engagement_code`, `audit_type` (Full-scope IA/IFC/SOX), `reporting_currency` (JSON array), `audit_fy`
- Status: `Draft` → `Confirmed` → `Analysis_Running` → `Analysis_Completed` → `Locked`
- Unique constraint on `engagement_code`

#### **Engagement Context** (`engagement_context`)
- Temporal JSON storage for engagement context
- Uses `st_dt`/`e_dt` pattern for versioning
- Stores flexible JSON context data

### 2.2 Master Data Tables

**Reference Data:**
- `entity_type_master` - Legal entity types
- `group_master` - Parent groups
- `industry_master` - Industry sectors
- `sub_industry_master` - Sub-industries (linked to industries)
- `industry_code_master` - Industry codes (NIC/NAICS)
- `nature_of_operation_master` - Operation types
- `business_model_master` - Business models (B2B/B2C/etc.)
- `annual_turnover_master` - Turnover bands
- `employee_master` - Employee count bands
- `transaction_indicator` - Revenue/Spend indicators
- `country_master` - Countries (temporal with `st_dt`/`e_dt`)

**Supporting Lists:**
- `company_tax_registration` - Tax IDs (GST/VAT) - one-to-many
- `company_manufacturing_list` - Manufacturing plants - one-to-many

### 2.3 Analysis & Insights Tables

#### **Analysis Jobs** (`analysis_job`)
- Tracks BE/VA analysis execution
- Types: `BE` (Business Environment), `VA` (Variance Analysis)
- Status: `Running` → `Completed`/`Failed`/`Partial`

#### **BE Insights** (`be_insight`)
- Business environment insights per engagement
- Links to: `dimension_id` (from `be_dimension_master`)
- Fields: `insight_title`, `insight_statement`, `confidence_score`
- Related: `be_insight_driver` (supporting drivers), `be_insight_validation` (user validation)

#### **VA Insights** (`va_insight`)
- Variance analysis insights per engagement
- Links to: `metric_group_id` (from `va_metric_group_master`)
- Fields: `metric_code`, `insight_statement`, `confidence_score`, `trend_direction`, `deviation_magnitude`
- Related: `va_insight_metric` (metric details), `va_insight_validation` (user validation)

#### **Consolidated Risk Signals** (`consolidated_risk_signal`)
- Aggregated risk signals by `risk_theme_id`
- Stores system and user scores, trend labels, impact notes

### 2.4 Problem Statements & Risk Universe

#### **Problem Statements** (`problem_statement`)
- System-generated problem statements from insights
- Links to: `risk_theme_id`, `system_priority_id`
- Status: `Draft` → `Reviewed`/`Rejected`
- Related mappings:
  - `problem_statement_process_map` - Process associations
  - `problem_statement_impact_map` - Impact classifications
  - `problem_statement_be_link` - BE insight links
  - `problem_statement_va_link` - VA insight links
  - `problem_statement_review` - User review decisions

#### **Risk Universe** (Process/Sub-process)
- `engagement_process_universe` - Process-level scope decisions
- `engagement_subprocess_universe` - Sub-process-level scope decisions
- Fields: `inherent_risk_id`, `system_recommended`, `final_in_scope`, `override_reason_id`, `rationale`
- Templates: `universe_template`, `universe_template_process`, `universe_template_subprocess`

### 2.5 Audit Planning

#### **Audit Areas** (`audit_area`)
- Final audit areas for engagement
- Fields: `audit_area_name`, `scope_description`, `inherent_risk_id`, frequency, timing, team assignment
- Related: `audit_area_process_map`, `audit_area_subprocess_map`

#### **Audit Plan Status** (`audit_plan_status`)
- Tracks plan lifecycle: `Draft` → `Sent` → `Approved` → `Locked`

### 2.6 Design Patterns

**Temporal Tables:**
- `country_master`, `engagement_context` use `st_dt`/`e_dt` for versioning
- Allows historical tracking without data loss

**Soft Deletes:**
- All tables have `is_active` boolean flag
- Enables logical deletion without physical removal

**UUID Primary Keys:**
- Most tables use `CHAR(36)` UUIDs for primary keys
- Generated via `uuid_str()` function (SQLAlchemy default)

**Enum Types:**
- Status fields use MySQL ENUMs for type safety
- Examples: `company_status`, `engagement_status`, `audit_type`, `listed_status`

---

## 3. API Endpoints

### 3.1 Master Data Endpoints (`/api`)

All master endpoints are **GET** requests returning lookup lists:

| Endpoint | Description | Response |
|----------|-------------|----------|
| `/entity-types` | Legal entity types | `[{id, name}]` |
| `/groups` | Parent groups | `[{id, name}]` |
| `/industries` | Industry sectors | `[{id, name}]` |
| `/sub-industries` | Sub-industries (optional `sector_id` filter) | `[{id, sector_id, name}]` |
| `/industry-codes` | Industry codes (optional `code_type` filter) | `[{id, code_type, description}]` |
| `/nature-operations` | Nature of operations | `[{id, name}]` |
| `/business-models` | Business models | `[{id, name}]` |
| `/annual-turnovers` | Turnover bands | `[{id, label}]` |
| `/employees` | Employee bands | `[{id, label}]` |
| `/transaction-indicators` | Revenue/Spend indicators | `[{id, type, label}]` |
| `/countries` | Active countries (filtered by date) | `[{id, name, code, currency_code, currency_name}]` |

### 3.2 Company Management Endpoints (`/api`)

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| GET | `/company-search` | Search companies by name | Query: `q` (optional) |
| GET | `/company-master` | Get company details | Query: `company_id` |
| POST | `/company-create` | Create new company | `CompanyCreateRequest` |
| POST | `/regulatory-upsert` | Upsert regulatory data | `RegulatoryUpsertRequest` |
| POST | `/industry-size-upsert` | Upsert industry/size profile | `IndustrySizeUpsertRequest` |
| POST | `/tax-registration-replace` | Replace tax registrations | `TaxRegistrationReplaceRequest` |
| POST | `/manufacturing-replace` | Replace manufacturing list | `ManufacturingReplaceRequest` |
| POST | `/engagement-create` | Create engagement | `EngagementCreateRequest` |
| POST | `/engagement-context` | Save engagement context | `EngagementContextCreateRequest` |

### 3.3 Request/Response Schemas

**CompanyCreateRequest:**
```python
{
  "legal_name": str,
  "display_name": str | None,
  "entity_type_id": str,
  "country_id": str,
  "registered_address": str,
  "operational_hq_address": str | None,
  "is_part_of_group": bool,
  "parent_group_id": str | None,
  "cin": str | None
}
```

**RegulatoryUpsertRequest:**
```python
{
  "company_id": str,
  "cin": str | None,
  "pan": str,
  "lei": str | None,
  "listed_status": "Listed" | "Unlisted",
  "exchange_list": list[str] | None,
  "ticker_symbol": str | None
}
```

**IndustrySizeUpsertRequest:**
```python
{
  "company_id": str,
  "industry_sector_id": str,
  "sub_industry_id": str,
  "industry_code_id": str,
  "annual_turnover_id": str | None,
  "employee_band_id": str | None,
  "manufacturing_plants_count": int | None,
  "sez_eou_presence": bool | None,
  "revenue_indicator_id": str,
  "spend_indicator_id": str
}
```

---

## 4. Authentication & Authorization

### 4.1 Authentication Flow

**Two-Tier Authentication:**
1. **User Authentication**: `Authorization: Bearer <JWT>` header
   - Validated via Auth Microservice
   - Token verified at `/verify` endpoint
   - User identity stored in `request.state.user_identity`

2. **Service Authentication**: `X-Service-Token: <JWT>` header
   - For inter-service communication
   - Verified locally via JWKS (JSON Web Key Set)
   - Service identity stored in `request.state.service_identity`

### 4.2 Auth Middleware (`auth_middleware.py`)

**Responsibilities:**
- Validates `X-Service-Token` (internal calls) via local JWT verification
- Validates `Authorization: Bearer <JWT>` (external calls) via Auth MS
- Attaches identities to `request.state`
- **Enforces**: At least one identity must be present (no anonymous access)

**Flow:**
```
Request → AuthMiddleware.dispatch()
  ├─ Check X-Service-Token → verify_service_token() → request.state.service_identity
  ├─ Check Authorization → verify_user_token() → request.state.user_identity
  └─ Enforce: user_identity OR service_identity must exist
```

### 4.3 Auth SDK (`itmtb_auth_sdk.py`)

**AuthClient Features:**
- **Service Token Management**: Cached service tokens with TTL (9 minutes default)
- **User Token Verification**: Calls Auth MS `/verify` endpoint
- **Service Token Verification**: Local JWKS-based verification
- **Cross-Service Calls**: `call_service()` helper with automatic token injection
- **JWKS Caching**: 5-minute TTL for JWKS keys

**Key Methods:**
- `get_service_token()` - Returns cached or fresh service token
- `verify_user_token(token)` - Validates user JWT via Auth MS
- `verify_service_token(token)` - Validates service JWT locally
- `call_service(service_name, path, ...)` - Makes authenticated cross-service calls

### 4.4 RBAC Guard (`rbac_guard.py`)

**Purpose**: Enforce role-based access control via RBAC service

**Usage:**
```python
@router.post("/endpoint")
async def endpoint(request: Request, dep: dict = Depends(require("activity_name"))):
    # User has permission to perform "activity_name"
    ...
```

**Flow:**
1. Extract `user_id` from token (via middleware state or Auth MS)
2. Extract `project_id`/`tenant_id` from token (preferred) or query/header/body
3. Call RBAC service: `POST /authz/direct/check`
4. Payload: `{userId, projectId, activity, requiredRoles?}`
5. Returns: `{data: {allowed: bool}}`

### 4.5 Current Implementation

**Simple Auth Dependency** (`deps.py`):
```python
def get_current_user(authorization: str | None = Header(default=None)) -> dict:
    if not authorization:
        raise HTTPException(401, "Missing Authorization header")
    return {"user_id": "demo-user"}  # Placeholder
```

**Note**: Currently returns a placeholder. Should integrate with `AuthMiddleware` or `AuthClient` for production.

**Router Protection:**
```python
router = APIRouter(dependencies=[Depends(get_current_user)])
```
All routes in `master.py` and `company.py` require authentication.

---

## 5. Database Configuration

### 5.1 Connection Setup (`config/db_config.py`)

**Environment-Based Configuration:**
- `RUNNING_ENV`: `dev` (default), `test`, `prod`
- Database credentials from environment variables:
  - `DATABASE_HOST` (default: `localhost`)
  - `DATABASE_USER` (default: `root`)
  - `DATABASE_PASSWORD`
  - `DATABASE_NAME`
  - `DATABASE_PORT` (default: `3306`)

**Connection String:**
```python
DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
```

**Session Management:**
- `SessionLocal` created with `sessionmaker`
- `autocommit=False`, `autoflush=False`
- Connection pooling via `pool_pre_ping=True`

### 5.2 Database Dependency (`schemas/db.py`)

**get_db() Generator:**
```python
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Used in all endpoints via `Depends(get_db)`.

---

## 6. Business Logic Flow

### 6.1 Screen 1: Company Master Setup

**Workflow:**
1. **Search Company**: `GET /company-search?q=<name>`
2. **If Found**: `GET /company-master?company_id=<id>` → Populate form
3. **If New**: `POST /company-create` → Get `company_id`
4. **Regulatory Data**: `POST /regulatory-upsert`
5. **Industry/Size**: `POST /industry-size-upsert`
6. **Tax Registrations**: `POST /tax-registration-replace`
7. **Manufacturing**: `POST /manufacturing-replace`
8. **Create Engagement**: `POST /engagement-create`
9. **Save Context**: `POST /engagement-context`

**Validation:**
- Duplicate check: Same `legal_name` + `CIN` combination
- Required fields enforced at Pydantic level
- Status transitions: `Draft` → `Confirmed`

### 6.2 Screen 2: Business Environment & Variance Analysis

**Planned Endpoints** (from `endpoints.txt`):
- `POST /analysis-run` - Trigger BE/VA jobs
- `GET /analysis-status` - Check job status
- `GET /be-insights` - Get BE insights by dimension
- `GET /va-insights` - Get VA insights by metric group
- `POST /be-insight-validate` - Validate BE insights
- `POST /va-insight-validate` - Validate VA insights
- `GET /risk-signals` - Get consolidated risk signals
- `POST /confirm-generate-problem-statements` - Generate problem statements

**Data Flow:**
```
Engagement (Confirmed)
  ↓
Analysis Job (BE/VA) → Running → Completed
  ↓
BE Insights / VA Insights
  ↓
User Validation (Relevant/Not Relevant)
  ↓
Consolidated Risk Signals
  ↓
Problem Statements (Generated)
```

### 6.3 Screen 3-5: Problem Statements → Risk Universe → Audit Plan

**Screen 3: Problem Statements**
- System-generated from validated insights
- User review: Accept/Reject with priority overrides
- Process and impact mappings

**Screen 4: IA Risk Universe**
- Process/sub-process universe from templates
- System recommendations with override capability
- Scope decisions: `final_in_scope` boolean

**Screen 5: Audit Plan**
- Audit areas with frequency, timing, team assignment
- Process/sub-process mappings to audit areas
- Plan status: Draft → Sent → Approved → Locked

---

## 7. Key Features

### 7.1 Data Integrity

**Unique Constraints:**
- `regulatory_master.company_id` - One regulatory record per company
- `company_industry_size_master.company_id` - One industry profile per company
- `engagement.engagement_code` - Unique engagement codes
- `be_insight_validation.be_insight_id` - One validation per insight
- `va_insight_validation.va_insight_id` - One validation per insight

**Foreign Key Relationships:**
- All child tables reference parent via `company_id`, `engagement_id`, etc.
- Master tables provide referential integrity

### 7.2 Replace Pattern

**Replace Operations:**
- `tax-registration-replace`: Deletes all existing, inserts new list
- `manufacturing-replace`: Deletes all existing, inserts new list

**Rationale**: Simplifies UI state management (replace entire list vs. diff updates)

### 7.3 Upsert Pattern

**Upsert Operations:**
- `regulatory-upsert`: Update if exists, create if not
- `industry-size-upsert`: Update if exists, create if not

**Implementation:**
```python
record = db.query(Model).filter(...).first()
if record:
    # Update fields
else:
    # Create new
```

### 7.4 Temporal Data

**Versioning:**
- `country_master`: `st_dt`/`e_dt` for country changes over time
- `engagement_context`: `st_dt`/`e_dt` for context versioning

**Query Pattern:**
```python
.filter(
    Model.st_dt <= func.now(),
    Model.e_dt > func.now(),
    Model.is_active.is_(True)
)
```

---

## 8. Error Handling

### 8.1 HTTP Exceptions

**Standard Responses:**
- `400 Bad Request`: Invalid input (Pydantic validation)
- `401 Unauthorized`: Missing/invalid authentication
- `403 Forbidden`: RBAC permission denied
- `404 Not Found`: Resource not found (e.g., company_id)
- `409 Conflict`: Duplicate data (e.g., same legal_name + CIN)
- `503 Service Unavailable`: Auth/RBAC service errors

### 8.2 Validation

**Pydantic Validation:**
- Request schemas validate types, required fields, patterns
- Example: `listed_status` must match `^(Listed|Unlisted)$`

**Business Logic Validation:**
- Duplicate checks before creation
- Existence checks before updates
- Status transition validation (future enhancement)

---

## 9. Dependencies

### 9.1 Core Dependencies

```txt
fastapi==0.115.0          # Web framework
uvicorn[standard]==0.30.6 # ASGI server
pydantic==2.9.2           # Data validation
sqlalchemy==2.0.46        # ORM
pymysql==1.1.2            # MySQL driver
requests==2.32.5          # HTTP client (for Auth MS)
jwt==1.4.0                # JWT handling
python-dotenv==1.2.1      # Environment variables
```

### 9.2 External Services

**Auth Microservice:**
- Base URL: `AUTH_BASE_URL` env var
- Endpoints:
  - `POST /verify` - Verify user token
  - `POST /internal/service-token` - Get service token
  - `GET /.well-known/jwks.json` - JWKS for service token verification

**RBAC Service:**
- Service name: `RBAC` (from `RBAC_SERVICE_NAME` env var)
- Endpoint: `POST /authz/direct/check`
- Payload: `{userId, projectId, activity, requiredRoles?}`

---

## 10. Configuration

### 10.1 Environment Variables

**Database:**
- `DATABASE_HOST`
- `DATABASE_USER`
- `DATABASE_PASSWORD`
- `DATABASE_NAME`
- `DATABASE_PORT`

**Authentication:**
- `AUTH_BASE_URL` - Auth microservice URL
- `SERVICE_ID` - This service's identifier
- `SERVICE_SECRET` - Service secret for token generation
- `SERVICE_JWKS_URL` - JWKS endpoint for service token verification
- `SERVICE_JWT_ISSUER` - JWT issuer (default: `auth-service`)
- `SERVICE_JWT_AUDIENCE` - JWT audience (default: `itmtb-internal`)

**RBAC:**
- `RBAC_SERVICE_NAME` - RBAC service identifier (default: `RBAC`)
- `RBAC_TIMEOUT` - RBAC call timeout in seconds (default: `5`)

**Environment:**
- `RUNNING_ENV` - `dev`/`test`/`prod` (default: `dev`)

---

## 11. Code Quality & Patterns

### 11.1 Type Hints

**Extensive Use:**
- Function parameters and returns
- SQLAlchemy `Mapped[]` types
- Pydantic models with type annotations

**Example:**
```python
def get_entity_types(db: Session = Depends(get_db)) -> list[dict]:
    ...
```

### 11.2 Dependency Injection

**FastAPI Dependencies:**
- `get_db()` - Database session
- `get_current_user()` - User authentication
- `require(activity)` - RBAC permission check

**Router-Level:**
```python
router = APIRouter(dependencies=[Depends(get_current_user)])
```

### 11.3 Query Patterns

**Filtering:**
```python
query = db.query(Model)
if filter_value:
    query = query.filter(Model.field == filter_value)
rows = query.order_by(Model.id).all()
```

**Joins:**
```python
db.query(CompanyMaster, RegulatoryMaster)
  .outerjoin(RegulatoryMaster, ...)
  .filter(...)
```

### 11.4 Error Patterns

**HTTPException:**
```python
if not company:
    raise HTTPException(status_code=404, detail="Company not found")
```

**Conflict Detection:**
```python
if duplicate:
    raise HTTPException(status_code=409, detail="Duplicate exists")
```

---

## 12. Known Limitations & Future Enhancements

### 12.1 Current Limitations

1. **Authentication**: `get_current_user()` returns placeholder `{"user_id": "demo-user"}`
   - **Fix**: Integrate with `AuthMiddleware` or `AuthClient.verify_user_token()`

2. **Missing Endpoints**: Screen 2-5 endpoints are documented but not implemented
   - **Status**: Only Screen 1 (Company Master) is implemented

3. **No Pagination**: List endpoints return all records
   - **Enhancement**: Add pagination with `limit`/`offset` or cursor-based

4. **No Soft Delete API**: `is_active` flag exists but no endpoints to toggle
   - **Enhancement**: Add `DELETE /company-master/{id}` (soft delete)

5. **No Audit Logging**: No tracking of who changed what and when
   - **Enhancement**: Add audit log table or integrate with logging service

6. **No Caching**: Master data fetched on every request
   - **Enhancement**: Add Redis caching for master data

### 12.2 Recommended Enhancements

1. **Pagination**: Add to all list endpoints
2. **Filtering**: Enhanced search with multiple criteria
3. **Sorting**: Allow `order_by` parameter
4. **Bulk Operations**: Batch create/update endpoints
5. **Export**: CSV/Excel export for company lists
6. **Validation**: Business rule validation (e.g., status transitions)
7. **Event Sourcing**: Track all changes for audit trail
8. **Caching**: Redis for master data and frequently accessed records
9. **Rate Limiting**: Prevent abuse of endpoints
10. **API Versioning**: `/v1/` prefix for future compatibility

---

## 13. Testing Considerations

### 13.1 Unit Tests

**Recommended Coverage:**
- Pydantic schema validation
- Business logic functions (duplicate checks, validations)
- Database query functions

### 13.2 Integration Tests

**Test Scenarios:**
- Full company creation workflow
- Duplicate detection
- Upsert operations
- Replace operations
- Authentication/authorization flows

### 13.3 Test Database

**Setup:**
- Use separate test database
- Seed with test data
- Cleanup after tests

---

## 14. Deployment Considerations

### 14.1 Database Migrations

**Current State:**
- DDL in `ddl.sql` for manual execution
- **Recommendation**: Use Alembic for versioned migrations

### 14.2 Environment Configuration

**Production:**
- Use secrets manager (AWS Secrets Manager, Vault, etc.)
- Secure credential storage
- Environment-specific configs

### 14.3 Monitoring

**Recommended:**
- Application logs (structured logging)
- Database query performance
- API response times
- Error rates
- Authentication failures

### 14.4 Scaling

**Considerations:**
- Database connection pooling (already configured)
- Read replicas for master data queries
- Caching layer (Redis)
- Load balancing for API instances

---

## 15. Security Considerations

### 15.1 Current Security

✅ **Implemented:**
- JWT-based authentication
- Service-to-service authentication
- RBAC integration (via guard)
- SQL injection protection (SQLAlchemy parameterized queries)
- Input validation (Pydantic)

### 15.2 Recommendations

**Additional Security:**
- HTTPS enforcement
- CORS configuration
- Rate limiting
- Input sanitization
- SQL injection prevention (already via ORM)
- XSS prevention (API-only, but validate inputs)
- Audit logging for sensitive operations
- Encryption at rest for sensitive data

---

## 16. Summary

The **Internal Audit - BE** codebase is a well-structured FastAPI microservice with:

✅ **Strengths:**
- Clean architecture with separation of concerns
- Comprehensive database schema
- Type-safe code with Pydantic and SQLAlchemy
- Authentication/authorization framework in place
- Temporal data support for versioning
- Soft delete pattern for data retention

⚠️ **Areas for Improvement:**
- Complete authentication integration (currently placeholder)
- Implement remaining endpoints (Screens 2-5)
- Add pagination and filtering
- Implement audit logging
- Add comprehensive error handling
- Database migration tooling (Alembic)

The codebase follows modern Python best practices and is well-positioned for extension and maintenance.

