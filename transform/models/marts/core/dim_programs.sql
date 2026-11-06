with programs as (

    select * from {{ ref('int_usaspending__programs_latest') }}

)

select
    assistance_listing_number,
    assistance_listing_title
from programs

union all

-- Unknown member: contracts have no assistance listing
select
    'NONE'                  as assistance_listing_number,
    'No program (contract)' as assistance_listing_title