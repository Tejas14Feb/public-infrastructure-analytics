select
    awarding_sub_agency,
    sector,
    'Department of Transportation' as awarding_agency
from {{ ref('agency_sectors') }}