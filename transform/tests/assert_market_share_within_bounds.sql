-- market_share_pct must be between 0 and 100, and the shares within one
-- state and fiscal year must add up to at most 100, allowing for rounding.
-- Returns offending state-years; any row fails the test.

with shares_by_state_year as (

    select
        state_code,
        fiscal_year,
        count(market_share_pct) as recipients_with_share,
        min(market_share_pct) as min_share,
        max(market_share_pct) as max_share,
        sum(market_share_pct) as total_share
    from {{ ref('mart_top_contract_recipients') }}
    group by 1, 2

)

select *
from shares_by_state_year
where min_share < 0
    or max_share > 100
    or total_share > 100 + 0.05 * recipients_with_share