if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader



@data_loader
def load_data(*args, **kwargs):
    """
    Template code for loading data from any source.

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    # Specify your data loading logic here
    spark_reddit = kwargs['context']['spark']
    spark_mage = kwargs['spark']
    # Fetch the name of the active Spark session
    active_spark_session_name_reddit = spark_reddit.conf.get("spark.app.name")
    active_spark_session_name_mage = spark_mage.conf.get("spark.app.name")

    print("Active Spark session name reddit:", active_spark_session_name_reddit)
    print("Active Spark session name mage:", active_spark_session_name_mage)
    print('class path spark reddit {}'.format(spark_reddit.sparkContext.getConf().get("spark.driver.extraClassPath")))
    print('class path spark mage {}'.format(spark_mage.sparkContext.getConf().get("spark.driver.extraClassPath")))

    df_post = (
        spark_reddit.read
        .parquet('gs://reddit-terra-bucket/subreddit/dataengineering/post/2024/2/24/post.parquet')
    )
    
    print(df_post.count())


