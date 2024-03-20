import unittest
from unittest.mock import patch, MagicMock

import sys
sys.path.append('/home/src/magic-de-reddit-reports')
from data_loaders.load_metadata_from_gcs import (
    load_from_google_cloud_storage
)

class TestLoadMetadataFromGcs(unittest.TestCase):
    @patch('data_loaders.load_metadata_from_gcs.get_repo_path')
    @patch('data_loaders.load_metadata_from_gcs.ConfigFileLoader')
    @patch('data_loaders.load_metadata_from_gcs.GoogleCloudStorage')
    def test_load_from_google_cloud_storage(self, mock_gcs, mock_config_loader, mock_get_repo_path):
        # Mock the return values and behavior of the dependencies
        mock_get_repo_path.return_value = '/path/to/repo'
        mock_config_loader.return_value = MagicMock()
        # Mock the with_config method to return a MagicMock
        mock_with_config = MagicMock()
        mock_gcs.with_config.return_value = mock_with_config

        # Create a custom MagicMock instance with 'date' attribute
        mock_df = MagicMock()

        mock_gcs.load.return_value = (
            # Sample DataFrame for testing
           mock_df
        )

        # Call the function with sample arguments
        df, run_date = load_from_google_cloud_storage(bucket_name='test_bucket', sub_reddit='test_subreddit')

        # Assert that the expected methods were called with the correct arguments
        mock_get_repo_path.assert_called_once()
        mock_config_loader.assert_called_once_with('/path/to/repo/io_config.yaml', 'default')
        mock_gcs.with_config.assert_called_once_with(mock_config_loader.return_value)
        # mock_gcs.load.assert_called_once_with('test_bucket', 'subreddit/test_subreddit/metadata/metadata.parquet')

        # Assert the return values
        self.assertIsInstance(df, MagicMock)  # Assert that df is a DataFrame or mock equivalent