with awards as (

    select * from {{ ref('stg_usaspending__awards') }}

),

latest as (

    -- Award staging has one row per award, state, and fiscal year.
    -- Keep the most recent version of each award: the latest fiscal year,
    -- then the latest fetch within it.
    select *
    from awards
    qualify row_number() over (
        partition by award_key
        order by fiscal_year desc, extracted_at desc
    ) = 1

)

select
    award_key,
    award_id,
    recipient_name,
    awarding_agency,
    award_type,
    award_amount,
    start_date,
    state_code  as latest_state_code,
    fiscal_year as latest_reported_fiscal_year
from latest