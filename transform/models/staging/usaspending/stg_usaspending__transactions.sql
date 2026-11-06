with source as (

    select * from {{ source('usaspending', 'transactions') }}

),

renamed as (

    select
        record:"generated_internal_id"::string          as award_key,
        record:"Award ID"::string                       as award_id,
        record:"Mod"::string                            as modification_number,
        record:"Action Date"::date                      as action_date,
        record:"Transaction Amount"::number(18, 2)      as transaction_amount,
        record:"Recipient Name"::string                 as recipient_name,
        record:"Recipient UEI"::string                  as recipient_uei,
        record:"Awarding Agency"::string                as awarding_agency,
        record:"Awarding Sub Agency"::string            as awarding_sub_agency,
        record:"Award Type"::string                     as award_type_description,
        record:"Assistance Listing":cfda_number::string as assistance_listing_number,
        record:"Assistance Listing":cfda_title::string  as assistance_listing_title,
        record:"_state"::string                         as state_code,
        record:"_fiscal_year"::integer                  as fiscal_year,
        record:"_award_type"::string                    as award_type,
        record:"_extracted_at"::timestamp_tz            as extracted_at,
        source_file,
        loaded_at

    from source

),

latest_snapshot as (

    -- Each file is a complete, reconciled snapshot of one state, fiscal year,
    -- and award type. Keep only rows from the most recent snapshot of each slice.
    select *
    from renamed
    qualify extracted_at = max(extracted_at) over (
        partition by state_code, fiscal_year, award_type
    )

),

numbered as (

    -- Some transactions are identical in every available field but are real,
    -- separate amounts. Number them so every row can get a unique key.
    select
        *,
        row_number() over (
            partition by award_key, modification_number, action_date, transaction_amount
            order by source_file
        ) as occurrence_number
    from latest_snapshot

)

select
    {{ dbt_utils.generate_surrogate_key([
        'award_key',
        'modification_number',
        'action_date',
        'transaction_amount',
        'occurrence_number'
    ]) }} as transaction_key,
    *
from numbered