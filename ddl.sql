-- ============================================================
-- Internal Audit - BE DDL (Screens 1-5)
-- MySQL 5.7+ / 8.x / InnoDB / utf8mb4
-- ============================================================

CREATE TABLE gen_seq (
  key_id CHAR(36) NOT NULL,
  surr_key bigint DEFAULT NULL,
  key_hash varchar(15) DEFAULT NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (key_id),
  UNIQUE KEY key_hash (key_hash),
  KEY key_hash_2 (key_hash)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
CREATE TABLE error_logs (
  er_id CHAR(36) NOT NULL,
  lg_id CHAR(36) DEFAULT NULL,
  er_code smallint NOT NULL,
  er_name varchar(500) NOT NULL,
  er_msg varchar(5000) NOT NULL,
  fail_cmp varchar(250) DEFAULT NULL,
  dt_ts datetime NOT NULL,
  seq_no smallint DEFAULT NULL,
  solutn varchar(500) DEFAULT NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (er_id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
CREATE TABLE browsr_det (
  u_id CHAR(36) NOT NULL,
  name varchar(20) NOT NULL,
  ver varchar(10) DEFAULT NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (u_id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
INSERT INTO browsr_det (`u_id`, `name`, `ver`)
VALUES (UUID(), 'chrome', NULL);
INSERT INTO browsr_det (`u_id`, `name`, `ver`)
VALUES (UUID(), 'safari', NULL);
INSERT INTO browsr_det (`u_id`, `name`, `ver`)
VALUES (UUID(), 'unknown', NULL);
INSERT INTO browsr_det (`u_id`, `name`, `ver`)
VALUES (UUID(), 'firefox', NULL);
INSERT INTO browsr_det (`u_id`, `name`, `ver`)
VALUES (UUID(), 'webkit', NULL);
INSERT INTO browsr_det (`u_id`, `name`, `ver`)
VALUES (UUID(), 'opera', NULL);
INSERT INTO browsr_det (`u_id`, `name`, `ver`)
VALUES (UUID(), 'google', NULL);
INSERT INTO browsr_det (`u_id`, `name`, `ver`)
VALUES (UUID(), 'mozilla', NULL);
INSERT INTO browsr_det (`u_id`, `name`, `ver`)
VALUES (UUID(), 'edge', NULL);
CREATE TABLE log_data (
  lg_id CHAR(36) NOT NULL,
  user_id CHAR(36) DEFAULT NULL,
  ip_add varchar(20) DEFAULT NULL,
  st_t datetime NOT NULL,
  ex_t bigint NOT NULL,
  scp_name varchar(500) NOT NULL,
  end_pt varchar(500) NOT NULL,
  browsr_id CHAR(36) DEFAULT NULL,
  os_id CHAR(36) DEFAULT NULL,
  auth_res smallint DEFAULT NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (lg_id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
CREATE TABLE opsys_det (
  u_id CHAR(36) NOT NULL,
  name varchar(20) NOT NULL,
  ver varchar(10) DEFAULT NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (u_id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
INSERT INTO opsys_det (`u_id`, `name`, `ver`)
VALUES (UUID(), 'windows', NULL);
INSERT INTO opsys_det (`u_id`, `name`, `ver`)
VALUES (UUID(), 'macos', NULL);
INSERT INTO opsys_det (`u_id`, `name`, `ver`)
VALUES (UUID(), 'android', NULL);
INSERT INTO opsys_det (`u_id`, `name`, `ver`)
VALUES (UUID(), 'unknown', NULL);
INSERT INTO opsys_det (`u_id`, `name`, `ver`)
VALUES (UUID(), 'iphone', NULL);
INSERT INTO opsys_det (`u_id`, `name`, `ver`)
VALUES (UUID(), 'ipad', NULL);
INSERT INTO opsys_det (`u_id`, `name`, `ver`)
VALUES (UUID(), 'linux', NULL);
INSERT INTO opsys_det (`u_id`, `name`, `ver`)
VALUES (UUID(), 'chromeos', NULL);

create Table user_data (
 u_id CHAR(36) NOT NULL,
 st_dt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 e_dt DATETIME NOT NULL DEFAULT '9999-12-31',
 first_name Varchar(100),
 last_name Varchar(100),
 dob Date,
 gender Char(1), /* M - Male, F - Female, X - prefer not to say */
 image_path varchar(500),
 account_type_id CHAR(36), /* from account_typ_master */
  is_active TINYINT(1) NOT NULL DEFAULT 1,
 PRIMARY KEY (u_id, st_dt),
 index(u_id)
);

create table organization (
  org_id CHAR(36) NOT NULL,
  st_dt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  e_dt DATETIME NOT NULL DEFAULT '9999-12-31',
  org_name varchar(200) NOT NULL,
--  changes bellow
  website varchar(100),
  industry varchar(30), -- dropdown
  country varchar(15),
  org_typ_id CHAR(36), -- (cust/vendor) mapping account type master 
  profile_path varchar(200),
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  index(org_id)
);

create table user_rel(
   org_id CHAR(36) not null,
   u_id CHAR(36) not null,
   st_dt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
   e_dt DATETIME NOT NULL DEFAULT '9999-12-31',
   typ tinyint(1) not null, -- (ind/sub) mapping account type master 
  is_active TINYINT(1) NOT NULL DEFAULT 1,
   PRIMARY KEY (org_id, u_id, st_dt)
);


create table email (
  email_id CHAR(36) NOT NULL,
  u_id CHAR(36) NOT NULL,
  email varchar(100) NOT NULL,
  is_verified TINYINT,
  st_dt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  e_dt DATETIME NOT NULL DEFAULT '9999-12-31',
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (email_id, st_dt),
  index(u_id),
  index(email)
);

-- insert into email VALUES (UUID(), 101, "cecal77780@bustayes.com", 1, CURRENT_TIMESTAMP, "9999-12-31");
create table phone (
  phone_id CHAR(36) NOT NULL,
  u_id CHAR(36) NOT NULL,
  phone varchar(15) NOT NULL,
  st_dt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  e_dt DATETIME NOT NULL DEFAULT '9999-12-31',
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (phone_id, st_dt),
  index(u_id),
  index(phone)
);

-- create products for both purchase and credit 
create table product(
  prd_id CHAR(36), /*unique id given to every product, surrogate key.*/
  prd_type_id CHAR(36) NOT NULL,
  st_dt DATETIME DEFAULT CURRENT_TIMESTAMP,
  e_dt DATETIME DEFAULT '9999-12-31',
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  INDEX (prd_id)
);

create table product_rel(
  parent_prd_id CHAR(36) NOT NULL,
  child_prd_id CHAR(36) NOT NULL, /* natural key, variant id, if relationship is parent child, this will be separate, else it will same as int_product_id */
  st_dt DATETIME DEFAULT CURRENT_TIMESTAMP,
  e_dt DATETIME DEFAULT '9999-12-31',
  is_active TINYINT(1) NOT NULL DEFAULT 1
);

create table properties_master(
  property_id CHAR(36),
  property_name varchar(100), /*eta, xpiry, size, gender */
  st_dt DATETIME DEFAULT CURRENT_TIMESTAMP,
  edt DATETIME DEFAULT '9999-12-31',
  val_type varchar(100), /*int, date, char*/
  is_active TINYINT(1) NOT NULL DEFAULT 1
);

create table product_property_rel(
  product_id CHAR(36),
  property_id CHAR(36),
  st_dt DATETIME DEFAULT CURRENT_TIMESTAMP,
  edt DATETIME DEFAULT '9999-12-31',
  property_val varchar(1000),
  is_active TINYINT(1) NOT NULL DEFAULT 1
);

create table product_property_role (
  product_id CHAR(36),
  property_id CHAR(36), 
  st_dt DATETIME DEFAULT CURRENT_TIMESTAMP,
  edt DATETIME DEFAULT '9999-12-31', 
  access_role char(10),
  access_typ char(10), -- 1 - read, 2- write, 3 - delete, 4 - update 
  is_active TINYINT(1) NOT NULL DEFAULT 1
);

-- REPORTS BAG
-- ============================================
create table carts (
  cart_id CHAR(36) NOT NULL,
  u_id CHAR(36) NOT NULL,
  product_id CHAR(36) NOT NULL, /* product id from product table */
  product_type char(1),/* p- product,  o - offer  */
  qty tinyint,
  price decimal(10, 2), -- credit / amount
  total_price decimal(10, 2),/* price x qty */
  cart_status CHAR(1),/* 1 - active, 2 - expired, */
  rec_ts DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (cart_id, product_id),
  INDEX (cart_id),
  INDEX (u_id)
);

-- CREDIT
-- ============================================ 
create table coin_balance(
   /*table to store current coin balance for users*/
   /*this table will be used to fetch current coin balance whenever needed*/
   u_id CHAR(36) not null,
   coin_balance bigint not null,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
   index(u_id)
);

create table coin_policy_master(
   /*master table to decide coins transacted/charged for different tasks*/
   policy_id CHAR(36) not null, /* report type id */
   account_typ_id CHAR(36) not null, /*for now it will be 3*/
   task_name varchar(100), /*report generation for <report name>*/
   coin_cost bigint not null, /*positive when coins are to be given, negative when they are to be charged*/
   e_dt DATETIME NOT NULL DEFAULT '9999-12-31',
   is_active TINYINT(1) NOT NULL DEFAULT 1
);
-- insert into coin_policy_master VALUES (UUID(), 3, "Onboarding Free Credit", 2, '9999-12-31')
create table coin_transactions(
   /*coin balance is for individuals not companies*/
   transaction_id CHAR(36) not null, /*unique id for each transaction*/
   u_id CHAR(36) not null,
   dtts timestamp default CURRENT_TIMESTAMP,
   ref_transaction_id CHAR(36), /* payment id */
   purchased_service_typ tinyint, /*1 = report 2 = purchase*/
   coin_delta bigint, /*negative value if coins paid, positive value if coins added*/
   coin_balance bigint,
   transaction_note varchar(200),
  is_active TINYINT(1) NOT NULL DEFAULT 1,
   index(u_id),
   index(transaction_id)
);



-- ORDERS
-- ============================================
create table orders (  
-- orders for purchase transaction or report creations
 order_id CHAR(36) NOT NULL, /*unique id each time a payment is initiated*/
 cart_id CHAR(36) NOT NULL,
 u_id CHAR(36) NOT NULL, /*purchaser*/
 seller_id CHAR(36) NOT NULL, 
 payment_time DATETIME,
 order_status_id CHAR(36) NOT NULL, /*0 not complete 1 complete*/
 order_price decimal(10, 2),/* price without discount*/
 order_discount decimal(10, 2),
 final_price decimal(10, 2),/* price after discount add and tax deduct*/
 paid_amount decimal(10, 2),/* should be same as final_price, paid amount by customer after tax, offers*/
 
  is_active TINYINT(1) NOT NULL DEFAULT 1,
 PRIMARY KEY (order_id),
 INDEX (order_id),
 INDEX (u_id)
);


create table order_status (
  order_status_id CHAR(36) NOT NULL, -- unique id 
  order_id CHAR(36) NOT NULL,
  product_id CHAR(36) NOT NULL,
  u_id CHAR(36) NOT NULL,
  prd_type_id CHAR(36) NOT NULL,
  step_id CHAR(36) not null, -- 1 - step 1, 2 - step 2, 3 - step 3
  step_phase tinyint not null, -- 1 - init, 2 - inprogress, 3 - failed, 4 - complete --5 draft
  retrial_attempt tinyint not null, -- to store number of retrial attempt
  notes VARCHAR(200) DEFAULT NULL, 
  rec_ts DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  status_sdt DATETIME NULL,
  status_edt DATETIME NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  INDEX (order_id),
  INDEX (u_id)
);

-- select order_status_id, order_id, product_id, u_id, prd_type_id, status_id, status_phase from order_status;

create table order_attributes (
  order_id CHAR(36) NOT NULL,
  add_id CHAR(36) NOT NULL, -- address id
  st_dt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  e_dt DATETIME NOT NULL DEFAULT '9999-12-31',
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  primary key (order_id)
);



-- PAYMENT 
-- ===============================
create table pymt_details(
  payment_id CHAR(36) NOT NULL, -- system generated unique id
  order_id CHAR(36) NOT NULL, -- system generated order id
  gateway_payment_id CHAR(36) NOT NULL, -- gateway generated payment id
  user_id CHAR(36) NOT NULL, -- purchaser
  st_dt  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, -- payment start time
  e_dt  DATETIME NOT NULL DEFAULT '9999-12-31',
  pymnt_hash varchar(500), -- gateway generated hash/key
  pymt_stat varchar(50),
  pymt_currency varchar(10) NOT NULL,
  pymt_comment  varchar(200), -- user defiend comment 
  pymt_gateway varchar(50) NOT NULL, -- STRIPE
  pymt_amnt float NOT NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1
);


create table tax_applied (
  tax_applied_id CHAR(36) NOT NULL,
  order_id CHAR(36) NOT NULL,
  tax_rate_id CHAR(36) NOT NULL, -- mapping with tax_master tax_rate_id
  tax_amount float, -- tax amount after calculation
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  INDEX(order_id)
);



create table tax_master (
  tax_rate_id CHAR(36) NOT NULL, -- system generated id
  tax_name varchar(20) not null, -- GST, SGST
  tax_rate float not null, -- standard tax rate
  region_id CHAR(36) not null,
  st_dt  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  e_dt DATETIME DEFAULT '9999-12-31',
  is_active TINYINT(1) NOT NULL DEFAULT 1
);




-- org to tax mapping
create table tax_policy_master (
  tax_policy_id CHAR(36) NOT NULL,
  tax_rate_id CHAR(36) NOT NULL, -- mapping with tax_master tax_rate_id
  rel_id CHAR(36) NOT NULL, -- it should be organisation/individual id
  rel_typ smallint not null,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  INDEX(rel_id)
);



-- INVOICE 
-- ================================
CREATE TABLE invoice (
  invoice_id CHAR(36) not null, 
  u_id CHAR(36) not null, 
  org_id CHAR(36) not null, -- org_id of seller, mapping org_id with organization
  order_id CHAR(36) not null, -- mapping order_id with orders order_id
  payment_id CHAR(36) not null, -- mapping payment_id with pymt_details payment_id
  invoice_link varchar(200) not null,
  time_stamp datetime not null default CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1
);

CREATE TABLE invoice_master (
    rel_id CHAR(36) NOT NULL, -- u_id or org_id
    rel_typ smallint NOT NULL,  -- 1- org  or 2- individual
    address_id CHAR(36) NOT NULL, -- map with address table
    invoice_notice VARCHAR(3000),
    invoice_refund_policy VARCHAR(3000),
    template VARCHAR(100),
  is_active TINYINT(1) NOT NULL DEFAULT 1
);

CREATE TABLE region_master (
  region_id CHAR(36) NOT NULL DEFAULT (UUID()),
  region_name VARCHAR(50),
  region_code VARCHAR(10),
  dial_code CHAR(7),
  currency CHAR(10),
  flag_link VARCHAR(200),
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (region_id)
);

CREATE TABLE country_master (
  country_id CHAR(36) NOT NULL,
  st_dt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  e_dt DATETIME NOT NULL DEFAULT '9999-12-31',
  country_name VARCHAR(100) NOT NULL,
  country_code CHAR(3) NOT NULL,
  currency_code CHAR(3) NOT NULL,
  currency_name VARCHAR(50) NOT NULL,
  active TINYINT(1) NOT NULL DEFAULT 1,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  flag_link VARCHAR(200),
  PRIMARY KEY (country_id, st_dt),
  INDEX (country_id),
  INDEX (country_code),
  INDEX (active)
);

CREATE TABLE states (
  region_id CHAR(36) not null,
  state_name VARCHAR(100),
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  index(region_id)
);

-- =========================
-- Screen 1: Company Master
-- =========================
CREATE TABLE company_master (
  -- sample data of company_master
  company_id CHAR(36) NOT NULL DEFAULT (UUID()),
  legal_name VARCHAR(255) NOT NULL,
  display_name VARCHAR(255) NULL,
  entity_type_id CHAR(36) NOT NULL,
  country_id CHAR(36) NOT NULL,
  registered_address TEXT NOT NULL,
  operational_hq_address TEXT NULL,
  is_part_of_group TINYINT(1) NOT NULL DEFAULT 0,
  parent_group_id CHAR(36) NULL,

  status ENUM('Draft','Confirmed','Archived') NOT NULL DEFAULT 'Draft',

  created_by CHAR(36) NOT NULL,
  updated_by CHAR(36) NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (company_id),
  INDEX idx_legal_name (legal_name),
  FULLTEXT INDEX ft_company_search (legal_name, display_name),
  INDEX idx_country (country_id),
  INDEX idx_entity_type (entity_type_id),
  INDEX idx_parent_group (parent_group_id)
) ENGINE=InnoDB;




-- =========================
-- Screen 1: Regulatory / Registration Master
-- =========================
CREATE TABLE regulatory_master (
  -- sample data of regulatory_master
  registration_id CHAR(36) NOT NULL DEFAULT (UUID()),
  company_id CHAR(36) NOT NULL,
  country_id CHAR(36) NULL,

  cin VARCHAR(25) NULL,
  pan VARCHAR(15) NOT NULL,
  lei VARCHAR(30) NULL,

  listed_status ENUM('Listed','Unlisted') NOT NULL,
  exchange_list JSON NULL,
  ticker_symbol VARCHAR(30) NULL,

  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (registration_id),
  UNIQUE KEY uniq_company_reg (company_id),
  INDEX idx_company (company_id),
  INDEX idx_country (country_id)
) ENGINE=InnoDB;




-- Optional: tax registrations (GST/VAT repeater)
CREATE TABLE company_tax_registration (
  -- sample data of company_tax_registration
  tax_reg_id CHAR(36) NOT NULL DEFAULT (UUID()),
  company_id CHAR(36) NOT NULL,
  tax_type VARCHAR(30) NOT NULL,
  tax_id VARCHAR(50) NOT NULL,
  country_id CHAR(36) NULL,

  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (tax_reg_id),
  INDEX idx_company (company_id),
  INDEX idx_tax_id (tax_id)
) ENGINE=InnoDB;




CREATE TABLE entity_type_master (
  entity_type_id CHAR(36) NOT NULL DEFAULT (UUID()),
  name VARCHAR(100) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (entity_type_id)
) ENGINE=InnoDB;

CREATE TABLE group_master (
  group_id CHAR(36) NOT NULL DEFAULT (UUID()),
  name VARCHAR(255) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (group_id)
) ENGINE=InnoDB;

CREATE TABLE industry_master (
  industry_id CHAR(36) NOT NULL DEFAULT (UUID()),
  name VARCHAR(255) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (industry_id)
) ENGINE=InnoDB;


-- =========================
-- Screen 1: Industry & Size Master (linked to company_master)
-- =========================
CREATE TABLE company_industry_size_master (
  -- sample data of company_industry_size_master
  industry_size_id CHAR(36) NOT NULL DEFAULT (UUID()),
  company_id CHAR(36) NOT NULL,

  industry_sector_id CHAR(36) NOT NULL,
  sub_industry_id CHAR(36) NOT NULL,
  industry_code_id CHAR(36) NOT NULL,

  annual_turnover_id CHAR(36) NULL,
  employee_band_id CHAR(36) NULL,

  manufacturing_plants_count INT NULL,
  sez_eou_presence TINYINT(1) NULL,

  revenue_indicator_id CHAR(36) NOT NULL,
  spend_indicator_id CHAR(36) NOT NULL,

  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (industry_size_id),
  UNIQUE KEY uniq_company_industry (company_id),
  INDEX idx_sector (industry_sector_id),
  INDEX idx_sub_sector (sub_industry_id)
) ENGINE=InnoDB;




-- =========================
-- Screen 1: Sub-Industry Master
-- =========================
CREATE TABLE sub_industry_master (
  -- sample data of sub_industry_master
  sub_industry_id CHAR(36) NOT NULL,
  industry_id CHAR(36) NOT NULL, -- industry_master
  sub_industry_name VARCHAR(255) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (sub_industry_id),
  INDEX (industry_id)
) ENGINE=InnoDB;



-- =========================
-- Screen 1: Industry Code Master
-- =========================
CREATE TABLE industry_code_master (
  -- sample data of industry_code_master
  industry_code_id CHAR(36) NOT NULL,
  code_type VARCHAR(30) NOT NULL,
  code_description VARCHAR(255) NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (industry_code_id),
  INDEX (code_type)
) ENGINE=InnoDB;



-- =========================
-- Screen 1: Nature of Operation Master
-- =========================
CREATE TABLE nature_of_operation_master (
  -- sample data of nature_of_operation_master
  nature_of_operation_id CHAR(36) NOT NULL,
  name VARCHAR(100) NOT NULL, -- Manufacturing, Trading, Services, etc.
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (nature_of_operation_id)
) ENGINE=InnoDB;



-- =========================
-- Screen 1: Business Model Master
-- =========================
CREATE TABLE business_model_master (
  -- sample data of business_model_master
  business_model_id CHAR(36) NOT NULL,
  name VARCHAR(100) NOT NULL, -- B2B, B2C, B2G, Export-oriented
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (business_model_id)
) ENGINE=InnoDB;



-- =========================
-- Screen 1: Annual Turnover Master
-- =========================
CREATE TABLE annual_turnover_master (
  -- sample data of annual_turnover_master
  annual_turnover_id CHAR(36) NOT NULL,
  band_label VARCHAR(50) NOT NULL, -- <100 Cr, 100-500 Cr, etc
  is_indian TINYINT(1) NOT NULL DEFAULT 1,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (annual_turnover_id)
) ENGINE=InnoDB;



-- =========================
-- Screen 1: Employee Band Master
-- =========================
CREATE TABLE employee_master (
  -- sample data of employee_master
  employee_band_id CHAR(36) NOT NULL,
  band_label VARCHAR(50) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (employee_band_id)
) ENGINE=InnoDB;



-- =========================
-- Screen 1: Company Manufacturing List
-- =========================
CREATE TABLE company_manufacturing_list (
  -- sample data of company_manufacturing_list
  manufacturing_id CHAR(36) NOT NULL DEFAULT (UUID()),
  company_id CHAR(36) NOT NULL,
  plant_name VARCHAR(255) NULL,
  city VARCHAR(100) NULL,
  state VARCHAR(100) NULL,
  country_id CHAR(36) NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (manufacturing_id),
  INDEX (company_id)
) ENGINE=InnoDB;



-- =========================
-- Screen 1: Transaction Indicator Master
-- =========================
CREATE TABLE transaction_indicator (
  -- sample data of transaction_indicator
  indicator_id CHAR(36) NOT NULL,
  indicator_type ENUM('Revenue','Spend') NOT NULL,
  indicator_label VARCHAR(100) NOT NULL, -- Domestic / Domestic+Export / Only Export
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (indicator_id),
  INDEX (indicator_type)
) ENGINE=InnoDB;



-- =========================
-- Screen 1: Engagement Table
-- =========================
CREATE TABLE engagement (
  -- sample data of engagement
  engagement_id CHAR(36) NOT NULL DEFAULT (UUID()),
  user_id CHAR(36) NOT NULL DEFAULT (UUID()),
  company_id CHAR(36) NOT NULL,
  report_id CHAR(36) NULL,

  engagement_name VARCHAR(255) NOT NULL,
  engagement_code VARCHAR(50) NOT NULL,

  audit_type ENUM('Full-scope IA','IFC','SOX') NOT NULL,
  reporting_currency JSON NOT NULL,
  audit_fy VARCHAR(10) NOT NULL,

  status ENUM(
    'Draft',
    'Confirmed',
    'Analysis_Running',
    'Analysis_Completed',
    'Locked'
  ) NOT NULL DEFAULT 'Draft',

  confirmed_at DATETIME NULL,
  confirmed_by CHAR(36) NULL,

  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,

  PRIMARY KEY (engagement_id),
  UNIQUE KEY uniq_engagement_code (engagement_code),
  INDEX idx_company (company_id)
) ENGINE=InnoDB;

CREATE TABLE engagement_context (
  engagement_context_id CHAR(36) NOT NULL DEFAULT (UUID()),
  engagement_id CHAR(36) NOT NULL,
  context_json JSON NOT NULL,
  st_dt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  e_dt DATETIME NOT NULL DEFAULT '9999-12-31',
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (engagement_context_id, st_dt),
  INDEX (engagement_id),
  INDEX (is_active)
) ENGINE=InnoDB;




-- =========================
-- Screen 2: BE / VA Lookups
-- =========================
CREATE TABLE be_dimension_master (
  -- sample data of be_dimension_master
  dimension_id CHAR(36) NOT NULL,
  dimension_name VARCHAR(100) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (dimension_id)
) ENGINE=InnoDB;



CREATE TABLE va_metric_group_master (
  -- sample data of va_metric_group_master
  metric_group_id CHAR(36) NOT NULL,
  group_name VARCHAR(100) NOT NULL, -- Profitability, Liquidity, Leverage
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (metric_group_id)
) ENGINE=InnoDB;



CREATE TABLE relevance_reason_master (
  -- sample data of relevance_reason_master
  reason_id CHAR(36) NOT NULL,
  reason_label VARCHAR(100) NOT NULL, -- Not applicable, Already mitigated, etc.
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (reason_id)
) ENGINE=InnoDB;



CREATE TABLE override_type_master (
  -- sample data of override_type_master
  override_type_id CHAR(36) NOT NULL,
  override_label VARCHAR(100) NOT NULL, -- Accept as-is, Modify risk, Modify likelihood, Re-interpret
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (override_type_id)
) ENGINE=InnoDB;



CREATE TABLE risk_theme_master (
  -- sample data of risk_theme_master
  risk_theme_id CHAR(36) NOT NULL,
  risk_theme_name VARCHAR(120) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (risk_theme_id)
) ENGINE=InnoDB;



CREATE TABLE risk_level_master (
  -- sample data of risk_level_master
  risk_level_id CHAR(36) NOT NULL,
  risk_level_label VARCHAR(20) NOT NULL, -- High / Medium / Low
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (risk_level_id)
) ENGINE=InnoDB;



-- =========================
-- Screen 2: Analysis Jobs
-- =========================
CREATE TABLE analysis_job (
  -- sample data of analysis_job
  job_id CHAR(36) NOT NULL ,
  engagement_id CHAR(36) NOT NULL,
  job_type ENUM('BE','VA') NOT NULL,
  status ENUM('Running','Completed','Failed','Partial') NOT NULL DEFAULT 'Running',
  started_at DATETIME NULL,
  completed_at DATETIME NULL,
  error_message TEXT NULL,

  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (job_id),
  INDEX idx_engagement (engagement_id),
  INDEX idx_job_type (job_type)
) ENGINE=InnoDB;



-- =========================
-- Screen 2: BE Insights
-- =========================
CREATE TABLE be_insight (
  -- sample data of be_insight
  be_insight_id CHAR(36) NOT NULL ,
  engagement_id CHAR(36) NOT NULL,
  dimension_id CHAR(36) NOT NULL,
  insight_title VARCHAR(255) NOT NULL,
  insight_statement TEXT NOT NULL,
  confidence_score DECIMAL(5,2) NOT NULL,

  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (be_insight_id),
  INDEX idx_be_engagement (engagement_id),
  INDEX idx_dimension (dimension_id)
) ENGINE=InnoDB;



CREATE TABLE be_insight_driver (
  -- sample data of be_insight_driver
  driver_id CHAR(36) NOT NULL ,
  be_insight_id CHAR(36) NOT NULL,
  driver_text VARCHAR(255) NOT NULL,

  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (driver_id),
  INDEX idx_be_insight (be_insight_id)
) ENGINE=InnoDB;



CREATE TABLE be_insight_validation (
  -- sample data of be_insight_validation
  be_validation_id CHAR(36) NOT NULL ,
  be_insight_id CHAR(36) NOT NULL,
  relevance_status ENUM('Relevant','Not Relevant') NOT NULL,
  not_relevant_reason_id CHAR(36) NULL,
  override_type_id CHAR(36) NULL,
  user_comment TEXT NULL,
  validated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (be_validation_id),
  UNIQUE KEY uniq_be_validation (be_insight_id),
  INDEX idx_be_valid (be_insight_id)
) ENGINE=InnoDB;



-- =========================
-- Screen 2: VA Insights
-- =========================
CREATE TABLE va_insight (
  -- sample data of va_insight
  va_insight_id CHAR(36) NOT NULL ,
  engagement_id CHAR(36) NOT NULL,
  metric_group_id CHAR(36) NOT NULL,
  metric_code VARCHAR(50) NOT NULL,
  insight_statement TEXT NOT NULL,
  confidence_score DECIMAL(5,2) NOT NULL,
  trend_direction VARCHAR(20) NULL,
  deviation_magnitude DECIMAL(12,2) NULL,

  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (va_insight_id),
  INDEX idx_va_engagement (engagement_id),
  INDEX idx_metric_group (metric_group_id)
) ENGINE=InnoDB;



CREATE TABLE va_insight_metric (
  -- sample data of va_insight_metric
  metric_id CHAR(36) NOT NULL ,
  va_insight_id CHAR(36) NOT NULL,
  metric_name VARCHAR(100) NOT NULL,
  current_value DECIMAL(18,4) NULL,
  prior_value DECIMAL(18,4) NULL,
  peer_median DECIMAL(18,4) NULL,
  unit VARCHAR(20) NULL,

  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (metric_id),
  INDEX idx_va_metric (va_insight_id)
) ENGINE=InnoDB;



CREATE TABLE va_insight_validation (
  -- sample data of va_insight_validation
  va_validation_id CHAR(36) NOT NULL ,
  va_insight_id CHAR(36) NOT NULL,
  relevance_status ENUM('Relevant','Not Relevant') NOT NULL,
  not_relevant_reason_id CHAR(36) NULL,
  override_type_id CHAR(36) NULL,
  user_comment TEXT NULL,
  validated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (va_validation_id),
  UNIQUE KEY uniq_va_validation (va_insight_id),
  INDEX idx_va_valid (va_insight_id)
) ENGINE=InnoDB;



-- =========================
-- Screen 2: Consolidated Risk Signals
-- =========================
CREATE TABLE consolidated_risk_signal (
  -- sample data of consolidated_risk_signal
  signal_id CHAR(36) NOT NULL ,
  engagement_id CHAR(36) NOT NULL,
  risk_theme_id CHAR(36) NOT NULL,
  system_score_id CHAR(36) NOT NULL,
  user_score_id CHAR(36) NOT NULL,
  trend_label VARCHAR(50) NULL,
  impact_note VARCHAR(255) NULL,

  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (signal_id),
  INDEX idx_signal_eng (engagement_id),
  INDEX idx_signal_theme (risk_theme_id)
) ENGINE=InnoDB;




-- =========================
-- Screen 3: Problem Statements
-- =========================
CREATE TABLE impact_type_master (
  -- sample data of impact_type_master
  impact_type_id CHAR(36) NOT NULL,
  impact_label VARCHAR(50) NOT NULL, -- Financial, Operational, etc.
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (impact_type_id)
) ENGINE=InnoDB;



CREATE TABLE time_horizon_master (
  -- sample data of time_horizon_master
  time_horizon_id CHAR(36) NOT NULL,
  horizon_label VARCHAR(50) NOT NULL, -- Immediate, Short-term, Long-term
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (time_horizon_id)
) ENGINE=InnoDB;



CREATE TABLE process_master (
  -- sample data of process_master
  process_id CHAR(36) NOT NULL,
  process_name VARCHAR(120) NOT NULL, -- Procurement, Inventory, etc.
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (process_id)
) ENGINE=InnoDB;



CREATE TABLE sub_process_master (
  -- sample data of sub_process_master
  sub_process_id CHAR(36) NOT NULL,
  process_id CHAR(36) NOT NULL,
  sub_process_name VARCHAR(150) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (sub_process_id),
  INDEX idx_sub_process (process_id)
) ENGINE=InnoDB;



CREATE TABLE problem_statement (
  -- sample data of problem_statement
  problem_statement_id CHAR(36) NOT NULL ,
  engagement_id CHAR(36) NOT NULL,
  risk_theme_id CHAR(36) NOT NULL,
  system_priority_id CHAR(36) NOT NULL,
  confidence_score DECIMAL(5,2) NOT NULL,
  statement_text TEXT NOT NULL,
  value_proposition TEXT NULL,
  status ENUM('Draft','Reviewed','Rejected') NOT NULL DEFAULT 'Draft',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (problem_statement_id),
  INDEX idx_ps_engagement (engagement_id),
  INDEX idx_ps_theme (risk_theme_id)
) ENGINE=InnoDB;



CREATE TABLE problem_statement_process_map (
  -- sample data of problem_statement_process_map
  map_id CHAR(36) NOT NULL ,
  problem_statement_id CHAR(36) NOT NULL,
  process_id CHAR(36) NOT NULL,

  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (map_id),
  UNIQUE KEY uniq_ps_process (problem_statement_id, process_id)
) ENGINE=InnoDB;



CREATE TABLE problem_statement_impact_map (
  -- sample data of problem_statement_impact_map
  map_id CHAR(36) NOT NULL ,
  problem_statement_id CHAR(36) NOT NULL,
  impact_type_id CHAR(36) NOT NULL,
  magnitude_level_id CHAR(36) NOT NULL,
  time_horizon_id CHAR(36) NOT NULL,

  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (map_id),
  UNIQUE KEY uniq_ps_impact (problem_statement_id, impact_type_id)
) ENGINE=InnoDB;



CREATE TABLE problem_statement_be_link (
  -- sample data of problem_statement_be_link
  link_id CHAR(36) NOT NULL ,
  problem_statement_id CHAR(36) NOT NULL,
  be_insight_id CHAR(36) NOT NULL,
  confidence_score DECIMAL(5,2) NULL,

  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (link_id),
  UNIQUE KEY uniq_ps_be (problem_statement_id, be_insight_id)
) ENGINE=InnoDB;



CREATE TABLE problem_statement_va_link (
  -- sample data of problem_statement_va_link
  link_id CHAR(36) NOT NULL ,
  problem_statement_id CHAR(36) NOT NULL,
  va_insight_id CHAR(36) NOT NULL,
  confidence_score DECIMAL(5,2) NULL,

  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (link_id),
  UNIQUE KEY uniq_ps_va (problem_statement_id, va_insight_id)
) ENGINE=InnoDB;



CREATE TABLE problem_statement_review (
  -- sample data of problem_statement_review
  review_id CHAR(36) NOT NULL ,
  problem_statement_id CHAR(36) NOT NULL,
  relevance_status ENUM('Accepted','Rejected') NOT NULL,
  rejection_reason TEXT NULL,
  priority_override_id CHAR(36) NULL,
  override_comment TEXT NULL,
  reviewed_at DATETIME DEFAULT CURRENT_TIMESTAMP,

  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (review_id),
  UNIQUE KEY uniq_ps_review (problem_statement_id)
) ENGINE=InnoDB;




-- =========================
-- Screen 4: IA Risk Universe
-- =========================
CREATE TABLE scope_override_reason_master (
  -- sample data of scope_override_reason_master
  reason_id CHAR(36) NOT NULL,
  reason_label VARCHAR(120) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (reason_id)
) ENGINE=InnoDB;



CREATE TABLE universe_template (
  -- sample data of universe_template
  template_id CHAR(36) NOT NULL ,
  template_name VARCHAR(150) NOT NULL,
  industry_sector_id CHAR(36) NULL,
  sub_industry_id CHAR(36) NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (template_id)
) ENGINE=InnoDB;



CREATE TABLE universe_template_process (
  -- sample data of universe_template_process
  template_process_id CHAR(36) NOT NULL ,
  template_id CHAR(36) NOT NULL,
  process_id CHAR(36) NOT NULL,

  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (template_process_id),
  UNIQUE KEY uniq_template_process (template_id, process_id)
) ENGINE=InnoDB;



CREATE TABLE universe_template_subprocess (
  -- sample data of universe_template_subprocess
  template_subprocess_id CHAR(36) NOT NULL ,
  template_process_id CHAR(36) NOT NULL,
  sub_process_id CHAR(36) NOT NULL,

  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (template_subprocess_id),
  UNIQUE KEY uniq_template_subprocess (template_process_id, sub_process_id)
) ENGINE=InnoDB;



CREATE TABLE engagement_process_universe (
  -- sample data of engagement_process_universe
  eng_process_id CHAR(36) NOT NULL ,
  engagement_id CHAR(36) NOT NULL,
  process_id CHAR(36) NOT NULL,
  inherent_risk_id CHAR(36) NOT NULL,
  system_recommended TINYINT(1) NOT NULL DEFAULT 1,
  final_in_scope TINYINT(1) NOT NULL DEFAULT 1,
  override_reason_id CHAR(36) NULL,
  rationale TEXT NULL,

  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (eng_process_id),
  UNIQUE KEY uniq_eng_process (engagement_id, process_id)
) ENGINE=InnoDB;



CREATE TABLE engagement_subprocess_universe (
  -- sample data of engagement_subprocess_universe
  eng_subprocess_id CHAR(36) NOT NULL ,
  engagement_id CHAR(36) NOT NULL,
  sub_process_id CHAR(36) NOT NULL,
  inherent_risk_id CHAR(36) NOT NULL,
  system_recommended TINYINT(1) NOT NULL DEFAULT 1,
  final_in_scope TINYINT(1) NOT NULL DEFAULT 1,
  override_reason_id CHAR(36) NULL,
  rationale TEXT NULL,

  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (eng_subprocess_id),
  UNIQUE KEY uniq_eng_subprocess (engagement_id, sub_process_id)
) ENGINE=InnoDB;



CREATE TABLE engagement_process_problem_map (
  -- sample data of engagement_process_problem_map
  map_id CHAR(36) NOT NULL ,
  engagement_id CHAR(36) NOT NULL,
  process_id CHAR(36) NOT NULL,
  problem_statement_id CHAR(36) NOT NULL,

  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (map_id),
  UNIQUE KEY uniq_eng_proc_ps (engagement_id, process_id, problem_statement_id)
) ENGINE=InnoDB;




-- =========================
-- Screen 5: Audit Plan
-- =========================
CREATE TABLE audit_frequency_master (
  -- sample data of audit_frequency_master
  frequency_id CHAR(36) NOT NULL,
  frequency_label VARCHAR(50) NOT NULL, -- Annual, 18m, 2-year
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (frequency_id)
) ENGINE=InnoDB;



CREATE TABLE audit_plan_type_master (
  -- sample data of audit_plan_type_master
  plan_type_id CHAR(36) NOT NULL,
  plan_type_label VARCHAR(50) NOT NULL, -- Full-scope, Follow-up
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (plan_type_id)
) ENGINE=InnoDB;



CREATE TABLE audit_area (
  -- sample data of audit_area
  audit_area_id CHAR(36) NOT NULL ,
  engagement_id CHAR(36) NOT NULL,
  audit_area_name VARCHAR(150) NOT NULL,
  scope_description TEXT NULL,
  inherent_risk_id CHAR(36) NOT NULL,
  system_suggested_frequency_id CHAR(36) NULL,
  final_frequency_id CHAR(36) NULL,
  plan_type_id CHAR(36) NULL,
  planned_period VARCHAR(30) NULL,
  planned_start DATE NULL,
  planned_end DATE NULL,
  assigned_team VARCHAR(255) NULL,
  locations TEXT NULL,
  dependencies TEXT NULL,
  rationale TEXT NULL,

  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (audit_area_id),
  INDEX idx_audit_area_eng (engagement_id)
) ENGINE=InnoDB;



CREATE TABLE audit_area_process_map (
  -- sample data of audit_area_process_map
  map_id CHAR(36) NOT NULL ,
  audit_area_id CHAR(36) NOT NULL,
  process_id CHAR(36) NOT NULL,

  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (map_id),
  UNIQUE KEY uniq_audit_area_process (audit_area_id, process_id)
) ENGINE=InnoDB;



CREATE TABLE audit_area_subprocess_map (
  -- sample data of audit_area_subprocess_map
  map_id CHAR(36) NOT NULL ,
  audit_area_id CHAR(36) NOT NULL,
  eng_subprocess_id CHAR(36) NOT NULL,

  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (map_id),
  UNIQUE KEY uniq_audit_area_subprocess (audit_area_id, eng_subprocess_id)
) ENGINE=InnoDB;



CREATE TABLE audit_plan_status (
  -- sample data of audit_plan_status
  engagement_id CHAR(36) NOT NULL,
  status ENUM('Draft','Sent','Approved','Locked') NOT NULL DEFAULT 'Draft',
  locked_at DATETIME NULL,
  approved_at DATETIME NULL,

  is_active TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (engagement_id)
) ENGINE=InnoDB;


