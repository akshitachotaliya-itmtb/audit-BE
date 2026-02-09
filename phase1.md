# Screen 1 – Target Company Setup

## Purpose of this Screen
This screen is used to:
- Create / select the company that is being audited
- Capture core entity, regulatory, industry, and engagement anchor information
- Provide enough structure for the system to:
  - Identify the company (for any registry / external data)
  - Understand industry and size
  - Know audit period & currency to run BE + VA in the next step

### Exit Condition
When the user clicks **“Confirm & Run Analysis”** with all mandatory fields valid, the system:
1. Creates or updates Company Master
2. Creates Engagement record
3. Triggers **Understand Business Environment** job (Screen 2)

---

## A. Understand Target Identity

### Objective
Unambiguous identification of the legal entity.

### Fields

#### Target Company Information
- Enter Company Name and system searches to check if entity already exists in Company Master
- Results listing:
  - Name
  - Country
  - CIN
  - Sector
- Options:
  - Use Existing Company
  - Create New Company

#### If Create New Company
- Legal Name (text, **mandatory**)
- Display / Short Name (text)
- Entity Type (dropdown, **mandatory**)
  - Company
  - LLP
  - Partnership
  - Proprietorship
  - Other
- Country of Incorporation (dropdown, **mandatory**)
- Registered Address (multiline, **mandatory**)
- Operational HQ Address (multiline + “Same as Registered” toggle)
- Part of Group? (Yes/No, **mandatory**)
  - If Yes → Group / Parent Name (search from Group Master or free text)

### Behaviour
- If existing company chosen, most fields appear read-only
- New company data is written into Company Master on confirmation

---

## B. Regulatory & Registration

### Objective
Capture statutory IDs required for external lookups and risk context.

### Fields
- CIN / Corporate Registration Number (text; mandatory for Indian companies)
- PAN / Tax ID (text, **mandatory**)
- GST / VAT / Tax Registration IDs (list/repeater, optional)
- LEI (Legal Entity Identifier) (optional)
- Listed Status (**mandatory**)
  - Listed / Unlisted
  - If Listed:
    - Exchange(s)
    - Ticker Symbol

### Validations
- CIN / LEI pattern validation
- PAN format validation
- If registry data mismatch > X% → soft warning:
  > “Registered name differs significantly – review before continuing.”

---

## C. Industry & Size Profile

### Objective
Give the BE engine and IA universe logic a clear industry and scale picture.

### Fields
- Industry Sector (dropdown, **mandatory**)
  - Manufacturing
  - Services
  - Trading
  - BFSI
- Sub-Sector / Industry Segment (dependent dropdown, **mandatory**)
  - Auto Components, Pharma, Chemicals, FMCG, Engineering, etc.
- Standard Industry Code (**mandatory**)
  - NIC / NAICS / Custom
- Nature of Operations (multi-select, **mandatory**)
  - Manufacturing
  - Trading
  - Services
  - Project-based
  - Contract manufacturing
  - OEM / ODM
- Business Model (multi-select, optional)
  - B2B / B2C / B2G / Export-oriented

#### Scale Indicators (Optional)
- Annual Turnover Band
  - <100 Cr
  - 100–500 Cr
  - 500–1000 Cr
  - >1000 Cr
- Employee Count Band

#### Manufacturing Footprint (If Manufacturing)
- Number of Plants / Factories
- High-level Plant Locations (City, State, Country)
- SEZ / EOU presence (Yes/No)

#### Transaction Indicators (**Mandatory**)
- Revenue
  - Domestic
  - Domestic and Export
  - Only Export
- Spends
  - Domestic
  - Domestic and Export
  - Only Export

### System Use
- Sector + Sub-sector + Scale feed:
  - External industry benchmarks for VA
  - Risk overlays and IA universe templates

---

## D. Engagement Context

### Objective
Anchor this company to a specific IA cycle so BE + VA know which period to analyse.

### Fields
- Engagement Name (text)
  - Example: “FY25 Internal Audit – Entity Level”
