import os
import pytz
import pandas as pd
from google.cloud import storage
from datetime import datetime, timedelta


if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/src/keys/de-reddit-reports-f9479aba34a3.json"

bucket_name = 'reddit-terra-bucket'
object_key_post = 'subreddit/dataengineering/post/2024/2/24/post.parquet'
object_key_comment = 'subreddit/dataengineering/comment/2024/2/24/comment.parquet'

@data_loader
def load_data(*args, **kwargs):
    """
    Template code for loading data from any source.

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
# Specify your data loading logic here

    # Initialize Google Cloud Storage client
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    # Get the blob (object) from the bucket
    blob_post = bucket.blob(object_key_post)
    blob_comment = bucket.blob(object_key_comment)
    # Download the data from the blob to a file object
    with open("temp_post.parquet", "wb") as file_obj_post:
        blob_post.download_to_file(file_obj_post)
    with open("temp_comment.parquet", "wb") as file_obj_comment:
        blob_comment.download_to_file(file_obj_comment)
    # Read the downloaded Parquet file into a DataFrame
    post_df = pd.read_parquet("temp_post.parquet")
    post_df['created_utc'] = pd.to_datetime(post_df['created_utc'], unit='s')


    comment_df = pd.read_parquet("temp_comment.parquet")
    comment_df['created_utc'] = pd.to_datetime(comment_df['created_utc'], unit='s')

    print(kwargs['execution_date'])

    # total_posts = len(post_df)
    # total_comments = len(comment_df)
    # Update last_run_date to the maximum created_utc in posts_df
    # if not post_df.empty:
    #     last_run_date = convert_to_local_time(post_df['created_utc'].max())
    # # Update metadata_df
    # metadata_df = pd.DataFrame({
    #     'last_run_date': [last_run_date],
    #     'extraction_start_date': [last_run_date - timedelta(days=7)],
    #     'extraction_end_date': [last_run_date],
    #     'total_posts': [total_posts],
    #     'total_comments': [total_comments],
    #     'pipeline_run_date': [kwargs['execution_date']- timedelta(days=1)]  # Add pipeline run date to metadata
    # })

    # write_metadata(bucket_name, metadata_df)
        
    blob_metadata = bucket.blob(f"subreddit/dataengineering/metadata/metadata.parquet")
    # Download the data from the blob to a file object
    with open("temp_metadata.parquet", "wb") as file_obj_post:
        blob_metadata.download_to_file(file_obj_post)
    # Read the downloaded Parquet file into a DataFrame
    metadata_df = pd.read_parquet("temp_metadata.parquet")
    # # Print the first 5 rows
    # # print(post_df.info())   
    # os.remove('temp_post.parquet')
    # os.remove('temp_comment.parquet')
    # os.remove('temp_metadata.parquet')
    return post_df, comment_df, metadata_df


def write_metadata(bucket_name, metadata_df):
    try:
        client = storage.Client()
        bucket = client.get_bucket(bucket_name)
        blob = bucket.blob('subreddit/dataengineering/metadata/metadata.parquet')
        if blob.exists():
            # If the file exists, delete it. We only keep metadata of last run
            blob.delete()
        
        # Convert DataFrame to bytes
        metadata_bytes = metadata_df.to_parquet(None, engine='pyarrow', index=False)
        
         # Define the filename with interpolation
        file_name = "temp_metadata.parquet"
        
        # Write DataFrame bytes to a local file
        with open(file_name, "wb") as f:
            f.write(metadata_bytes)
        
        # Upload bytes to GCS blob
        with open(file_name, "rb") as f:
            blob.upload_from_file(f, content_type='application/octet-stream')
        
        print(f"Metadata DataFrame successfully written to 'subreddit/metadata/metadata.parquet' in bucket '{bucket_name}'.")
    except Exception as e:
        print(f"Error writing metadata DataFrame to 'subreddit/metadata/metadata.parquet' in bucket '{bucket_name}': {e}")
    finally:
        # Clean up temporary file
        os.remove(file_name)


def convert_to_local_time(utc_datetime):
    # Get the timezone for Toronto
    utc_datetime = utc_datetime.tz_localize('UTC')
    
    # Get the timezone for Toronto
    toronto_timezone = pytz.timezone('America/Toronto')
    # Convert UTC datetime to Toronto local time
    toronto_datetime = utc_datetime.astimezone(toronto_timezone)
    return toronto_datetime


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
