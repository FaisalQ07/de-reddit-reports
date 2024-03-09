{{
    config(
        materialized='incremental',
        unique_key=['post_id', 'comment_id'],
        on_schema_change='sync_all_columns',
        incremental_strategy='merge'
    )
}}


select * 
from {{ source('staging', 'dataengineering_staging') }} 



