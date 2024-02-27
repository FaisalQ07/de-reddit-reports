import os
from pyspark.sql import SparkSession

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@data_loader
def load_data(*args, **kwargs):
    """
    Template code for loading data from any source.

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    # Specify your data loading logic here
    spark = SparkSession.builder.master(os.getenv('SPARK_MASTER_HOST', 'local')).getOrCreate()
    # Create some sample data
    data = [("John", 25), ("Alice", 30), ("Bob", 35)]

    # Define the schema for the DataFrame
    schema = ["Name", "Age"]

    # Create a DataFrame
    df = spark.createDataFrame(data, schema)


    return df


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
