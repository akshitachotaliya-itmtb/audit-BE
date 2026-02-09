-- ============================================================
-- Internal Audit - BE Seed Data (Screens 1-5)
-- Uses UUID() for primary keys to match CHAR(36) schema
-- ============================================================

-- =========================
-- Screen 1: Masters
-- =========================

-- First, insert master data that other tables depend on

INSERT INTO entity_type_master (entity_type_id, name) VALUES
  (UUID(), 'Company'),
  (UUID(), 'LLP'),
  (UUID(), 'Partnership'),
  (UUID(), 'Proprietorship'),
  (UUID(), 'Other');

INSERT INTO group_master (group_id, name) VALUES
  (UUID(), 'Apex Group Holdings'),
  (UUID(), 'BlueWave Foods Group');

INSERT INTO industry_master (industry_id, name) VALUES
  (UUID(), 'Manufacturing'),
  (UUID(), 'Services'),
  (UUID(), 'Trading'),
  (UUID(), 'BFSI'),
  (UUID(), 'Food Processing');

-- We need to capture the UUID values for foreign key relationships
-- Using variables in MySQL for seed data

SET @entity_company = UUID();
SET @entity_llp = UUID();

SET @country_india = UUID();
SET @country_usa = UUID();
SET @country_uk = UUID();

SET @industry_mfg = (SELECT industry_id FROM industry_master WHERE name = 'Manufacturing' LIMIT 1);
SET @industry_service = (SELECT industry_id FROM industry_master WHERE name = 'Services' LIMIT 1);
SET @industry_trading = (SELECT industry_id FROM industry_master WHERE name = 'Trading' LIMIT 1);

INSERT INTO country_master (
  country_id, st_dt, e_dt, country_name, country_code, currency_code, currency_name, active, flag_link
) VALUES
  (@country_india, '2020-01-01 00:00:00', '9999-12-31', 'India', 'IND', 'INR', 'Indian Rupee', 1, NULL),
  (@country_usa, '2020-01-01 00:00:00', '9999-12-31', 'United States', 'USA', 'USD', 'US Dollar', 1, NULL),
  (@country_uk, '2020-01-01 00:00:00', '9999-12-31', 'United Kingdom', 'GBR', 'GBP', 'Pound Sterling', 1, NULL),
  (UUID(), '2020-01-01 00:00:00', '9999-12-31', 'United Arab Emirates', 'ARE', 'AED', 'UAE Dirham', 1, NULL),
  (UUID(), '2020-01-01 00:00:00', '9999-12-31', 'Singapore', 'SGP', 'SGD', 'Singapore Dollar', 1, NULL);

-- Sub industries
INSERT INTO sub_industry_master (sub_industry_id, industry_id, sub_industry_name) VALUES
  (UUID(), @industry_mfg, 'Auto Components'),
  (UUID(), @industry_service, 'Logistics and Warehousing'),
  (UUID(), @industry_trading, 'Retail Trading'),
  (UUID(), @industry_mfg, 'Pharmaceuticals'),
  (UUID(), (SELECT industry_id FROM industry_master WHERE name = 'Food Processing' LIMIT 1), 'Food Processing');

INSERT INTO industry_code_master (industry_code_id, code_type, code_description) VALUES
  (UUID(), 'NIC', '2930 - Manufacture of parts and accessories for motor vehicles'),
  (UUID(), 'NIC', '1030 - Processing and preserving of fruit and vegetables'),
  (UUID(), 'NIC', '2100 - Manufacture of pharmaceuticals'),
  (UUID(), 'NIC', '5210 - Warehousing and storage'),
  (UUID(), 'NIC', '4711 - Retail sale in non-specialized stores');

INSERT INTO nature_of_operation_master (nature_of_operation_id, name) VALUES
  (UUID(), 'Manufacturing'),
  (UUID(), 'Trading'),
  (UUID(), 'Services'),
  (UUID(), 'Project-based'),
  (UUID(), 'Contract manufacturing');

