from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

from app.api import company, master

app = FastAPI(
    title="Internal Audit BE API",
    version="0.1.0",
)


app.include_router(company.router, prefix="/api")
app.include_router(master.router , prefix="/api")


@app.get("/")
def root():
    return {"status": "ok", "service": "internal-audit-be"}
