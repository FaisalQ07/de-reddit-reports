import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime,timedelta

import sys
sys.path.append('/home/src/magic-de-reddit-reports')
from data_loaders.load_reddit_data import (
    extract_reddit_data,
    write_dataframe_to_gcs,
    write_metadata,
    read_metadata,
    convert_to_local_time,
    reddit_api_connect
)

class TestLoadRedditData(unittest.TestCase):
    
    @patch('data_loaders.load_reddit_data.reddit_api_connect')
    def test_extract_reddit_data(self, mock_reddit_api_connect):
        # Mocking the subreddit and submission
        mock_subreddit = mock_reddit_api_connect.subreddit.return_value
        mock_submission = mock_subreddit.hot.return_value
        mock_submission.__iter__.return_value = []

        last_run_date = datetime.now() - timedelta(days=1)
        sub_reddit = 'test_subreddit'
        kwargs = {'sub_reddit': sub_reddit}
        # Calling the function
        posts, comments = extract_reddit_data(last_run_date, **kwargs)
        # Assertions
        self.assertIsInstance(posts, list)
        self.assertIsInstance(comments, list)


    def test_convert_to_local_time(self):
        utc_datetime = datetime(2024, 3, 18, 12, 0, 0)
        # Call the function
        local_datetime = convert_to_local_time(utc_datetime)
        # Define the expected timezone
        expected_timezone = 'America/Toronto'
         # Assert that the timezone of the returned datetime matches the expected timezone
        self.assertEqual(local_datetime.tzinfo.zone, expected_timezone)
        self.assertEqual(local_datetime.year, 2024)
        self.assertEqual(local_datetime.month, 3)
        self.assertEqual(local_datetime.day, 18)
        self.assertEqual(local_datetime.hour, 8)  # Adjusted to Toronto time

    @patch('data_loaders.load_reddit_data.storage.Client')
    def test_write_dataframe_to_gcs(self, mock_storage_client):
        # Mocking client, bucket, and blob
        mock_client = MagicMock()
        mock_storage_client.return_value = mock_client
        mock_bucket = MagicMock()
        mock_client.get_bucket.return_value = mock_bucket
        mock_blob = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        # mock input args
        mock_dataframe = pd.DataFrame({
            'Post_id': ['12ab', '34cd', '56ef'],
            'post_author': ['A', 'B', 'C'],
            'post_score': [4, 7, 9]
        })
        mock_dataframe_type = 'post'
        mock_destination_path = MagicMock()
        bucket_name = 'test-bucket'
        # call the function 
        write_dataframe_to_gcs(mock_dataframe, mock_dataframe_type, mock_destination_path, bucket_name=bucket_name)
        # Assert the expected method calls
        mock_client.get_bucket.assert_called_once_with(bucket_name)
        mock_bucket.blob.assert_called_once_with(mock_destination_path)


    @patch('data_loaders.load_reddit_data.storage.Client')
    @patch('data_loaders.load_reddit_data.pd.read_parquet')
    def test_read_metadata(self, mock_read_parquet, mock_client):
        # Mocking client, bucket, and blob
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_client.return_value.get_bucket.return_value = mock_bucket
        # Mocking DataFrame returned by pd.read_parquet
        expected_df = MagicMock()
        mock_read_parquet.return_value = expected_df
        # Call the function
        metadata_df = read_metadata(bucket_name='test_bucket', sub_reddit='test_subreddit')
        # Assertions
        self.assertEqual(metadata_df, expected_df)
    
    @patch('data_loaders.load_reddit_data.praw.Reddit')
    def test_reddit_api_connect(self, mock_praw_reddit):
        # Mock Reddit instance
        instance_mock = MagicMock()
        mock_praw_reddit.return_value = instance_mock
        #Call the function
        instance_returned = reddit_api_connect()
        self.assertEqual(instance_returned, instance_mock)
    
    @patch('data_loaders.load_reddit_data.storage')
    def test_write_metadata(self, mock_storage):
        # Mock the necessary objects
        mock_client = MagicMock()
        mock_storage.Client.return_value = mock_client
        mock_bucket = MagicMock()
        mock_client.get_bucket.return_value = mock_bucket
        mock_blob = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        # Define test data
        metadata_df = MagicMock()  # Provide test DataFrame
        bucket_name = "test_bucket"
        sub_reddit = "test_subreddit"
        # Call the function
        write_metadata(metadata_df, bucket_name=bucket_name, sub_reddit=sub_reddit)
        # Assert the expected method calls
        mock_storage.Client.assert_called_once()
        mock_client.get_bucket.assert_called_once_with(bucket_name)

    




        