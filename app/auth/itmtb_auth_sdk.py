"""
itmtb_auth_sdk.py

Central Auth client for all Python microservices.

Responsibilities:
- Get + cache service token (Auth MS).
- Verify user JWT via Auth MS.
- Verify service token via JWKS (local, fast).
- Provide helpers for cross-service calls with correct headers.
"""

import os
import time
from typing import Optional, Dict, Any

import requests
import jwt
from jwt import PyJWKClient, InvalidTokenError


JWKS_URL = os.getenv("SERVICE_JWKS_URL", "http://localhost:6501/auth/.well-known/jwks.json")
SERVICE_JWT_ISSUER = os.getenv("SERVICE_JWT_ISSUER", "auth-service")
SERVICE_JWT_AUDIENCE = os.getenv("SERVICE_JWT_AUDIENCE", "itmtb-internal")

import os
print("[AuthSDK LOADED FROM]", __file__)
print("[AuthSDK ENV SERVICE_ID]", os.getenv("SERVICE_ID"))
print("[AuthSDK ENV SERVICE_SECRET SET]", bool(os.getenv("SERVICE_SECRET")))


_jwks_cache = None
_jwks_last_fetched = 0
JWKS_CACHE_TTL = 300  # 5 minutes

# =========================
# Exceptions
# =========================

class AuthConfigError(Exception):
    """Missing or invalid configuration for Auth client."""


class AuthUnauthorizedError(Exception):
    """Auth or Auth-related call returned 401/403."""


class AuthServiceError(Exception):
    """Auth microservice itself failed (5xx or malformed response)."""


class ServiceCallError(Exception):
    """Generic error from cross-service calls."""


# =========================
# Helper: service URL resolution
# =========================

def resolve_service_url(service_name: str) -> str:
    """
    Resolve base URL for a given service name.
    For now, read from env: <SERVICE_NAME>_BASE_URL, e.g. UMS_BASE_URL.

    You can replace this later with Consul / Nginx / internal DNS.
    """
    env_name = f"{service_name.upper()}_BASE_URL"
    base_url = os.getenv(env_name)
    if not base_url:
        raise AuthConfigError(f"Missing env var: {env_name}")
    return base_url.rstrip("/")

# =========================
# Auth Client
# =========================

