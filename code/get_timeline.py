import tweepy
import pymongo
import os
import data_scraper
import time

from dateutil import parser

# Some user related details
FRIEND_COUNT = 5
MIN_FOLLOWER_COUNT = 5
MAX_FOLLOWER_COUNT = 100000
FAVOURITE_COUNT = 5
STATUSES_COUNT = 5

START_DATE = 'Jan 1 0:0:0 +0000 2020'
start_date = parser.parse(START_DATE)

# mongo db collection names
client = pymongo.MongoClient("mongodb://localhost:27017/")
DATABASE = "twitter_database"
TWEETS_COL = "tweets_collection"
RETWEETS_COL = "retweets_collection"
REPLIES_COL = "replies_collection"

# store twitter API credentials
KEY = os.getenv('key')
SECRET_KEY = os.getenv('secret_key')
ACCESS_TOKEN = os.getenv('access_token')
ACCESS_TOKEN_SECRET = os.getenv('access_token_secret')

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
        for status in tweepy.Cursor(api.user_timeline, id=twitter_user._json["id"], monitor_rate_limit=True, wait_on_rate_limit=True).items():
            tweet_date = parser.parse(status._json["created_at"])

            """ Only saving tweets upto a certain time """
            if tweet_date < start_date:
                break

            if status._json["in_reply_to_screen_name"] != None:
                replies.append(status._json)

            elif hasattr(status,"retweeted_status"):
                retweets.append(status._json)

            else:
                tweets.append(status._json)

    return tweets, retweets, replies


def main():
    userfile = "users1.txt"
    tweetfile = "tweets1.csv"
    retweetfile = "retweets1.csv"
    replyfile = "replies1.csv"

    ufile = open(userfile, 'r')
    twfile = open(tweetfile, "w")
    rtfile = open(retweetfile, "w")
    repfile = open(replyfile, "w")

    # Storing in MongoDB database
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = client[DATABASE]
    tweets_col = mydb[TWEETS_COL]
    retweets_col = mydb[RETWEETS_COL]
    replies_col = mydb[REPLIES_COL]

    tweets_col.drop()
    retweets_col.drop()
    replies_col.drop()

    user_lines = ufile.readlines() 
    api = data_scraper.get_twitter_auth_api(KEY, SECRET_KEY)
    user_num = 0
    for line in user_lines:
        user_num = user_num+1
        if user_num%50==0:
            print("Saving statuses for user number: ", user_num)

        while True:
            try: 
                twitter_user = api.get_user(line)
                break
            except tweepy.TweepError:
                print("Sleeping for 15 minutes...while fetching user details")
                time.sleep(15*60)

        tweets, retweets, replies = user_timeline(api, twitter_user)

        for tweet in tweets:
            try:
                tweet["_id"] = tweet["id_str"]
                tweets_col.insert_one(tweet)
                text = tweet["text"]
                text = text.replace('\r',' ')
                text = text.replace('\n',' ')
                lang = "en"
                if hasattr(tweet, "lang"):
                    lang = tweet["lang"]
                twfile.write(str(tweet["id"])+","+str(tweet["created_at"])+","+text+","+str(tweet["user"]["id"])+","+lang+"\n")
            except pymongo.errors.DuplicateKeyError:
                print("Tweet already saved")
            
        for retweet in retweets:
            try:
                retweet["_id"] = retweet["id_str"]
                retweets_col.insert_one(retweet)
                text = retweet["text"]
                text = text.replace('\r',' ')
                text = text.replace('\n',' ')
                lang = "en"
                if hasattr(retweet, "lang"):
                    lang = retweet["lang"]
                rtfile.write(str(retweet["id"])+","+str(retweet["created_at"])+","+text+","+str(retweet["user"]["id"])+","+lang+"\n")
            except pymongo.errors.DuplicateKeyError:
                print("Retweet already saved")

        for reply in replies:
            try:
                reply["_id"] = reply["id_str"]
                replies_col.insert_one(reply)
                text = reply["text"]
                text = text.replace('\r',' ')
                text = text.replace('\n',' ')
                lang = "en"
                if hasattr(reply, "lang"):
                    lang = reply["lang"]
                repfile.write(str(reply["id"])+","+str(reply["created_at"])+","+text+","+str(reply["user"]["id"])+","+lang+"\n")
            except pymongo.errors.DuplicateKeyError:
                print("Reply already saved")

if __name__ == "__main__":
    main()