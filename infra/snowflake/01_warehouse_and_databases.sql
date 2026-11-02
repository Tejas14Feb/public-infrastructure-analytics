-- =====================================================================
-- 01_warehouse_and_databases.sql
-- Creates compute and storage for public-infrastructure-analytics.
-- Run as SYSADMIN. Safe to rerun: every statement uses IF NOT EXISTS.
-- In Snowsight, set the role picker to SYSADMIN before running.
-- =====================================================================

use role sysadmin;

-- Compute -------------------------------------------------------------

create warehouse if not exists analytics_wh
    warehouse_size = 'XSMALL'
    auto_suspend = 60
    auto_resume = true
    initially_suspended = true
    comment = 'Compute for loading and transforming project data';

-- Storage -------------------------------------------------------------

create database if not exists raw
    comment = 'Data exactly as received from source APIs';

create schema if not exists raw.usaspending
    comment = 'Raw USAspending award data';

create database if not exists analytics_dev
    comment = 'Development area for dbt models';

create database if not exists analytics
    comment = 'Production dbt models read by the dashboard';
