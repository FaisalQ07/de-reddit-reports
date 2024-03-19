import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime

import sys
sys.path.append('/home/src/magic-de-reddit-reports')
from data_loaders.load_reddit_data import (
    load_data_from_api,
    convert_to_local_time,
    read_metadata,
    reddit_api_connect,
    write_metadata
)

class TestLoadRedditData(unittest.TestCase):
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
        #call reddit_api_connect()
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



        