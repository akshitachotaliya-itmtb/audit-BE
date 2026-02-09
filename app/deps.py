from fastapi import Request, HTTPException, status
from typing import Optional, Tuple


def get_current_user(request: Request) -> dict:
    """
    Extract user identity from request.state (set by AuthMiddleware).
    
    This dependency expects AuthMiddleware to have already validated the token
    and set request.state.user_identity.
    
    Returns:
        dict: User identity with keys like:
            - user_id / u_id / auth_user_id / sub
            - tenant_id
            - email
            - etc.
    
    Raises:
        HTTPException: 401 if no user identity found
    """
    user_identity = getattr(request.state, "user_identity", None)
    
    if not user_identity:
        # Check if service identity exists (for internal service calls)
        service_identity = getattr(request.state, "service_identity", None)
        if service_identity:
            # For service-to-service calls, return service identity
            return {
                "user_id": service_identity.get("service_id", "system"),
                "is_service": True,
                "service_id": service_identity.get("service_id"),
                "scopes": service_identity.get("scopes", []),
            }
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication. Authorization header required.",
        )
    
    # Extract user_id from various possible keys
    user_id = (
        user_identity.get("u_id")
        or user_identity.get("user_id")
        or user_identity.get("auth_user_id")
        or user_identity.get("uid")
        or user_identity.get("sub")
    )
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to resolve user ID from token",
        )
    
    return {
        "user_id": str(user_id),
        "tenant_id": user_identity.get("tenant_id"),
        "email": user_identity.get("email"),
        "is_service": False,
        **user_identity,  # Include all other identity fields
    }


def extract_user_identity(request: Request) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract user_id and tenant_id from request.state.user_identity.
    
    This is a reusable helper function that handles both nested and flat identity structures.
    Use this in endpoints to get user_id and tenant_id without repeating the extraction logic.
    
    Args:
        request: FastAPI Request object (must have user_identity in request.state)
    
    Returns:
        Tuple[Optional[str], Optional[str]]: (actor_user_id, tenant_id)
            - actor_user_id: User ID extracted from token (u_id, user_id, auth_user_id, sub, etc.)
            - tenant_id: Tenant ID from token
    
    Example:
        ```python
        actor_user_id, tenant_id = extract_user_identity(request)
        if not actor_user_id:
            raise HTTPException(status_code=401, detail="User authentication required")
        ```
    """
    user_identity = getattr(request.state, "user_identity", None)
    
    if not user_identity:
        return None, None
    
    # Support nested user object (from Auth MS response) or flat structure
    user_obj = user_identity.get("user", {})
    
    if isinstance(user_obj, dict) and user_obj:
        # Nested structure: {"user": {"u_id": "...", "tenant_id": "..."}}
        actor_user_id = (
            user_obj.get("u_id")
            or user_obj.get("user_id")
            or user_obj.get("auth_user_id")
            or user_obj.get("uid")
            or user_obj.get("sub")
        )
        tenant_id = user_obj.get("tenant_id") or user_identity.get("tenant_id")
    else:
        # Flat structure: {"u_id": "...", "tenant_id": "..."}
        actor_user_id = (
            user_identity.get("u_id")
            or user_identity.get("user_id")
            or user_identity.get("auth_user_id")
            or user_identity.get("uid")
            or user_identity.get("sub")
        )
        tenant_id = user_identity.get("tenant_id")
    
    # Convert to string if not None
    if actor_user_id:
        actor_user_id = str(actor_user_id)
    if tenant_id:
        tenant_id = str(tenant_id)
    
    return actor_user_id, tenant_id