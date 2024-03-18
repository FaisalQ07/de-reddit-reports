import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime

import sys
sys.path.append('/home/src/magic-de-reddit-reports')
from data_loaders.load_reddit_data import load_data_from_api, convert_to_local_time

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
        