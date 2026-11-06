with awards as (

    select * from {{ ref('int_usaspending__awards_latest') }}

),

transaction_awards as (

    select
        award_key,
        max(award_id)   as award_id,
        max(award_type) as award_type
    from {{ ref('stg_usaspending__transactions') }}
    group by award_key

),

inferred as (

    -- Inferred members: awards that appear in transactions but not in the
    -- award search, so every transaction can join to an award row
    select transaction_awards.*
    from transaction_awards
    left join awards
        on transaction_awards.award_key = awards.award_key
    where awards.award_key is null

)

select
    award_key,
    award_id,
    recipient_name,
    awarding_agency,
    award_type,
    award_amount,
    start_date,
    latest_state_code,
    latest_reported_fiscal_year,
    true as is_in_award_search
from awards

union all

select
    award_key,
    award_id,
    null  as recipient_name,
    null  as awarding_agency,
    award_type,
    null  as award_amount,
    null  as start_date,
    null  as latest_state_code,
    null  as latest_reported_fiscal_year,
    false as is_in_award_search
from inferred