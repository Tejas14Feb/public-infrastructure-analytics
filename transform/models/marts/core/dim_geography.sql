select
    state_code,
    state_name
from {{ ref('states') }}