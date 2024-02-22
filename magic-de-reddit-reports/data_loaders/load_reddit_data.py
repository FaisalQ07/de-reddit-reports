import io
import os
import praw
import pprint
import pandas as pd
import requests

from time import sleep

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

POST_FIELDS = (
    "id",
    "title",
    "score",
    "num_comments",
    "author",
    "created_utc",
    "url",
    "upvote_ratio",
    "over_18",
    "edited",
    "spoiler",
    "stickied",
)

@data_loader
def load_data_from_api(*args, **kwargs):
    """
    Template for loading data from API
    """
    
    reddit_instance = reddit_api_connect()
    if reddit_instance:
        print('reddit_api_connect() success')
    subreddit_posts_object = subreddit_posts(reddit_instance, **kwargs)
    if subreddit_posts_object:
        print('subreddit_posts() success')
    reddit_df = extract_subreddit_data(subreddit_posts_object)

    
    # response = requests.get(url)

    return reddit_df

def reddit_api_connect():
    """Create and return an instance of reddit api"""
    REDDIT_APP_NAME = os.getenv("REDDIT_APP_NAME")
    REDDIT_APP_ID = os.getenv("REDDIT_APP_ID")
    REDDIT_SECRET = os.getenv("REDDIT_SECRET")

    try:
       instance = praw.Reddit(
            client_id=REDDIT_APP_ID, 
            client_secret=REDDIT_SECRET, 
            user_agent="My User Agent"
        )
    except Exception as e:
        print(f"Unable to connect to Reddit API for instantiation. Error: {e}")
        sys.exit(1) 
    return instance

def subreddit_posts(reddit_instance, **kwargs):
    """Return posts object of sub_reddit"""
    try:
        subreddit = reddit_instance.subreddit(kwargs['sub_reddit'])
        posts = subreddit.top(time_filter=kwargs['time_filter'])
        return posts
    except Exception as e:
        print(f"There's been an issue. Error: {e}")
        sys.exit(1)

def extract_subreddit_data(subreddit_posts_object):
    """
    Function iterates through the subreddit posts. 
    Extract the fields as key-value pair and return a dataframe containing posts for the hour
    Args:
        subreddit_posts_object: subreddit posts object
    Return:
        reddit_df: Dataframe containing custom fields defined in POST_FIELDS
    """
    list_of_posts = []
    try:
        for post in subreddit_posts_object:
            sleep(6)
            post_dict = vars(post)
            pprint.pprint(post_dict)
            break
            # subreddit_dict = {field: post_dict[field] for field in POST_FIELDS}
            # subreddit_dict["author"] = str(subreddit_dict["author"])
            # list_of_posts.append(subreddit_dict)
        
        # reddit_df = pd.DataFrame(list_of_posts)
    except Exception as e:
        print(f"There has been an issue while parsing the subreddit. Error {e}")
        sys.exit(1)
    return #reddit_df



@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
