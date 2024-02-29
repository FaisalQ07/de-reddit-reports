import pyspark
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader


credentials_location = '/home/src/keys/de-reddit-reports-f9479aba34a3.json'


@data_loader
def load_data(*args, **kwargs):
    """
    Template code for loading data from any source.

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    # Specify your data loading logic here

    # Stop any existing Spark session
    SparkSession.builder.appName("Test Spark").getOrCreate().stop()

    conf = SparkConf() \
    .setMaster('local') \
    .setAppName('Test Spark') \
    .set("spark.jars", "/home/src/lib/gcs-connector-hadoop3-2.2.5.jar") \
    .set("spark.hadoop.google.cloud.auth.service.account.enable", "true") \
    .set("spark.hadoop.google.cloud.auth.service.account.json.keyfile", credentials_location)
    
    spark = (
        SparkSession
        .builder
        .config(conf=conf)
        .config("spark.driver.extraClassPath", "/home/src/lib/gcs-connector-hadoop3-2.2.5.jar")
        .config("spark.executor.extraClassPath", "/home/src/lib/gcs-connector-hadoop3-2.2.5.jar")
        .appName('Test Spark')
        .getOrCreate()
    )
    hadoop_conf = spark._jsc.hadoopConfiguration()

    hadoop_conf.set("fs.AbstractFileSystem.gs.impl",  "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS")
    hadoop_conf.set("fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem")
    hadoop_conf.set("fs.gs.auth.service.account.json.keyfile", credentials_location)
    hadoop_conf.set("fs.gs.auth.service.account.enable", "true")

    kwargs['context']['spark'] = spark

    spark_created = kwargs['context']['spark']
    active_spark_session_name = spark.conf.get("spark.app.name")
    print(f'active_spark_session_name: {active_spark_session_name}')

    # return df


# @test

# def test_output(output, *args) -> None:
#     """
#     Template code for testing the output of the block.
#     """
#     assert output is not None, 'The output is undefined'
