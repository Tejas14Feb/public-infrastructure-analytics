-- =====================================================================
-- 04_resource_monitor.sql
-- Caps monthly credit usage across the whole account.
-- Run as ACCOUNTADMIN (only ACCOUNTADMIN can manage resource monitors).
-- In Snowsight, set the role picker to ACCOUNTADMIN before running.
-- =====================================================================

use role accountadmin;

create resource monitor if not exists monthly_credit_cap
    with credit_quota = 40
    frequency = monthly
    start_timestamp = immediately
    triggers
        on 50 percent do notify
        on 75 percent do notify
        on 90 percent do suspend
        on 100 percent do suspend_immediate;

alter account set resource_monitor = monthly_credit_cap;