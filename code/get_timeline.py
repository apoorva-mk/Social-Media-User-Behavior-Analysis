import tweepy
from dateutil import parser

FRIEND_COUNT = 5
MIN_FOLLOWER_COUNT = 5
MAX_FOLLOWER_COUNT = 100000
FAVOURITE_COUNT = 5
STATUSES_COUNT = 5

START_DATE = 'Jan 1 0:0:0 +0000 2020'
start_date = parser.parse(START_DATE)


def check_optimal(twitter_user):
    """ checking if the given user is suitable for obtaining tweets """

    if twitter_user._json["protected"]:
        return False

    if twitter_user._json["verified"]:
        return False

    if twitter_user._json["followers_count"] < MIN_FOLLOWER_COUNT or twitter_user._json["followers_count"] > MAX_FOLLOWER_COUNT:
        return False

    if twitter_user._json["friends_count"] < FRIEND_COUNT:
        return False

    if twitter_user._json["favourites_count"] < FAVOURITE_COUNT:
        return False

    if twitter_user._json["statuses_count"] < STATUSES_COUNT:
        return False

    return True
    

def user_timeline(api, twitter_user):
    """ To get the tweets from a user's timeline """
    tweets = []
    retweets = []
    replies = []

    if check_optimal(twitter_user): 
        for status in tweepy.Cursor(api.user_timeline, id=twitter_user._json["id"]).items():
            tweet_date = parser.parse(status._json["created_at"])

            """ Only saving tweets upto a certain time """
            if tweet_date < start_date:
                break

            if status._json["in_reply_to_screen_name"] != None:
                replies.append(status._json)

            elif status._json["retweeted"]:
                retweets.append(status._json)

            else:
                tweets.append(status._json)

    return tweets, retweets, replies

