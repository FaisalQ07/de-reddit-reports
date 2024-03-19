import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime

import sys
sys.path.append('/home/src/magic-de-reddit-reports')
from data_loaders.load_reddit_data import load_data_from_api, convert_to_local_time, read_metadata

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
        