# 🚀 Quick API Reference (Post-Fix)

## Base URL
```
http://localhost:8000
```

## Authentication
All endpoints require:
```
Authorization: Bearer <token>
```

---

## 📋 Screen 1: Company & Engagement APIs

### 1. Search Companies
```http
GET /api/company-search?q=apex
```

**Response:**
```json
[
  {
    "company_id": "550e8400-e29b-41d4-a716-446655440000",
    "legal_name": "Apex Manufacturing Pvt Ltd",
    "country_id": "660e8400-e29b-41d4-a716-446655440001",
    "cin": "L29304MH2010PLC201001",
    "sector": "770e8400-e29b-41d4-a716-446655440002"
  }
]
```

### 2. Get Company Details
```http
GET /api/company-master?company_id=550e8400-e29b-41d4-a716-446655440000
```

**Response:**
```json
{
  "company_id": "550e8400-e29b-41d4-a716-446655440000",
  "legal_name": "Apex Manufacturing Pvt Ltd",
  "display_name": "Apex Manufacturing",
  "entity_type_id": "aa0e8400-e29b-41d4-a716-446655440003",
  "country_id": "660e8400-e29b-41d4-a716-446655440001",
  "registered_address": "12 Industrial Estate, Pune, MH, India",
  "operational_hq_address": "Apex Towers, Pune, MH, India",
  "is_part_of_group": false,
  "parent_group_id": null,
  "status": "Draft"
}
```

### 3. Create Company
```http
POST /api/company-create
Content-Type: application/json

{
  "legal_name": "New Company Ltd",
  "display_name": "NewCo",
  "entity_type_id": "aa0e8400-e29b-41d4-a716-446655440003",
  "country_id": "660e8400-e29b-41d4-a716-446655440001",
  "registered_address": "123 Business Park, Mumbai",
  "operational_hq_address": "456 Corporate Center, Mumbai",
  "is_part_of_group": true,
  "parent_group_id": "bb0e8400-e29b-41d4-a716-446655440004",
  "cin": "U12345MH2020PLC123456"
}
```

**Response:**
```json
{
  "message": "Company created",
  "company_id": "new-uuid-here"
}
```

### 4. Upsert Regulatory Data
```http
POST /api/regulatory-upsert
Content-Type: application/json

{
  "company_id": "550e8400-e29b-41d4-a716-446655440000",
  "cin": "L29304MH2010PLC201001",
  "pan": "AAECA1234F",
  "lei": "5493001KJTIIGC8Y1R12",
  "listed_status": "Listed",
  "exchange_list": ["NSE", "BSE"],
  "ticker_symbol": "APEX"
}
```

### 5. Upsert Industry & Size Profile
```http
POST /api/industry-size-upsert
Content-Type: application/json

{
  "company_id": "550e8400-e29b-41d4-a716-446655440000",
  "industry_sector_id": "cc0e8400-e29b-41d4-a716-446655440005",
  "sub_industry_id": "dd0e8400-e29b-41d4-a716-446655440006",
  "industry_code_id": "ee0e8400-e29b-41d4-a716-446655440007",
  "annual_turnover_id": "ff0e8400-e29b-41d4-a716-446655440008",
  "employee_band_id": "110e8400-e29b-41d4-a716-446655440009",
  "manufacturing_plants_count": 3,
  "sez_eou_presence": true,
  "revenue_indicator_id": "220e8400-e29b-41d4-a716-44665544000a",
  "spend_indicator_id": "330e8400-e29b-41d4-a716-44665544000b"
}
```

### 6. Replace Tax Registrations
```http
POST /api/tax-registration-replace
Content-Type: application/json

{
  "company_id": "550e8400-e29b-41d4-a716-446655440000",
  "items": [
    {
      "tax_type": "GST",
      "tax_id": "27AAECA1234F1Z5",
      "country_id": "660e8400-e29b-41d4-a716-446655440001"
    },
    {
      "tax_type": "TAN",
      "tax_id": "ABCD12345E",
      "country_id": "660e8400-e29b-41d4-a716-446655440001"
    }
  ]
}
```