class AuthClient:
    """
    Central Auth client used by ALL microservices.

    - Talks to Auth MS (AUTH_BASE_URL)
    - Issues service tokens
    - Verifies user tokens
    - Verifies service tokens (for middleware)
    - Helps construct headers
    - Wraps cross-service HTTP calls
    """

    def __init__(
        self,
        auth_base_url: Optional[str] = None,
        service_id: Optional[str] = None,
        service_secret: Optional[str] = None,
        session: Optional[requests.Session] = None,
        service_token_ttl_seconds: int = 9 * 60,
    ):
        """
        auth_base_url: e.g. http://localhost:6501/auth
        service_id: e.g. svc_file
        service_secret: secret configured in service_accounts table
        session: optional requests.Session for connection reuse / mocking
        """
        self._jwks_client = None
        self._jwks_last_fetched = 0
        self._jwks_cache_ttl = 300  # seconds
        self.auth_base_url = (auth_base_url or os.getenv("AUTH_BASE_URL") or "").rstrip("/")
        self.service_id = os.getenv("SERVICE_ID") or service_id
        self.service_secret = os.getenv("SERVICE_SECRET") or service_secret
        self.session = session or requests.Session()
        self.service_token_ttl_seconds = service_token_ttl_seconds

        print(f'in auth sdk service id {os.getenv("SERVICE_ID")}')
        print(f"in auth secret {self.service_secret}")
        print(f"in auth service url service id {self.auth_base_url}")

        if not self.auth_base_url:
            raise AuthConfigError("AUTH_BASE_URL not set")
        if not self.service_id:
            raise AuthConfigError("SERVICE_ID not set")
        if not self.service_secret:
            raise AuthConfigError("SERVICE_SECRET not set")

        # service token cache
        self._service_token: Optional[str] = None
        self._service_token_expiry_ts: float = 0.0

    # ------------------------------------------------------
    # Internal HTTP helpers
    # ------------------------------------------------------

    def _auth_post(self, path: str, json: Optional[Dict[str, Any]] = None, timeout: int = 10) -> requests.Response:
        url = f"{self.auth_base_url}{path}"
        try:
            resp = self.session.post(url, json=json or {}, timeout=timeout)
        except requests.RequestException as e:
            raise AuthServiceError(f"Error calling Auth at {url}: {e}")
        return resp

    # ------------------------------------------------------
    # User Token Verification (for middleware or services)
    # ------------------------------------------------------

    def verify_user_token(self, user_token: str) -> Dict[str, Any]:
        """
        Verify user JWT via Auth MS.

        Returns identity JSON on success:
        {
          "user": {
            "u_id": "...",
            "auth_user_id": "...",
            "email": "...",
            "tenant_id": ...,
            "is_active": true
          }
        }
        """
        if not user_token:
            raise AuthUnauthorizedError("User token missing")

        resp = self._auth_post("/verify", {"token": user_token})
        if resp.status_code == 200:
            try:
                return resp.json()
            except ValueError:
                raise AuthServiceError("Auth /verify returned non-JSON")
        elif resp.status_code in (400, 401, 403):
            raise AuthUnauthorizedError(f"User token invalid: {resp.status_code} {resp.text}")
        else:
            raise AuthServiceError(f"Auth /verify failed: {resp.status_code} {resp.text}")

    # ------------------------------------------------------
    # Service Token Handling
    # ------------------------------------------------------

    def _fetch_new_service_token(self) -> str:
        body = {
            "service_id": self.service_id,
            "service_secret": self.service_secret,
        }
        resp = self._auth_post("/internal/service-token", body)
        if resp.status_code != 200:
            raise AuthUnauthorizedError(
                f"Auth /internal/service-token failed: {resp.status_code} {resp.text}"
            )

        try:
            data = resp.json()
        except ValueError:
            raise AuthServiceError("Auth /internal/service-token returned non-JSON")

        token = data.get("token")
        if not token:
            raise AuthServiceError("Auth /internal/service-token response missing 'token'")

        # naive TTL; we assume token expiry ~10min, so cache for service_token_ttl_seconds
        self._service_token = token
        self._service_token_expiry_ts = time.time() + self.service_token_ttl_seconds
        return token

    def get_service_token(self, force_refresh: bool = False) -> str:
        """
        Return a valid service token, refreshing if needed.
        """
        now = time.time()
        if (
            not force_refresh
            and self._service_token
            and now < self._service_token_expiry_ts
        ):
            return self._service_token

        return self._fetch_new_service_token()

    # ------------------------------------------------------
    # Service Token Verification (for inbound middleware)
    # ------------------------------------------------------

    def _get_jwks_client(self) -> PyJWKClient:
        now = time.time()

        if (
            self._jwks_client is None
            or now - self._jwks_last_fetched > self._jwks_cache_ttl
        ):
            jwks_url = os.getenv(
                "SERVICE_JWKS_URL",
                f"{self.auth_base_url}/.well-known/jwks.json"
            )

            try:
                self._jwks_client = PyJWKClient(jwks_url)
                self._jwks_last_fetched = now
            except Exception as e:
                raise AuthServiceError(f"Failed to load JWKS: {e}")

        return self._jwks_client


    def verify_service_token(self, token: str) -> Dict[str, Any]:
        if not token:
            raise AuthUnauthorizedError("Missing service token")

        try:
            jwks_client = self._get_jwks_client()
            signing_key = jwks_client.get_signing_key_from_jwt(token).key

            decoded = jwt.decode(
                token,
                key=signing_key,
                algorithms=["RS256"],
                audience=os.getenv("SERVICE_JWT_AUDIENCE", "itmtb-internal"),
                issuer=os.getenv("SERVICE_JWT_ISSUER", "auth-service"),
            )

            if decoded.get("type") != "service":
                raise AuthUnauthorizedError("Invalid token type")

            service_id = decoded.get("sub")
            if not service_id:
                raise AuthUnauthorizedError("Token missing subject")

            scopes = decoded.get("scopes", [])
            if not isinstance(scopes, list):
                raise AuthUnauthorizedError("Invalid scopes format")

            return {
                "service_id": service_id,
                "scopes": scopes,
            }

        except jwt.ExpiredSignatureError:
            raise AuthUnauthorizedError("Service token expired")
        except jwt.InvalidTokenError as e:
            raise AuthUnauthorizedError(f"Invalid service token: {e}")
        except AuthUnauthorizedError:
            raise
        except Exception as e:
            raise AuthServiceError(f"Service token verification failed: {e}")

    # ------------------------------------------------------
    # Header helpers
    # ------------------------------------------------------

    def build_service_headers(self, user_token: Optional[str] = None) -> Dict[str, str]:
        """
        Build headers for outgoing cross-service calls:
        - X-Service-Token: <this service's token>
        - X-User-Token: <end-user token> (optional)
        """
        svc_token = self.get_service_token()
        # Do not print service token - contains sensitive information
        headers = {
            "X-Service-Token": svc_token,
        }
        if user_token:
            # user_token may be "Bearer x" or just "x"
            if user_token.startswith("Bearer "):
                headers["X-User-Token"] = user_token.split(" ", 1)[1]
            else:
                headers["X-User-Token"] = user_token
        return headers

    # ------------------------------------------------------
    # Cross-service call wrapper
    # ------------------------------------------------------

    def call_service(
        self,
        service_name: str,
        path: str,
        method: str = "GET",
        user_token: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 10,
        **kwargs,
    ) -> requests.Response:
        """
        Call another microservice with:
        - X-Service-Token (this service)
        - X-User-Token (optional)

        Automatically retries once on 401 with a forced service-token refresh.
        """
        base_url = resolve_service_url(service_name)
        url = f"{base_url}{path}"

        # merge headers: caller-supplied + auth headers
        auth_headers = self.build_service_headers(user_token=user_token)
        final_headers = {**(headers or {}), **auth_headers}
        # Do not print final_headers - contains sensitive token information

        try:
            resp = self.session.request(method, url, headers=final_headers, timeout=timeout, **kwargs)
        except requests.RequestException as e:
            raise ServiceCallError(f"Error calling service '{service_name}' at {url}: {e}")

        # if 401 from target, refresh service token once and retry
        if resp.status_code == 401:
            # force refresh
            self.get_service_token(force_refresh=True)
            auth_headers = self.build_service_headers(user_token=user_token)
            final_headers = {**(headers or {}), **auth_headers}

            try:
                resp = self.session.request(method, url, headers=final_headers, timeout=timeout, **kwargs)
            except requests.RequestException as e:
                raise ServiceCallError(f"Error calling service '{service_name}' at {url} after refresh: {e}")

        return resp

