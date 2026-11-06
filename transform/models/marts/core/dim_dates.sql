with date_spine as (

    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="cast('2018-10-01' as date)",
        end_date="cast('2027-10-01' as date)"
    ) }}

)

select
    date_day,
    year(date_day)                                    as calendar_year,
    month(date_day)                                   as calendar_month,
    monthname(date_day)                               as month_name,
    year(date_day) + iff(month(date_day) >= 10, 1, 0) as fiscal_year,
    ceil((mod(month(date_day) + 2, 12) + 1) / 3)      as fiscal_quarter
from date_spine