with transactions as (

    select * from {{ ref('fct_transactions') }}

),

agencies as (

    select * from {{ ref('dim_agencies') }}

),

geography as (

    select * from {{ ref('dim_geography') }}

)

select
    transactions.fiscal_year,
    transactions.state_code,
    geography.state_name,
    agencies.sector,
    count(*)                                                        as transactions,
    sum(transactions.transaction_amount)                            as net_obligations,
    sum(iff(transactions.award_type = 'grants', transactions.transaction_amount, 0))    as grant_obligations,
    sum(iff(transactions.award_type = 'contracts', transactions.transaction_amount, 0)) as contract_obligations
from transactions
join agencies
    on transactions.awarding_sub_agency = agencies.awarding_sub_agency
join geography
    on transactions.state_code = geography.state_code
group by 1, 2, 3, 4