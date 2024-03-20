{{
    config(
        materialized='incremental',
        unique_key=['post_id', 'comment_id'],
        on_schema_change='sync_all_columns',
        incremental_strategy='merge'
    )
}}

with source_data as (
    select * 
    from {{ source('staging', 'dataengineering_staging') }}
)
select *
from source_data s
where comment_id is not null
or not exists (
    select 1
    from reddit_dataset.reddit_data_consolidated t
    where t.post_id = s.post_id
)




