# Internal Audit BE API (Screen 1)

## Setup (Python 3.12 + venv)
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run
```powershell
uvicorn app.main:app --reload
```

## Auth
All Screen 1 endpoints are protected. Send `Authorization: Bearer <token>` header in requests.