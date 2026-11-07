with transactions as (

    select * from {{ ref('fct_transactions') }}

),

agencies as (

    select * from {{ ref('dim_agencies') }}

),

by_sector_year as (

    select
        transactions.fiscal_year,
        agencies.sector,
        sum(transactions.transaction_amount) as net_obligations
    from transactions
    join agencies
        on transactions.awarding_sub_agency = agencies.awarding_sub_agency
    group by 1, 2

),

current_fiscal_year as (

    select year(current_date) + iff(month(current_date) >= 10, 1, 0) as fiscal_year

)

select
    by_sector_year.fiscal_year,
    by_sector_year.sector,
    by_sector_year.net_obligations,

    -- The infrastructure bill was signed in November 2021, at the start of FY2022
    iff(by_sector_year.fiscal_year <= 2021, 'Before', 'After') as bill_period,

    lag(by_sector_year.net_obligations) over (
        partition by by_sector_year.sector
        order by by_sector_year.fiscal_year
    ) as prior_year_obligations,

    round(
        100 * (by_sector_year.net_obligations - prior_year_obligations)
        / nullif(prior_year_obligations, 0),
        1
    ) as pct_change_from_prior_year,

    -- The current fiscal year is still in progress, and agencies report late
    by_sector_year.fiscal_year >= current_fiscal_year.fiscal_year as is_partial_year

from by_sector_year
cross join current_fiscal_year