import unittest
from unittest.mock import patch, MagicMock

import sys
sys.path.append('/home/src/magic-de-reddit-reports')

from data_exporters.export_reddit_data_from_gcs_to_bq import export_data

class TestDataExporter(unittest.TestCase):

    @patch('data_exporters.export_reddit_data_from_gcs_to_bq.os.system')
    def test_export_data(self, mock_os_system):
        # Define test data
        data = [None, '2024-3-20']  
        bucket_name = 'test_bucket'
        sub_reddit = 'test_subreddit'

        # Call the function with mock arguments
        export_data(data, bucket_name=bucket_name, sub_reddit=sub_reddit)

        # Construct the expected command
        expected_command = f"""
    gcloud dataproc jobs submit pyspark \
        --cluster=de-reddit-reports-cluster \
        --region=northamerica-northeast1 \
        --project=de-reddit-reports \
        gs://{bucket_name}/subreddit/{sub_reddit}/code/transform_bigquery.py \
        -- \
        --input_date={data[1]} \
        --input_subreddit={sub_reddit}
    """

        # Assert that os.system was called with the expected command
        mock_os_system.assert_called_once_with(expected_command)

