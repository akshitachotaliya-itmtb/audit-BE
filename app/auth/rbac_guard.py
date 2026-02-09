# shared/rbac_guard.py
import os
import json
from typing import Optional, List
from fastapi import Request, HTTPException

from itmtb_auth_sdk import AuthClient, AuthUnauthorizedError, AuthServiceError

RBAC_SERVICE_NAME = os.getenv("RBAC_SERVICE_NAME", "RBAC")
RBAC_TIMEOUT = int(os.getenv("RBAC_TIMEOUT", "5"))


def _get_auth_client() -> AuthClient:
    # Lazy init: avoids import-time env capture
    return AuthClient()


def _get_project_from_header_or_query(request: Request) -> Optional[str]:
    # Backward compatible sources
    return (
        request.headers.get("X-Tenant-Id")
        or request.query_params.get("tenant_id")
        or request.query_params.get("project_id")
    )


def _get_project_from_json(payload) -> Optional[str]:
    # Accept:
    #   {"tenant_id": "..."} or {"project_id": "..."}
    #   {"context": {"tenant_id": "..."}} or {"context": {"project_id": "..."}}
    if not isinstance(payload, dict):
        return None

    pid = payload.get("tenant_id") or payload.get("project_id")
    if pid:
        return str(pid)

    ctx = payload.get("context")
    if isinstance(ctx, dict):
        pid = ctx.get("tenant_id") or ctx.get("project_id")
        if pid:
            return str(pid)

    return None


async def _extract_project_id(request: Request) -> Optional[str]:
    # 1) FIRST: Try to get tenant_id from token (PREFERRED - matches Auth MS)
    tenant_id_from_token = _extract_tenant_id_from_state(request)
    if tenant_id_from_token:
        return tenant_id_from_token
    
    # 2) FALLBACK: header/query (for backward compatibility)
    project_id = _get_project_from_header_or_query(request)
    if project_id:
        return project_id

    # 3) FALLBACK: JSON body
    content_type = (request.headers.get("content-type") or "").lower()
    if "application/json" not in content_type:
        return None

    try:
        raw = await request.body()
        if not raw:
            return None
        payload = json.loads(raw)
    except Exception:
        return None

    return _get_project_from_json(payload)


def _extract_user_id_from_state(request: Request) -> Optional[str]:
    ui = getattr(request.state, "user_identity", None)
    if not isinstance(ui, dict):
        return None

    # Support multiple common keys - check nested user object first
    user_obj = ui.get("user", {})
    if isinstance(user_obj, dict):
        return (
            user_obj.get("u_id")
            or user_obj.get("user_id")
            or user_obj.get("auth_user_id")
            or user_obj.get("uid")
            or user_obj.get("sub")
        )
    
    # Fallback to top-level keys
    return (
        ui.get("u_id")
        or ui.get("user_id")
        or ui.get("auth_user_id")
        or ui.get("uid")
        or ui.get("sub")
    )


def _extract_tenant_id_from_state(request: Request) -> Optional[str]:
    """Extract tenant_id from request.state.user_identity (token)"""
    ui = getattr(request.state, "user_identity", None)
    if not isinstance(ui, dict):
        return None
    
    # Check nested user object first
    user_obj = ui.get("user", {})
    if isinstance(user_obj, dict):
        tenant_id = user_obj.get("tenant_id")
        if tenant_id is not None:
            return str(tenant_id)
    
    # Fallback to top-level
    tenant_id = ui.get("tenant_id")
    if tenant_id is not None:
        return str(tenant_id)
    
    return None


