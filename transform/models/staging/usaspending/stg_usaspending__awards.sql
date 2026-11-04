with source as (

    select * from {{ source('usaspending', 'awards') }}

),

renamed as (

    select
        record:"generated_internal_id"::string as award_key,
        record:"Award ID"::string              as award_id,
        record:"Recipient Name"::string        as recipient_name,
        record:"Awarding Agency"::string       as awarding_agency,
        record:"Award Amount"::number(18, 2)   as award_amount,
        record:"Start Date"::date              as start_date,
        record:"_state"::string                as state_code,
        record:"_fiscal_year"::integer         as fiscal_year,
        record:"_award_type"::string           as award_type,
        record:"_extracted_at"::timestamp_tz   as extracted_at,
        source_file,
        loaded_at

    from source

),

deduplicated as (

    select *
    from renamed
    qualify row_number() over (
        partition by award_key, state_code, fiscal_year
        order by extracted_at desc
    ) = 1

)

select * from deduplicated