### 7. Replace Manufacturing Locations
```http
POST /api/manufacturing-replace
Content-Type: application/json

{
  "company_id": "550e8400-e29b-41d4-a716-446655440000",
  "items": [
    {
      "plant_name": "Pune Plant 1",
      "city": "Pune",
      "state": "Maharashtra",
      "country_id": "660e8400-e29b-41d4-a716-446655440001"
    },
    {
      "plant_name": "Chennai Plant",
      "city": "Chennai",
      "state": "Tamil Nadu",
      "country_id": "660e8400-e29b-41d4-a716-446655440001"
    }
  ]
}
```

### 8. Create Engagement
```http
POST /api/engagement-create
Content-Type: application/json

{
  "company_id": "550e8400-e29b-41d4-a716-446655440000",
  "engagement_name": "FY25 Internal Audit - Entity Level",
  "engagement_code": "APEX-FY25-001",
  "audit_type": "Full-scope IA",
  "reporting_currency": ["INR", "USD"],
  "audit_fy": "FY25"
}
```

**Response:**
```json
{
  "message": "Engagement created",
  "engagement_id": "440e8400-e29b-41d4-a716-44665544000c"
}
```

### 9. Save Engagement Context
```http
POST /api/engagement-context
Content-Type: application/json

{
  "engagement_id": "440e8400-e29b-41d4-a716-44665544000c",
  "context": {
    "theme": "Operational efficiency",
    "scope": "Entity-level controls",
    "exclusions": ["IT controls"],
    "prior_findings": 12,
    "notes": "Focus on working capital management"
  }
}
```

---

## 📋 Master Data APIs

### Get Entity Types
```http
GET /api/master/entity-types
```

**Response:**
```json
[
  {
    "entity_type_id": "aa0e8400-e29b-41d4-a716-446655440003",
    "name": "Company"
  },
  {
    "entity_type_id": "ab0e8400-e29b-41d4-a716-446655440003",
    "name": "LLP"
  }
]
```

### Get Industries
```http
GET /api/master/industries
```

### Get Sub-Industries
```http
GET /api/master/sub-industries?industry_id=cc0e8400-e29b-41d4-a716-446655440005
```

### Get Countries
```http
GET /api/master/countries
```

### Get Annual Turnover Bands
```http
GET /api/master/annual-turnovers
```

### Get Employee Bands
```http
GET /api/master/employee-bands
```

### Get Transaction Indicators
```http
GET /api/master/transaction-indicators?type=Revenue
```

**Supported types:** `Revenue`, `Spend`

---

## 🔧 Important Notes

### UUID Format
- All IDs are UUID v4 format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- Length: 36 characters (including hyphens)
- Example: `550e8400-e29b-41d4-a716-446655440000`

### Common Errors

**1. Invalid UUID Format**
```json
{
  "detail": [
    {
      "loc": ["body", "company_id"],
      "msg": "value is not a valid uuid",
      "type": "type_error.uuid"
    }
  ]
}
```

**2. Company Not Found**
```json
{
  "detail": "Company not found"
}
```

**3. Duplicate CIN**
```json
{
  "detail": "Company with same legal name and CIN already exists"
}
```

### Testing with cURL

```bash
# Get master data (no auth for demo)
curl http://localhost:8000/api/master/entity-types

# Search companies
curl -H "Authorization: Bearer demo-token" \
     "http://localhost:8000/api/company-search?q=apex"

# Create company
curl -X POST http://localhost:8000/api/company-create \
  -H "Authorization: Bearer demo-token" \
  -H "Content-Type: application/json" \
  -d '{
    "legal_name": "Test Co Ltd",
    "entity_type_id": "aa0e8400-e29b-41d4-a716-446655440003",
    "country_id": "660e8400-e29b-41d4-a716-446655440001",
    "registered_address": "123 Test St"
  }'
```

---

## 📊 Data Flow Example

```
1. Get master data
   GET /api/master/entity-types → Store entity_type_id
   GET /api/master/countries → Store country_id

2. Create company
   POST /api/company-create
   {
     "entity_type_id": "<from step 1>",
     "country_id": "<from step 1>",
     ...
   }
   → Returns company_id

3. Add regulatory data
   POST /api/regulatory-upsert
   {
     "company_id": "<from step 2>",
     ...
   }

4. Create engagement
   POST /api/engagement-create
   {
     "company_id": "<from step 2>",
     ...
   }
   → Returns engagement_id

5. Save context
   POST /api/engagement-context
   {
     "engagement_id": "<from step 4>",
     "context": {...}
   }
```

---

**Last Updated:** 2026-02-09  
**Version:** 1.0 (Post-UUID-Fix)
