%sql
-- FIXED VERSION: Only process raw records that haven't been extracted yet
-- This prevents duplicate insertions into bronze_leases

INSERT INTO ${CATALOG}.${SCHEMA}.bronze_leases (
  uploaded_at, landlord_name, landlord_address, tenant_name, tenant_address, 
  industry_sector, suite_number, lease_type, commencement_date, expiration_date, 
  term_months, rentable_square_feet, annual_base_rent, base_rent_psf, 
  annual_escalation_pct, renewal_notice_days, guarantor, 
  property_address, property_street_address, property_city, property_state, 
  property_zip_code, property_country, 
  raw_json_payload, is_fully_extracted, validation_status
)
WITH agent_raw_output AS (
  SELECT 
    raw.file_path,
    raw.raw_parsed_json AS input,
    raw.ingested_at AS source_uploaded_at,
    ai_query(
      'kie-c4f6b62e-endpoint',
      raw.raw_parsed_json,
      failOnError => false
    ) AS response
  FROM ${CATALOG}.${SCHEMA}.raw_leases raw
  -- CRITICAL FIX: Only process files that haven't been extracted to bronze yet
  WHERE NOT EXISTS (
    SELECT 1 
    FROM ${CATALOG}.${SCHEMA}.bronze_leases bronze
    WHERE bronze.uploaded_at = raw.ingested_at
  )
  -- Process up to 20 NEW records at a time
  LIMIT 20 
),
parsed_results AS (
  SELECT
    source_uploaded_at,
    from_json(
      CAST(response.result AS STRING),
      '
      landlord STRUCT<name: STRING, address: STRING>,
      tenant STRUCT<name: STRING, address: STRING, industry_sector: STRING>,
      property_location STRUCT<full_address: STRING, street_address: STRING, city: STRING, state: STRING, zip_code: STRING, country: STRING>,
      lease_details STRUCT<suite_number: STRING, lease_type: STRING, commencement_date: DATE, expiration_date: DATE, term_months: INT, rentable_square_feet: INT>,
      financial_terms STRUCT<annual_base_rent: INT, monthly_base_rent: DOUBLE, base_rent_psf: DOUBLE, annual_escalation_pct: INT, additional_rent_estimate: DOUBLE, pro_rata_share: DOUBLE, security_deposit: INT>,
      risk_and_options STRUCT<renewal_options: STRING, renewal_notice_days: INT, termination_rights: STRING, guarantor: STRING>
      '
    ) as r,
    response.result as raw_json
  FROM agent_raw_output
  WHERE response.errorMessage IS NULL
)
SELECT
  source_uploaded_at,
  r.landlord.name,
  r.landlord.address,
  r.tenant.name,
  r.tenant.address,
  r.tenant.industry_sector,
  r.lease_details.suite_number,
  r.lease_details.lease_type,
  r.lease_details.commencement_date,
  r.lease_details.expiration_date,
  r.lease_details.term_months,
  r.lease_details.rentable_square_feet,
  r.financial_terms.annual_base_rent,
  r.financial_terms.base_rent_psf,
  r.financial_terms.annual_escalation_pct,
  r.risk_and_options.renewal_notice_days,
  r.risk_and_options.guarantor,
  r.property_location.full_address,
  r.property_location.street_address,
  r.property_location.city,
  r.property_location.state,
  r.property_location.zip_code,
  r.property_location.country,
  raw_json,
  CASE 
    WHEN r.tenant.name IS NULL OR r.financial_terms.annual_base_rent IS NULL THEN FALSE 
    ELSE TRUE 
  END as is_fully_extracted,
  'NEW' as validation_status
FROM parsed_results;