INSERT INTO business_model_master (business_model_id, name) VALUES
  (UUID(), 'B2B'),
  (UUID(), 'B2C'),
  (UUID(), 'B2G'),
  (UUID(), 'Export-oriented'),
  (UUID(), 'Omni-channel');

INSERT INTO annual_turnover_master (annual_turnover_id, band_label, is_indian) VALUES
  (UUID(), '<100 Cr', 1),
  (UUID(), '100-500 Cr', 1),
  (UUID(), '500-1000 Cr', 1),
  (UUID(), '>1000 Cr', 1),
  (UUID(), '1000-5000 Cr', 1);

INSERT INTO employee_master (employee_band_id, band_label) VALUES
  (UUID(), '1-50'),
  (UUID(), '51-200'),
  (UUID(), '201-500'),
  (UUID(), '501-1000'),
  (UUID(), '>1000');

INSERT INTO transaction_indicator (indicator_id, indicator_type, indicator_label) VALUES
  (UUID(), 'Revenue', 'Domestic'),
  (UUID(), 'Revenue', 'Domestic and Export'),
  (UUID(), 'Revenue', 'Only Export'),
  (UUID(), 'Spend', 'Domestic'),
  (UUID(), 'Spend', 'Domestic and Export');

-- =========================
-- Screen 2: BE / VA Lookups
-- =========================
INSERT INTO be_dimension_master (dimension_id, dimension_name) VALUES
  (UUID(), 'Regulatory'),
  (UUID(), 'Economic and Macro'),
  (UUID(), 'Industry and Sector'),
  (UUID(), 'Market and Competition'),
  (UUID(), 'Supply Chain');

INSERT INTO va_metric_group_master (metric_group_id, group_name) VALUES
  (UUID(), 'Profitability'),
  (UUID(), 'Liquidity'),
  (UUID(), 'Leverage'),
  (UUID(), 'Efficiency'),
  (UUID(), 'Growth');

INSERT INTO relevance_reason_master (reason_id, reason_label) VALUES
  (UUID(), 'Not applicable to company'),
  (UUID(), 'Already mitigated'),
  (UUID(), 'Data not reliable'),
  (UUID(), 'Outside audit scope'),
  (UUID(), 'Timing not relevant');

INSERT INTO override_type_master (override_type_id, override_label) VALUES
  (UUID(), 'Accept as-is'),
  (UUID(), 'Modify risk'),
  (UUID(), 'Modify likelihood'),
  (UUID(), 'Re-interpret insight'),
  (UUID(), 'Adjust severity');

INSERT INTO risk_theme_master (risk_theme_id, risk_theme_name) VALUES
  (UUID(), 'Profitability'),
  (UUID(), 'Working Capital'),
  (UUID(), 'Compliance'),
  (UUID(), 'Supply Chain'),
  (UUID(), 'Liquidity');

INSERT INTO risk_level_master (risk_level_id, risk_level_label) VALUES
  (UUID(), 'Very High'),
  (UUID(), 'High'),
  (UUID(), 'Medium'),
  (UUID(), 'Low'),
  (UUID(), 'Very Low');

-- =========================
-- Screen 3: Problem Statement Masters
-- =========================
INSERT INTO impact_type_master (impact_type_id, impact_label) VALUES
  (UUID(), 'Financial'),
  (UUID(), 'Operational'),
  (UUID(), 'Compliance'),
  (UUID(), 'Strategic'),
  (UUID(), 'Reputational');

INSERT INTO time_horizon_master (time_horizon_id, horizon_label) VALUES
  (UUID(), 'Immediate'),
  (UUID(), 'Short-term'),
  (UUID(), 'Medium-term'),
  (UUID(), 'Long-term'),
  (UUID(), 'Ongoing');

INSERT INTO process_master (process_id, process_name) VALUES
  (UUID(), 'Procurement'),
  (UUID(), 'Inventory and Warehousing'),
  (UUID(), 'Production and Operations'),
  (UUID(), 'Sales and Distribution'),
  (UUID(), 'Finance and Accounts');

