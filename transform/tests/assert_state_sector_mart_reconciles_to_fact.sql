-- Fails if the state-sector mart's total differs from the fact table's total,
-- which would mean the joins dropped or duplicated dollars.
with mart as (

    select sum(net_obligations) as total
    from {{ ref('mart_spending_by_state_sector') }}

),

fact as (

    select sum(transaction_amount) as total
    from {{ ref('fct_transactions') }}

)

select
    mart.total as mart_total,
    fact.total as fact_total
from mart
cross join fact
where mart.total <> fact.total