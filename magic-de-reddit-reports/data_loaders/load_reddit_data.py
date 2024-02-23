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
        last_run_date = metadata_df['last_run_date'].iloc[0]
    else:
        # If metadata_df is empty, set last_run_date to current time minus 7 days and convert to local timezone (toronto)
        last_run_date = convert_to_local_time(datetime.now() - timedelta(days=7))

    print('last_run_date: {}'.format(last_run_date))

    # Extract Reddit posts and comments 
    posts, comments = extract_reddit_data(last_run_date, **kwargs)

     # Create DataFrame for posts
    posts_df = pd.DataFrame(posts, columns=POST_FIELDS)
    # Convert 'edited' column to boolean (True or False) or NaN
    posts_df['edited'] = posts_df['edited'].notna()
    # Create DataFrame for comments
    comments_df = pd.DataFrame(comments, columns=COMMENT_FIELDS)
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

    return metadata_df


def write_dataframe_to_gcs(dataframe, dataframe_type, bucket_name, destination_path):
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
        with open("temp.parquet", "wb") as f:
            f.write(dataframe_bytes)
        with open("temp.parquet", "rb") as f:
            blob.upload_from_file(f, content_type='application/octet-stream')
        print(f"DataFrame successfully written to '{destination_path}' in bucket '{bucket_name}'.")
    except Exception as e:
        print(f"Error writing DataFrame to '{destination_path}' in bucket '{bucket_name}': {e}")


def write_metadata(bucket_name, metadata_df):
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob('subreddit/metadata/metadata.parquet')
    metadata_df.to_parquet(blob, overwrite=True)


def read_metadata(bucket_name, **kwargs):
    try:
        client = storage.Client()
        bucket = client.get_bucket(bucket_name)
        submission_name = kwargs['sub_reddit']
        blob = bucket.blob(f"subreddit/{submission_name}/metadata/metadata.parquet")
        metadata_df = pd.read_parquet(blob)
        return metadata_df
    except Exception as e:
        print("Error reading metadata:", e)
        # If metadata file doesn't exist or cannot be read, return None
        return pd.DataFrame(columns=['last_run_date', 'extraction_start_date', 'extraction_end_date' 'total_posts', 'total_comments'])


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
        if reddit:
            print('reddit_api_connect() success')

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
