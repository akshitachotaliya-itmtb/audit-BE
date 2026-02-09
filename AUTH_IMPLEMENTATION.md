# Authorization Implementation - Internal Audit BE

## Overview
This document describes the authorization implementation in Internal Audit BE, based on the pattern used in `itmtb_ms_user`.

## Architecture

### 1. **AuthMiddleware** (`app/auth/auth_middleware.py`)
- **Purpose**: Validates incoming requests and extracts user/service identities
- **Responsibilities**:
  - Validates `Authorization: Bearer <JWT>` tokens via Auth MS
  - Validates `X-Service-Token` headers for service-to-service calls
  - Sets `request.state.user_identity` or `request.state.service_identity`
  - Enforces authentication (no anonymous access)

### 2. **get_current_user Dependency** (`app/deps.py`)
- **Purpose**: Extracts user identity from `request.state` (set by middleware)
- **Returns**: Dictionary with:
  - `user_id`: Extracted from token (u_id, user_id, auth_user_id, sub, etc.)
  - `tenant_id`: From token
  - `email`: From token
  - `is_service`: Boolean indicating if this is a service call
  - All other identity fields from token

### 3. **Router-Level Protection** (`app/api/company.py`)
- All endpoints in `company.py` router are protected via:
  ```python
  router = APIRouter(dependencies=[Depends(get_current_user)])
  ```
- This ensures every endpoint requires authentication

## Flow

```
1. Request arrives → AuthMiddleware
   ↓
2. AuthMiddleware validates token:
   - Authorization: Bearer <token> → verify_user_token() → request.state.user_identity
   - X-Service-Token: <token> → verify_service_token() → request.state.service_identity
   ↓
3. If no identity found → HTTP 401
   ↓
4. Request proceeds to endpoint
   ↓
5. get_current_user dependency extracts identity from request.state
   ↓
6. Endpoint receives current_user dict with user_id, tenant_id, etc.
```

## Changes Made

### 1. `app/deps.py`
- **Before**: Simple header check, returned `{"user_id": "demo-user"}`
- **After**: Extracts identity from `request.state.user_identity` (set by middleware)
- Supports both user tokens and service tokens

### 2. `main.py`
- **Added**: `app.add_middleware(AuthMiddleware)`
- This enables authentication for all requests

### 3. `app/api/company.py`
- **Updated**: `create_company_master` to use `current_user.get("user_id")` instead of hardcoded "demo-user"
- **Added**: `Request` parameter to access request state if needed

## Environment Variables Required

The AuthMiddleware and AuthClient require these environment variables:

```bash
# Auth Service Configuration
AUTH_BASE_URL=http://localhost:6501/auth  # Base URL of Auth microservice
SERVICE_ID=internal-audit-be              # This service's ID
SERVICE_SECRET=<secret>                   # This service's secret (from Auth MS)

# Optional (for service token verification)
SERVICE_JWKS_URL=http://localhost:6501/auth/.well-known/jwks.json
SERVICE_JWT_ISSUER=auth-service
SERVICE_JWT_AUDIENCE=itmtb-internal
```

## Usage in Endpoints

### Basic Authentication (Current Implementation)
```python
@router.post("/company-create")
def create_company_master(
    payload: CompanyCreateRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # ← Gets user identity
):
    user_id = current_user.get("user_id")
    tenant_id = current_user.get("tenant_id")
    # ... use user_id for created_by, etc.
```

### Optional: RBAC (Role-Based Access Control)
If you need to add RBAC checks (like `itmtb_ms_user` does), you can use:

```python
from app.auth.rbac_guard import require

@router.post("/company-create", dependencies=[Depends(require("company.create"))])
def create_company_master(...):
    # This endpoint now requires "company.create" permission
    # RBAC service will be called to verify permission
```

## Testing

### With User Token
```bash
curl -X GET "http://localhost:8000/api/company-search?q=test" \
  -H "Authorization: Bearer <user_jwt_token>"
```

### With Service Token
```bash
curl -X GET "http://localhost:8000/api/company-search?q=test" \
  -H "X-Service-Token: <service_jwt_token>"
```

### Without Token (Should Fail)
```bash
curl -X GET "http://localhost:8000/api/company-search?q=test"
# Expected: HTTP 401 "Missing authentication"
```

## Differences from itmtb_ms_user

1. **Simpler RBAC**: `itmtb_ms_user` uses `require(activity)` for RBAC checks. Internal Audit BE currently only does authentication. RBAC can be added later if needed.

2. **Tenant/Project Context**: `itmtb_ms_user` extracts `project_id`/`tenant_id` from headers/query/body for RBAC calls. Internal Audit BE currently doesn't need this, but the pattern is available in `rbac_guard.py` if needed.

3. **Audit Logging**: `itmtb_ms_user` includes audit logging. This can be added to Internal Audit BE later.

## Next Steps (Optional Enhancements)

1. **Add RBAC**: Use `require(activity)` dependency for permission checks
2. **Add Audit Logging**: Log all company creation/modification actions
3. **Add Tenant Isolation**: Filter queries by `tenant_id` from token
4. **Add Error Logging**: Use error_log SDK for better error tracking

