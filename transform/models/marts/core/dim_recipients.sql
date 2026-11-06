with transactions as (

    select * from {{ ref('stg_usaspending__transactions') }}
    where recipient_uei is not null

),

recipients as (

    -- One name per UEI is expected, but pick deterministically to be safe
    select
        recipient_uei,
        recipient_name
    from transactions
    qualify row_number() over (
        partition by recipient_uei
        order by action_date desc, recipient_name
    ) = 1

)

select
    recipient_uei,
    recipient_name
from recipients

union all

-- Unknown member: transactions with no UEI
select
    'UNKNOWN'           as recipient_uei,
    'Unknown recipient' as recipient_name