- Engagement ID (auto-generated, editable with permission)
  - Pattern: `[ClientCode]-[FY]-[Seq]`
- Audit Type (dropdown)
  - Full-scope IA
  - IFC
  - SOX
- Reporting Currency (dropdown, multi-currency)

### Behaviour
- On change of FY/period, system flags:
  > “This period will be used for Risk Assessment and Value Analytics – ensure it aligns with available financial data.”

---

## Buttons & Behaviour

### Primary Actions

#### 1. Save Draft
- Saves entered data
- Allows incomplete mandatory fields
- Status: *Draft – Target Company Setup Incomplete*
- No BE + VA run

#### 2. Confirm & Run Analysis
- Front-end validation
- Save/Update Company Master + Engagement
- Triggers Business Environment Study + Value Analytics (async)
- Redirects to Screen 2

#### 3. Cancel
- Warning: “Unsaved changes will be lost.”
- Returns to Engagements list

---

## Mandatory Field Logic (Summary)
If mandatory fields are missing and user clicks **Confirm & Run Analysis**, system displays a clear error list at the top.

---

## System Outputs from Screen 1
1. Company Master Record
   - Identity, regulatory, industry, size
2. Engagement Record
   - Audit period, FY, audit type, currency
3. Risk Environment + VA Input Metadata
   - Sector mapping and benchmark preferences

These are passed to:
- BE Engine
- VA Engine

---

# Screen 2 – Understand Business Environment

## Purpose
This screen exists to:
1. Display system-generated BE insights
2. Display system-generated VA insights
3. Allow users to validate insights
4. Convert validated insights into structured signals for:
   - Screen 3 – Problem Statements
   - Screen 4 – IA Universe
   - Screen 5 – Audit Areas

### This Screen Does NOT
- Create problem statements
- Create audit areas
- Assign ownership

---

## Entry Trigger & Data Flow

### Trigger
- Completion of Screen 1 → Confirm & Run Analysis

### System Actions (Async)
- Run BE Engine
- Run VA Engine
- Store raw indicators, interpretations, confidence scores

### Entry States
- Analysis Running
- Analysis Completed
- Partial Completed

---

## Section A – Risk Assessment Study

### Objective
Capture external and contextual risks impacting the company.

### Insight Card Structure
- Insight Title
- Dimension Tag
- Insight Statement
- Key Drivers
- User Validation Controls:
  - Relevant / Not Relevant
  - Override Type
  - User Comment

If marked **Not Relevant**, reason is mandatory.

---

## Value Analytics

### Objective
Highlight financial stress, inefficiencies, or abnormal trends.

### Financial Insight Card
- Metric Group
- Insight Statement
- Evidence Panel
- User Controls (same as BE)

### Stored Output
- Metric code
- Trend direction
- Deviation magnitude
- Relevance flag
- Override notes

---

## Consolidated Risk Signals
Only validated insights feed this view.

---

## Mandatory Completion Rules
- User must validate:
  - All high-confidence insights OR
  - Minimum X% of total insights

System blocks next step until conditions are met.

---

## Output of Screen 2
- Approved risks
- Approved financial stress points
- User-refined risk levels

Feeds:
- Screen 3
- Screen 4
- Screen 5

---

# Screen 3 – Define Problem Statements & Value Proposition

## Purpose
Convert validated intelligence into structured, audit-ready problem statements.

### Inputs
- Validated BE & VA insights
- User overrides
- Past audit reports (optional)

### Output
- Approved Problem Statement Register
- Traceability Map
- Audit Intent Layer

---

# Screen 4 – Determine Inherent Risk Universe

## Purpose
- Auto-generate IA risk universe
- Calculate inherent risk
- Recommend audit scope
- Allow user overrides

### Outputs
- Entity-specific IA Risk Universe
- Approved Audit Scope
- Audit Justification Register

---

# Screen 5 – Finalize Scope, Timelines & Audit Calendar

## Purpose
Convert approved audit scope into a time-bound audit plan.

### Outputs
1. Approved Annual Audit Plan
2. Planning Metadata
3. Defensible Audit Trail
