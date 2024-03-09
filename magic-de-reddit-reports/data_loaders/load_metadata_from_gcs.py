import os
import datetime
import pandas as pd

from mage_ai.settings.repo import get_repo_path
from mage_ai.io.config import ConfigFileLoader
from mage_ai.io.google_cloud_storage import GoogleCloudStorage
from os import path
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@data_loader
def load_from_google_cloud_storage(*args, **kwargs):
    """
    Template for loading data from a Google Cloud Storage bucket.
    Specify your configuration settings in 'io_config.yaml'.

    Docs: https://docs.mage.ai/design/data-loading#googlecloudstorage
    """
    config_path = path.join(get_repo_path(), 'io_config.yaml')
    config_profile = 'default'

    bucket_name = kwargs['bucket_name']
    sub_reddit = kwargs['sub_reddit']
    object_key = f'subreddit/{sub_reddit}/metadata/metadata.parquet'

    # read metadata file as pandas dataframe

    df =  GoogleCloudStorage.with_config(ConfigFileLoader(config_path, config_profile)).load(
        bucket_name,
        object_key,
    )

    # extract pipeline run date
    df['pipeline_run_date_new'] = (
        df['pipeline_run_date'].dt.strftime('%Y/%-m/%-d')
    )

    run_date = df['pipeline_run_date_new'].iloc[0]

    return df, run_date


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
