import os 
if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def export_data(data, *args, **kwargs):
    """
    Exports data to some source.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Output (optional):
        Optionally return any object and it'll be logged and
        displayed when inspecting the block run.
    """
    # Specify your data exporting logic here

    # Define the command as a string
command = """
gcloud dataproc jobs submit pyspark \
    --cluster=de-reddit-reports-cluster \
    --region=northamerica-northeast1 \
    --project=de-reddit-reports \
    gs://reddit-terra-bucket/subreddit/dataengineering/code/transform_bigquery.py \
    -- \
    --input_date=2024/2/24 \
    --input_subreddit=dataengineering
"""

# Execute the command
os.system(command)


