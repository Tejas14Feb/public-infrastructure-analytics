-- =====================================================================
-- 03_service_users.sql
-- Creates service users for the pipeline. Keys are attached separately.
-- Run as SECURITYADMIN. Safe to rerun.
-- In Snowsight, set the role picker to SECURITYADMIN before running.
--
-- After running, attach each public key once with:
--   alter user <user> set rsa_public_key = '<key>';
-- Keys live in ~/.snowflake/keys/ and are never committed.
-- =====================================================================

use role securityadmin;

create user if not exists loader_svc
    type = service
    default_role = loader
    default_warehouse = analytics_wh
    comment = 'Service user for the ingestion script';

create user if not exists dbt_svc
    type = service
    default_role = transformer
    default_warehouse = analytics_wh
    comment = 'Service user for dbt';

grant role loader to user loader_svc;
grant role transformer to user dbt_svc;