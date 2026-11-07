-- Every raw file must be loaded exactly once.
-- A second COPY of the same file duplicates all of its rows, and
-- occurrence_number would hide the duplicates from the unique tests downstream.
select
    source_file,
    count(distinct loaded_at) as load_count
from {{ source('usaspending', 'transactions') }}
group by source_file
having count(distinct loaded_at) > 1
