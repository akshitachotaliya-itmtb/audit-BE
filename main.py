from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

from app.api import company, master
from app.auth.auth_middleware import AuthMiddleware

app = FastAPI(
    title="Internal Audit BE API",
    version="0.1.0",
)

# Add authentication middleware
# This validates Authorization: Bearer <token> or X-Service-Token headers
# and sets request.state.user_identity or request.state.service_identity
app.add_middleware(AuthMiddleware)

app.include_router(company.router, prefix="/api")
app.include_router(master.router , prefix="/api")


@app.get("/")
def root():
    return {"status": "ok", "service": "internal-audit-be"}
