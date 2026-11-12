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

    -- Share of the contract money that went out in this state and year.
    -- The base is positive net obligations only, because recipients with a
    -- net negative (deobligations) would shrink the total and inflate shares.
    -- Recipients with zero or negative net get no share (null).
    round(
        100 * iff(net_obligations > 0, net_obligations, null)
        / nullif(
            sum(iff(net_obligations > 0, net_obligations, 0))
                over (partition by state_code, fiscal_year),
            0
        ),
        1
    ) as market_share_pct,

    rank() over (
        partition by state_code, fiscal_year
        order by net_obligations desc
    ) as rank_in_state_year

from by_recipient

