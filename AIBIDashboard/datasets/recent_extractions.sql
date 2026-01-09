-- Recent Extractions Dataset
-- Latest lease documents processed

SELECT 
    lease_id,
    CONCAT(tenant_name, '_lease.pdf') as filename,
    validation_status,
    base_rent_psf,
    verified_at
FROM ${catalog}.${schema}.silver_leases
WHERE tenant_name IS NOT NULL
ORDER BY verified_at DESC
LIMIT 10
