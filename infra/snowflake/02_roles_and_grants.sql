-- =====================================================================
-- 02_roles_and_grants.sql
-- Creates project roles with least-privilege access.
-- Run as SECURITYADMIN. Safe to rerun.
-- In Snowsight, set the role picker to SECURITYADMIN before running.
-- =====================================================================

use role securityadmin;

-- Roles ---------------------------------------------------------------

create role if not exists loader
    comment = 'Loads raw data from source APIs into RAW';

create role if not exists transformer
    comment = 'Runs dbt: reads RAW, builds models in ANALYTICS_DEV and ANALYTICS';

-- Roll both roles up to SYSADMIN, and give them to my user
grant role loader to role sysadmin;
grant role transformer to role sysadmin;
grant role loader to user tejasb;
grant role transformer to user tejasb;

-- LOADER: write access to raw data only -------------------------------

grant usage on warehouse analytics_wh to role loader;
grant usage on database raw to role loader;
grant usage on schema raw.usaspending to role loader;
grant create table on schema raw.usaspending to role loader;
grant create stage on schema raw.usaspending to role loader;

-- TRANSFORMER: read raw data, build models ----------------------------

grant usage on warehouse analytics_wh to role transformer;

grant usage on database raw to role transformer;
grant usage on schema raw.usaspending to role transformer;
grant select on all tables in schema raw.usaspending to role transformer;
grant select on future tables in schema raw.usaspending to role transformer;

grant usage on database analytics_dev to role transformer;
grant create schema on database analytics_dev to role transformer;

grant usage on database analytics to role transformer;
grant create schema on database analytics to role transformer;