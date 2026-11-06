with transactions as (

    select * from {{ ref('stg_usaspending__transactions') }}

)

select
    -- Primary key
    transaction_key,

    -- Foreign keys to dimensions
    award_key,
    coalesce(recipient_uei, 'UNKNOWN')          as recipient_uei,
    awarding_sub_agency,
    coalesce(assistance_listing_number, 'NONE') as assistance_listing_number,
    state_code,
    action_date,

    -- Attributes of the transaction itself
    fiscal_year,
    award_type,
    modification_number,
    coalesce(try_to_number(modification_number) = 0, false) as is_original_action,

    -- Measure
    transaction_amount

from transactions