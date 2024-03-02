import os
if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def export_data(data, *args, **kwargs):
    """
    Exports the joined posts and comments data from GCS bucket to BigQuery dataset.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Output (optional):
        Optionally return any object and it'll be logged and
        displayed when inspecting the block run.
    """
    bucket_name = kwargs['bucket_name']
    sub_reddit = kwargs['sub_reddit']
    run_date = data[1]
    print(f"Running data proc for {run_date}")

    command = f"""
    gcloud dataproc jobs submit pyspark \
        --cluster=de-reddit-reports-cluster \
        --region=northamerica-northeast1 \
        --project=de-reddit-reports \
        gs://{bucket_name}/subreddit/{sub_reddit}/code/transform_bigquery.py \
        -- \
        --input_date={run_date} \
        --input_subreddit={sub_reddit}
"""

    # Execute the command
    os.system(command)