def require(activity: str, required_roles: Optional[List[str]] = None):
    """
    Enforces RBAC via RBAC service endpoint: POST /authz/direct/check

    RBAC expects JSON:
      {
        "userId": "...",
        "projectId": "...",
        "activity": "...",
        "requiredRoles": ["ADMIN", ...]   # optional
      }

    required_roles:
      - leave None for normal RBAC lookup by activity
      - pass ["ADMIN"] to force role requirement in RBAC service (if it supports it)
    """

    async def dep(request: Request):
        print(f"\n=== [RBAC GUARD] Starting permission check for activity: '{activity}' ===")
        
        # 1) user token
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            print("=== [RBAC GUARD] Missing Authorization Bearer token ===")
            raise HTTPException(status_code=401, detail="Missing Authorization Bearer token")

        user_jwt = auth_header.split(" ", 1)[1].strip()
        if not user_jwt:
            print("=== [RBAC GUARD] Missing user token ===")
            raise HTTPException(status_code=401, detail="Missing user token")
        
        print(f"=== [RBAC GUARD] User token found (length: {len(user_jwt)}) ===")

        # 2) project/tenant context - FROM TOKEN FIRST (preferred), then fallback to query/header/body
        project_id = await _extract_project_id(request)
        if not project_id:
            print("=== [RBAC GUARD] Missing project_id/tenant_id ===")
            print(f"=== [RBAC GUARD] Checked: token, query params, headers (X-Tenant-Id), JSON body ===")
            raise HTTPException(
                status_code=400,
                detail="Missing project_id/tenant_id (token, header/query or JSON body tenant_id|project_id)",
            )
        
        # Check if it came from token or fallback
        tenant_id_from_token = _extract_tenant_id_from_state(request)
        if tenant_id_from_token and tenant_id_from_token == project_id:
            print(f"=== [RBAC GUARD] Project ID extracted: '{project_id}' (from token) ===")
        else:
            print(f"=== [RBAC GUARD] Project ID extracted: '{project_id}' (from query/header/body - fallback) ===")

        auth_client = _get_auth_client()

        # 3) userId: from middleware state if present, else verify with Auth
        # USER_ID COMES FROM TOKEN (via AuthMiddleware)
        user_id = _extract_user_id_from_state(request)
        if not user_id:
            print("=== [RBAC GUARD] User ID not in middleware state, verifying token with Auth MS ===")
            try:
                identity = auth_client.verify_user_token(user_jwt)
            except AuthUnauthorizedError as e:
                print(f"=== [RBAC GUARD] Auth verification failed: {str(e)} ===")
                raise HTTPException(status_code=401, detail=str(e))
            except AuthServiceError as e:
                print(f"=== [RBAC GUARD] Auth service error: {str(e)} ===")
                raise HTTPException(status_code=503, detail=str(e))
            except Exception as e:
                print(f"=== [RBAC GUARD] Auth verification exception: {str(e)} ===")
                raise HTTPException(status_code=503, detail="Auth verification failed")

            # Extract user_id from identity response
            user_obj = identity.get("user", {})
            if isinstance(user_obj, dict):
                user_id = (
                    user_obj.get("u_id")
                    or user_obj.get("user_id")
                    or user_obj.get("auth_user_id")
                    or user_obj.get("uid")
                    or user_obj.get("sub")
                )
            else:
                # Fallback to top-level
                user_id = (
                    identity.get("u_id")
                    or identity.get("user_id")
                    or identity.get("auth_user_id")
                    or identity.get("uid")
                    or identity.get("sub")
                )

        if not user_id:
            print("=== [RBAC GUARD] Unable to resolve userId from token ===")
            raise HTTPException(status_code=401, detail="Unable to resolve userId from token")
        
        print(f"=== [RBAC GUARD] User ID extracted: '{user_id}' (from token) ===")

        # 4) RBAC call with expected payload
        payload = {
            "userId": str(user_id),
            "projectId": str(project_id),
            "activity": activity,
        }
        if required_roles is not None:
            payload["requiredRoles"] = required_roles

        print(f"=== [RBAC GUARD] Calling RBAC service: POST /authz/direct/check ===")
        print(f"=== [RBAC GUARD] Payload: {payload} ===")
        
        try:
            resp = auth_client.call_service(
                service_name=RBAC_SERVICE_NAME,
                path="/authz/direct/check",
                method="POST",
                user_token=user_jwt,      # becomes X-User-Token for RBAC service
                json=payload,
                timeout=RBAC_TIMEOUT,
            )

            print(f"=== [RBAC GUARD] RBAC Response Status: {resp.status_code} ===")
            
            if resp.status_code != 200:
                print(f"=== [RBAC GUARD] RBAC returned non-200 status: {resp.status_code} ===")
                print(f"=== [RBAC GUARD] Response: {resp.text[:200]} ===")
                raise HTTPException(status_code=403, detail=f"Forbidden: {activity}")

            try:
                data = resp.json()
            except Exception as e:
                print(f"=== [RBAC GUARD] Failed to parse RBAC response JSON: {str(e)} ===")
                raise HTTPException(status_code=403, detail=f"Forbidden: {activity}")

            print(f"=== [RBAC GUARD] RBAC Response Data: {data} ===")
            
            is_allowed = bool(data.get("data", {}).get("allowed", False))
            print(f"=== [RBAC GUARD] Permission check result: {'ALLOWED' if is_allowed else 'DENIED'} ===")
            
            if not is_allowed:
                print(f"=== [RBAC GUARD] Permission denied for user '{user_id}' to perform '{activity}' in project '{project_id}' ===")
                raise HTTPException(status_code=403, detail=f"Forbidden: {activity}")
            
            print(f"=== [RBAC GUARD] Permission granted! User '{user_id}' can perform '{activity}' in project '{project_id}' ===\n")
            
        except HTTPException:
            # Re-raise HTTP exceptions (403, etc.)
            raise
        except Exception as e:
            print(f"=== [RBAC GUARD] Error calling RBAC service: {str(e)} ===")
            print(f"=== [RBAC GUARD] Exception type: {type(e).__name__} ===")
            raise HTTPException(status_code=503, detail=f"RBAC service error: {str(e)}")

    dep.__rbac_activity__ = activity
    return dep

