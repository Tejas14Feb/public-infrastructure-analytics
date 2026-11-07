-- Every raw awards file must be loaded exactly once.
-- A second COPY of the same file duplicates all of its rows downstream.
select
    source_file,
    count(distinct loaded_at) as load_count
from {{ source('usaspending', 'awards') }}
group by source_file
having count(distinct loaded_at) > 1
