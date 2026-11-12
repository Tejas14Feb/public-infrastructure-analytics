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

with_previous_row as (

    select
        fiscal_year,
        sector,
        net_obligations,
        lag(fiscal_year) over (
            partition by sector
            order by fiscal_year
        ) as previous_row_fiscal_year,
        lag(net_obligations) over (
            partition by sector
            order by fiscal_year
        ) as previous_row_obligations
    from by_sector_year

),

current_fiscal_year as (

    select year(current_date) + iff(month(current_date) >= 10, 1, 0) as fiscal_year

)

select
    with_previous_row.fiscal_year,
    with_previous_row.sector,
    with_previous_row.net_obligations,

    -- The infrastructure bill was signed in November 2021, at the start of FY2022
    iff(with_previous_row.fiscal_year <= 2021, 'Before', 'After') as bill_period,

    -- lag() returns the previous row, which skips years with no spending.
    -- Only use it when that row is exactly the prior fiscal year; otherwise null.
    iff(
        with_previous_row.previous_row_fiscal_year = with_previous_row.fiscal_year - 1,
        with_previous_row.previous_row_obligations,
        null
    ) as prior_year_obligations,

    round(
        100 * (with_previous_row.net_obligations - prior_year_obligations)
        / nullif(prior_year_obligations, 0),
        1
    ) as pct_change_from_prior_year,

    -- The current fiscal year is still in progress, and agencies report late
    with_previous_row.fiscal_year >= current_fiscal_year.fiscal_year as is_partial_year

from with_previous_row
cross join current_fiscal_year