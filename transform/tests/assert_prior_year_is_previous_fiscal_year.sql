-- prior_year_obligations must come from exactly fiscal_year - 1.
-- When that year has no row for the sector, it must be null.
-- Returns offending rows; any row fails the test.

select
    current_year.sector,
    current_year.fiscal_year,
    current_year.prior_year_obligations
from {{ ref('mart_spending_trends') }} as current_year
left join {{ ref('mart_spending_trends') }} as previous_year
    on previous_year.sector = current_year.sector
    and previous_year.fiscal_year = current_year.fiscal_year - 1
where current_year.prior_year_obligations is not null
    and (
        previous_year.fiscal_year is null
        or current_year.prior_year_obligations != previous_year.net_obligations
    )