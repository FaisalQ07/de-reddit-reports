import io
import os
import praw
import pytz
import pprint
import pandas as pd
import requests

from time import sleep
from google.cloud import storage
from datetime import datetime, timedelta
from prawcore.exceptions import PrawcoreException

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

POST_FIELDS = (
    "id",
    "title",
    "score",
    "num_comments",
    "author",
    "created_utc",
    "url",
    "upvote_ratio",
    "over_18",
    "edited",
    "spoiler",
    "stickied",
    'selftext'
)

COMMENT_FIELDS = [
    "id",
    "body",
    "author",
    "created_utc",
    "score",
    "edited",
    "stickied",
    "parent_id",
    "permalink"
]

COMMENT_FIELDS_DF = [
    "id",
    "body",
    "author",
    "created_utc",
    "score",
    "edited",
    "stickied",
    "parent_id",
    "post_id",
    "num_replies",
    "permalink"
]

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/src/keys/de-reddit-reports-f9479aba34a3.json"

bucket_name = 'reddit-terra-bucket'

@data_loader
def load_data_from_api(*args, **kwargs):
    """
    Template for loading data from API
    """
    
    # Read metadata
    metadata_df = read_metadata(bucket_name, **kwargs)
    # Check if metadata_df is empty
    if not metadata_df.empty:
        # Fetch the last run time
        last_run_date = metadata_df['extraction_end_date'].iloc[0]
    else:
        # If metadata_df is empty, set last_run_date to current time minus 7 days and convert to local timezone (toronto)
        last_run_date = convert_to_local_time(datetime.now() - timedelta(days=1))

    
    # Extract Reddit posts and comments 
    posts, comments = extract_reddit_data(last_run_date, **kwargs)

     # Create DataFrame for posts
    posts_df = pd.DataFrame(posts, columns=POST_FIELDS)
    # Convert 'edited' column to boolean (True or False) or NaN
    posts_df['edited'] = posts_df['edited'].notna()
    # Create DataFrame for comments
    comments_df = pd.DataFrame(comments, columns=COMMENT_FIELDS_DF)
    # Convert 'edited' column to boolean (True or False) or NaN
    comments_df['edited'] = comments_df['edited'].notna()

    print('posts_df count: {0}\t comments_df count: {1}'.format(len(posts_df), len(comments_df)))

     # Write DataFrames to Parquet files and upload to GCS bucket
    today = kwargs['execution_date']
    submission_name = kwargs['sub_reddit']
    post_path = f'subreddit/{submission_name}/post/{today.year}/{today.month}/{today.day}/post.parquet'
    comment_path = f'subreddit/{submission_name}/comment/{today.year}/{today.month}/{today.day}/comment.parquet'

    write_dataframe_to_gcs(posts_df, 'post', bucket_name, post_path)
    write_dataframe_to_gcs(comments_df, 'comment', bucket_name, comment_path)


    # Calculate total posts and comments
    total_posts = len(posts_df)
    total_comments = len(comments_df)
    # Update extraction_end_date to the maximum created_utc in posts_df
    if not posts_df.empty:
        extraction_end_date = convert_to_local_time(datetime.utcfromtimestamp(posts_df['created_utc'].max()))
     # Update metadata_df
    metadata_df = pd.DataFrame({
        'pipeline_run_date': [convert_to_local_time(kwargs['execution_date'])],  # Add pipeline run date to metadata
        'extraction_start_date': [last_run_date],
        'extraction_end_date': [extraction_end_date],
        'total_posts': [total_posts],
        'total_comments': [total_comments]
    })

    write_metadata(bucket_name, metadata_df, **kwargs)

    return metadata_df


def write_dataframe_to_gcs(dataframe, dataframe_type, bucket_name, destination_path):
    file_name = f"temp_{dataframe_type}.parquet"
    try:
        client = storage.Client()
        bucket = client.get_bucket(bucket_name)
        blob = bucket.blob(destination_path)
        if blob.exists():
            # If the file exists, delete it
            blob.delete()
        # Convert DataFrame to bytes
        dataframe_bytes = dataframe.to_parquet(None, engine='pyarrow', index=False)
        # Upload bytes to GCS blob
        
        with open(file_name, "wb") as f:
            f.write(dataframe_bytes)
        with open(file_name, "rb") as f:
            blob.upload_from_file(f, content_type='application/octet-stream')
        print(f"DataFrame successfully written to '{destination_path}' in bucket '{bucket_name}'.")
    except Exception as e:
        print(f"Error writing DataFrame to '{destination_path}' in bucket '{bucket_name}': {e}")
    finally:
        # Clean up temporary file
        if os.path.exists(file_name):
            os.remove(file_name)
        else:
            print(f"File '{file_name}' does not exist.")


