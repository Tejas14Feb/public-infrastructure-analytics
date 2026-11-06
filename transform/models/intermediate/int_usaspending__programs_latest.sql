with transactions as (

    select * from {{ ref('stg_usaspending__transactions') }}
    where assistance_listing_number is not null

),

latest_title as (

    -- A program number can carry several titles over time (20.106 had four).
    -- Keep the title from the program's most recent transaction.
    select
        assistance_listing_number,
        assistance_listing_title
    from transactions
    qualify row_number() over (
        partition by assistance_listing_number
        order by action_date desc, assistance_listing_title
    ) = 1

)

select * from latest_title