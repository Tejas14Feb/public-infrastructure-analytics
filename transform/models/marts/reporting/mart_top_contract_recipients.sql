with transactions as (

    select * from {{ ref('fct_transactions') }}
    where award_type = 'contracts'

),

recipients as (

    select * from {{ ref('dim_recipients') }}

),

by_recipient as (

    select
        transactions.fiscal_year,
        transactions.state_code,
        transactions.recipient_uei,
        recipients.recipient_name,
        count(*)                                 as transactions,
        count(distinct transactions.award_key)   as awards,
        sum(transactions.transaction_amount)     as net_obligations
    from transactions
    join recipients
        on transactions.recipient_uei = recipients.recipient_uei
    group by 1, 2, 3, 4

)

select
    *,
    round(
        100 * net_obligations
        / nullif(sum(net_obligations) over (partition by state_code, fiscal_year), 0),
        1
    ) as market_share_pct,
    rank() over (
        partition by state_code, fiscal_year
        order by net_obligations desc
    ) as rank_in_state_year
from by_recipient