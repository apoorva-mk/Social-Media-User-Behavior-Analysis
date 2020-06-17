import tweepy
import os
import pymongo
import json
import time
import pprint

from dotenv import load_dotenv
from get_timeline import check_optimal

# load environment variables
load_dotenv()

# store twitter API credentials
KEY = os.getenv('key')
SECRET_KEY = os.getenv('secret_key')
ACCESS_TOKEN = os.getenv('access_token')
ACCESS_TOKEN_SECRET = os.getenv('access_token_secret')

# storing mongodb database details
DATABASE = "twitter_database"
USERS_COL = "user_collection"
TWEETS_COL = "tweets_collection"
RETWEETS_COL = "retweets_collection"
REPLIES_COL = "replies_collection"
BFS_QUEUE_COL = "bfs_queue_collection"

# seed users to initiate scraping
seed_usernames = ["saffrontrail", 
                  "drashwathcn", 
                  "Tej_AnanthKumar",
                  "KumaraswamyFrCM",
                  "b50",
                  "pvsubramanyam"]

# Storing in MongoDB database
client = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = client[DATABASE]
users_col = mydb[USERS_COL]
tweets_col = mydb[TWEETS_COL]
retweets_col = mydb[RETWEETS_COL]
replies_col = mydb[REPLIES_COL]
bfs_queue_col = mydb[BFS_QUEUE_COL]

#some other variables
MAX_USERS = 5000

# get the twitter user details
def get_user_doc(twitter_user):
    twitter_user_doc = {
        "_id": twitter_user._json["id_str"],
        "name": twitter_user._json["name"],
        "screen_name": twitter_user._json["screen_name"],
        "followers": twitter_user._json["followers_count"],
        "friends": twitter_user._json["friends_count"]
    } 
    return twitter_user_doc

# get authenticated twitter api
def get_twitter_auth_api(api_key, api_secret_key):
    auth = tweepy.OAuthHandler(api_key, api_secret_key)
    api = tweepy.API(auth)
    return api

# performing a bfs to obtain users for twitter behaviour analysis
def twitter_bfs(file_obj):
    api = get_twitter_auth_api(KEY, SECRET_KEY)

    """ Saving the queue to deal with timeouts """
    bfs_queue = []
    for user_id in bfs_queue_col.find():
        bfs_queue.append(user_id["screen_name"])

    """ Using an estimated count to get quicker results """
    num_users = users_col.estimated_document_count()

    """ Performing the bfs """
    while len(bfs_queue)!=0 and num_users<MAX_USERS:
        user_name = bfs_queue.pop()
        twitter_user = None

        while True:
            try: 
                twitter_user = api.get_user(user_name)
                break
            except tweepy.TweepError:
                print("Sleeping for 15 minutes...while fetching user details")
                time.sleep(15*60)

        if check_optimal(twitter_user) and users_col.find_one({"_id":twitter_user._json["id_str"]})==None:
            twitter_user_doc = get_user_doc(twitter_user)
            users_col.insert_one(twitter_user_doc)
            num_users = num_users+1
            file_obj.write(twitter_user._json["screen_name"]+"\n")

            """ Logging for every 100 users """
            if num_users%100 == 0:
                print ("Number of users collected: ", num_users)

            """ get the followers of current user """
            while True:
                try:
                    for follower in twitter_user.followers():
                        """ Check if the user has already been saved """
                        if users_col.find_one({"_id": follower._json["id_str"]}) == None:
                            bfs_queue.append(follower._json["screen_name"])
                    break
                except tweepy.TweepError:
                    print("Sleeping for 15 minutes... while fetching followers")
                    time.sleep(15*60)


def main():
    """ Clear out the tables and files when about to start """
    users_col.drop()
    bfs_queue_col.drop()
    users_file = open("users.txt", "w")
    users_file.write("")
    users_file.close()

    """ Store the bfs queue in case if restart needs """
    for seed_user in seed_usernames:
        user = {
            "screen_name" : seed_user
        }
        bfs_queue_col.insert_one(user)

    """ Save the screenames in the file as well """
    users_file = open("users.txt", "a")
    twitter_bfs(users_file)
    users_file.close()

if __name__ == "__main__":
    main()


    

