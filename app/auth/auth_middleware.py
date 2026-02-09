# auth_middleware.py

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from dotenv import load_dotenv
load_dotenv()

from itmtb_auth_sdk import (
    AuthClient,
    AuthUnauthorizedError,
    AuthServiceError,
)

class AuthMiddleware(BaseHTTPMiddleware):
    """
    ITMTB Global Authentication Middleware for Microservices

    Responsibilities:
    -----------------
    1. Validate X-Service-Token (internal microservice calls) via local JWT verification
    2. Validate Authorization: Bearer <JWT> (external user calls) via Auth MS
    3. Attach validated identities to:
         request.state.service_identity
         request.state.user_identity
    4. Enforce: at least one identity MUST be present.
       (No anonymous access allowed.)
    """

    def __init__(self, app):
        super().__init__(app)
        self.auth_client = AuthClient()  # single instance, uses JWKS cache

    async def dispatch(self, request: Request, call_next):
        """
        Main entry point for every incoming request.
        """

        # allow unauthenticated health + docs endpoints - for checking headers
        # to be disabled
        #if request.url.path in ("/me", "/docs", "/openapi.json"):
        #    return await call_next(request)

        request.state.user_identity = None
        request.state.service_identity = None

        # -------------------------------
        # 1. Internal service auth (JWKS local verify)
        # -------------------------------
        svc_token = request.headers.get("X-Service-Token")
        if svc_token:
            try:
                service_identity = self.auth_client.verify_service_token(svc_token)
                request.state.service_identity = service_identity
            except AuthUnauthorizedError:
                raise HTTPException(status_code=401, detail="Invalid service token")
            except AuthServiceError:
                raise HTTPException(status_code=503, detail="Auth system error")

        # -------------------------------
        # 2. End-user JWT verification (via Auth MS)
        # -------------------------------
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            user_token = auth_header.split(" ", 1)[1]
            try:
                user_identity = self.auth_client.verify_user_token(user_token)
                request.state.user_identity = user_identity
            except AuthUnauthorizedError as e:
                print(f"❌ [AUTH_MIDDLEWARE] User token verification failed: {str(e)}")
                raise HTTPException(status_code=401, detail=f"Invalid user token: {str(e)}")
            except AuthServiceError as e:
                print(f"❌ [AUTH_MIDDLEWARE] Auth service error: {str(e)}")
                raise HTTPException(status_code=503, detail=f"Auth system error: {str(e)}")

        # -------------------------------
        # 3. Enforce at least one identity
        # -------------------------------
        if not request.state.user_identity and not request.state.service_identity:
            raise HTTPException(status_code=401, detail="Missing authentication")

        return await call_next(request)

