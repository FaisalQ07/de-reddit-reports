#!/usr/bin/env python
# coding: utf-8

import subprocess

# Install textblob library using pip
subprocess.call(['pip', 'install', 'textblob'])

import argparse
import pyspark
from pyspark.sql import SparkSession

from pyspark.sql import functions as F
import pyspark.sql.types as T
from textblob import TextBlob

parser = argparse.ArgumentParser()
parser.add_argument('--input_date', required=True)
parser.add_argument('--input_subreddit', required=True)
args = parser.parse_args()
input_date = args.input_date
input_subreddit = args.input_subreddit

spark = SparkSession.builder \
    .appName('test') \
    .getOrCreate()

df_post = spark.read.parquet(f'gs://reddit-terra-bucket/subreddit/{input_subreddit}/post/{input_date}/post.parquet')
df_comment = spark.read.parquet(f'gs://reddit-terra-bucket/subreddit/{input_subreddit}/comment/{input_date}/comment.parquet')

# Define UDF for sentiment analysis to return sentiment score only
def analyze_sentiment_score(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity

# Register UDF
sentiment_score_udf = F.udf(analyze_sentiment_score, T.FloatType())

def count_checksum_verification(posts_df, comments_df, joined_df):
    try:
        # Count the number of posts before the join
        posts_count_before = posts_df.count()

        # Count the number of comments before the join
        comments_count_before = comments_df.count()

        # Count the number of distinct non-null values in the 'post_id' column
        posts_count_after = joined_df.filter(joined_df['post_id'].isNotNull()).select(F.col("post_id")).distinct().count()

        # Count the number of distinct non-null values in the 'comment_id' column
        comments_count_after = joined_df.filter(joined_df['comment_id'].isNotNull()).select(F.col("comment_id")).distinct().count()

        # Perform count checksum verification
        if posts_count_before == posts_count_after and comments_count_before == comments_count_after:
            print("Count checksum verification passed.")
            return True
    except Exception as e:
        print("Error occurred during count checksum verification:", str(e))
        print("Count checksum verification failed.\ncomments_count_before:{0}\tcomments_count_after:{1} \
            \nposts_count_before:{2}\tposts_count_after:{3}" 
                  .format(comments_count_before, comments_count_after,posts_count_before, posts_count_after)
             )
    return False

# Apply UDF to create column for post sentiment score
df_post_with_sentiment = df_post.withColumn("post_sentiment_score", sentiment_score_udf(df_post["selftext"]))

# Derive post sentiment label based on sentiment score
df_post_with_sentiment = (
    df_post_with_sentiment
    .withColumn("post_sentiment_label",
                F.when(df_post_with_sentiment["post_sentiment_score"] > 0, "positive")
                .when(df_post_with_sentiment["post_sentiment_score"] < 0, "negative")
                .otherwise("neutral")
               )
    .withColumn("post_created_utc", 
               F.from_unixtime(F.col("created_utc")).cast(T.TimestampType())
              )
)

# Apply UDF to create column for comment sentiment score
df_comment_with_sentiment = df_comment.withColumn("comment_sentiment_score", sentiment_score_udf(df_comment["body"]))

# Derive commet sentiment label based on sentiment score
df_comment_with_sentiment = (
    df_comment_with_sentiment
    .withColumn("comment_sentiment_label",
                F.when(df_comment_with_sentiment["comment_sentiment_score"] > 0, "positive")
                .when(df_comment_with_sentiment["comment_sentiment_score"] < 0, "negative")
                .otherwise("neutral")
               )
    .withColumn("comment_created_utc", 
                F.from_unixtime(F.col("created_utc")).cast(T.TimestampType())
               )
)

# Join posts and comments dataframes
df_joined = (
    df_post_with_sentiment
    .join(df_comment_with_sentiment
          , df_post_with_sentiment.id == df_comment_with_sentiment.post_id
          , "left_outer"
         )
)

result_df = df_joined.select(
    df_post_with_sentiment["id"].alias("post_id"),
    df_post_with_sentiment["title"],
    df_post_with_sentiment["score"],
    df_post_with_sentiment["num_comments"],
    df_post_with_sentiment["author"].alias("post_author"),
    df_post_with_sentiment["post_created_utc"],
    df_post_with_sentiment["url"],
    df_post_with_sentiment["upvote_ratio"],
    df_post_with_sentiment["over_18"],
    df_post_with_sentiment["edited"],
    df_post_with_sentiment["spoiler"],
    df_post_with_sentiment["stickied"],
    df_post_with_sentiment["selftext"],
    df_post_with_sentiment["post_sentiment_score"],
    df_post_with_sentiment["post_sentiment_label"],
    df_comment_with_sentiment["id"].alias("comment_id"),
    df_comment_with_sentiment["body"].alias("comment_body"),
    df_comment_with_sentiment["author"].alias("comment_author"),
    df_comment_with_sentiment["comment_created_utc"],
    df_comment_with_sentiment["score"].alias("comment_score"),
    df_comment_with_sentiment["edited"].alias("comment_edited"),
    df_comment_with_sentiment["stickied"].alias("comment_stickied"),
    df_comment_with_sentiment["parent_id"].alias("comment_parent_id"),
    df_comment_with_sentiment["num_replies"].alias("comment_num_replies"),
    df_comment_with_sentiment["permalink"],
    df_comment_with_sentiment["comment_sentiment_score"],
    df_comment_with_sentiment["comment_sentiment_label"]
)

count_verification_result = count_checksum_verification(df_post_with_sentiment, df_comment_with_sentiment, result_df)

if count_verification_result:
    (
        result_df
        .write
        .partitionBy("post_id")
        .parquet(f'gs://reddit-terra-bucket/subreddit/{input_subreddit}/staging/post_comment/{input_date}/post_comment.parquet', mode='overwrite')
    )