def write_metadata(bucket_name, metadata_df, **kwargs):
     # Define the filename with interpolation
    file_name = "temp_metadata.parquet"
    try:
        client = storage.Client()
        bucket = client.get_bucket(bucket_name)
        submission = kwargs['sub_reddit']
        blob = bucket.blob(f"subreddit/{submission}/metadata/metadata.parquet")
        if blob.exists():
            # If the file exists, delete it. We only keep metadata of last run
            blob.delete()
        
        # Convert DataFrame to bytes
        metadata_bytes = metadata_df.to_parquet(None, engine='pyarrow', index=False)
        
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
        if os.path.exists(file_name):
            os.remove(file_name)
        else:
            print(f"File '{file_name}' does not exist.")


def read_metadata(bucket_name, **kwargs):
    try:
        client = storage.Client()
        bucket = client.get_bucket(bucket_name)
        submission_name = kwargs['sub_reddit']
        blob = bucket.blob(f"subreddit/{submission_name}/metadata/metadata.parquet")
        with open("temp_metadata.parquet", "wb") as file_obj_post:
            blob.download_to_file(file_obj_post)
        # Read the downloaded Parquet file into a DataFrame
        metadata_df = pd.read_parquet("temp_metadata.parquet")
        return metadata_df
    except Exception as e:
        print("Error reading metadata:", e)
        # If metadata file doesn't exist or cannot be read, return None
        return pd.DataFrame(columns=['last_run_date', 'extraction_start_date', 'extraction_end_date' 'total_posts', 'total_comments'])
    finally:
        os.remove('temp_metadata.parquet')



def convert_to_local_time(utc_datetime):
    # Get the timezone for Toronto
    toronto_timezone = pytz.timezone('America/Toronto')
    # Convert UTC datetime to Toronto local time
    toronto_datetime = utc_datetime.astimezone(toronto_timezone)
    return toronto_datetime


def extract_reddit_data(last_run_date, **kwargs):
    try:
        # get instance of reddit api using praw
        reddit = reddit_api_connect()

        subreddit = reddit.subreddit(kwargs['sub_reddit'])
        posts = []
        comments = []
        # Get the timestamp for today at midnight (00:00:00)
        today_midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        print('start_date: {} \t end_date: {}'.format(last_run_date, today_midnight))

        # Extract posts and comments between last run date and up to today midnight (00:00:00)
        submission_count = 1
        for submission in subreddit.hot(limit=50):
            print('sleep for 1 sec')
            sleep(1)
            if last_run_date.timestamp() < submission.created_utc < today_midnight.timestamp():
                # Append the submission to the 'posts' list
                print(f'appending submission: {submission_count}')
                post_data = {field: getattr(submission, field) for field in POST_FIELDS}
                # Convert author to string to handle Redditor objects
                post_data['author'] = str(post_data['author'])
                posts.append(post_data)
                # Fetch all comments for the submission
                submission.comments.replace_more(limit=None)
                for comment in submission.comments.list():
                    # Check if the comment's creation time is after the last run date and before today at midnight
                    if last_run_date.timestamp() < comment.created_utc < today_midnight.timestamp():
                        comment_data = {field: getattr(comment, field) for field in COMMENT_FIELDS}
                        # Convert author to string to handle Redditor objects
                        comment_data['author'] = str(comment_data['author'])
                        # Calculate the number of replies 
                        num_replies = sum(1 for _ in comment.replies.list())
                        comment_data["num_replies"] = num_replies
                        # Append post_id separately as it's not available in comment object directly
                        comment_data["post_id"] = comment.submission.id
                        comments.append(comment_data)
                submission_count += 1

        return posts, comments
    except PrawcoreException as e:
        print(f"An error occurred while extracting Reddit data: {e}")
        # Can handle the error further, log it, or raise it again if needed
        raise e


def reddit_api_connect():
    """Create and return an instance of reddit api"""
    REDDIT_APP_NAME = os.getenv("REDDIT_APP_NAME")
    REDDIT_APP_ID = os.getenv("REDDIT_APP_ID")
    REDDIT_SECRET = os.getenv("REDDIT_SECRET")

    try:
       instance = praw.Reddit(
            client_id=REDDIT_APP_ID, 
            client_secret=REDDIT_SECRET, 
            user_agent="My User Agent"
        )
    except Exception as e:
        print(f"Unable to connect to Reddit API for instantiation. Error: {e}")
        sys.exit(1) 
    return instance


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