-- Capture process IDs for sub-process insertion
SET @proc_procurement = (SELECT process_id FROM process_master WHERE process_name = 'Procurement' LIMIT 1);
SET @proc_inventory = (SELECT process_id FROM process_master WHERE process_name = 'Inventory and Warehousing' LIMIT 1);
SET @proc_production = (SELECT process_id FROM process_master WHERE process_name = 'Production and Operations' LIMIT 1);
SET @proc_sales = (SELECT process_id FROM process_master WHERE process_name = 'Sales and Distribution' LIMIT 1);
SET @proc_finance = (SELECT process_id FROM process_master WHERE process_name = 'Finance and Accounts' LIMIT 1);

INSERT INTO sub_process_master (sub_process_id, process_id, sub_process_name) VALUES
  (UUID(), @proc_procurement, 'Vendor onboarding'),
  (UUID(), @proc_inventory, 'Inventory planning'),
  (UUID(), @proc_production, 'Quality control'),
  (UUID(), @proc_sales, 'Order fulfillment'),
  (UUID(), @proc_finance, 'Accounts payable');

-- =========================
-- Screen 4: Universe Masters
-- =========================
INSERT INTO scope_override_reason_master (reason_id, reason_label) VALUES
  (UUID(), 'Risk overstated'),
  (UUID(), 'Risk understated'),
  (UUID(), 'Compensating controls exist'),
  (UUID(), 'Already audited recently'),
  (UUID(), 'Outside current audit focus');

-- =========================
-- Screen 5: Audit Plan Masters
-- =========================
INSERT INTO audit_frequency_master (frequency_id, frequency_label) VALUES
  (UUID(), 'Annual'),
  (UUID(), 'Semi-Annual'),
  (UUID(), '18 months'),
  (UUID(), '2 years'),
  (UUID(), '3 years');

INSERT INTO audit_plan_type_master (plan_type_id, plan_type_label) VALUES
  (UUID(), 'Full-scope'),
  (UUID(), 'Follow-up'),
  (UUID(), 'Thematic'),
  (UUID(), 'Compliance'),
  (UUID(), 'Operational');

-- =========================
-- Example: Create Sample Company + Engagement (Optional)
-- Uncomment below to add sample transactional data
-- =========================


SET @demo_user = UUID();
SET @demo_entity_type = (SELECT entity_type_id FROM entity_type_master WHERE name = 'Company' LIMIT 1);

SET @demo_company = UUID();
INSERT INTO company_master (
  company_id, legal_name, display_name, entity_type_id, country_id,
  registered_address, operational_hq_address, is_part_of_group, parent_group_id,
  status, created_by
) VALUES (
  @demo_company, 
  'Apex Manufacturing Pvt Ltd', 
  'Apex Manufacturing', 
  @demo_entity_type, 
  @country_india,
  '12 Industrial Estate, Pune, MH, India', 
  'Apex Towers, Pune, MH, India', 
  0, 
  NULL,
  'Confirmed', 
  @demo_user
);

-- Add regulatory data
INSERT INTO regulatory_master (
  registration_id, company_id, cin, pan, lei, listed_status, exchange_list, ticker_symbol
) VALUES (
  UUID(), 
  @demo_company, 
  'L29304MH2010PLC201001', 
  'AAECA1234F', 
  '5493001KJTIIGC8Y1R12', 
  'Listed', 
  '["NSE","BSE"]', 
  'APEX'
);

-- Create engagement
SET @demo_engagement = UUID();
INSERT INTO engagement (
  engagement_id, user_id, company_id, report_id, engagement_name, engagement_code,
  audit_type, reporting_currency, audit_fy, status, confirmed_at, confirmed_by
) VALUES (
  @demo_engagement,
  @demo_user,
  @demo_company, 
  NULL, 
  'FY25 Internal Audit - Entity Level', 
  'APEX-FY25-001', 
  'Full-scope IA', 
  '["INR"]', 
  'FY25', 
  'Confirmed', 
  '2026-01-10 10:00:00', 
  @demo_user
);
