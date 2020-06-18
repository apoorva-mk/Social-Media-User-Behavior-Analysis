from textblob import TextBlob
import tweepy
import matplotlib.pyplot as plt
import os
import pymongo

key = 'O0H9liclRNMQ3NdkKmrQjMjwB'
secret_key = 'eDnztQY4r00EvA5ODvIt1yNyE9JgWkqrMscC1LbVwvZ1XyaTu2'
access_token = '1272945396579332101-sdcvHLaaGh2OfKQMCLCrYBeACGXzLt'
access_token_secret = 'TFlEWI8uC8tlgzNHB7K7wcNEvu0qq4pX9ifhLohcn5X86'

def percentage(part, whole):
	return float(part)/float(whole) * 100

auth = tweepy.OAuthHandler(consumer_key=key, consumer_secret=secret_key)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
'''
myclient = pymongo.MongoClient("localhost", 27017)
mydb = myclient["Tweets"]
tweet_col = mydb["tweets"]
'''
geocodes = {'Delhi':'28.7041,77.1025,100km', 'Mumbai':'19.0760,72.8777,100km', 'Bangalore':'12.9716,77.5946,100km', 'Kolkata':'22.5726,88.3639,100km', 'Chennai':'13.0827,80.2707,100km'}
searchTerms = ['coronavirus', 'quarantine', 'lockdown', 'pandemic', 'covid-19']
num_tweets_per_search = 2000
for searchTerm in searchTerms:
	print("Scraping tweets with hashtag:",searchTerm)
	for city in geocodes.keys():
		print("\tScraping tweets from:",city)
		geocode = geocodes[city]
		f = open(os.path.join("tweets", searchTerm, city+".txt"),'a',encoding='utf-8')
		tweets = tweepy.Cursor(api.search, q=searchTerm, geocode=geocode).items(num_tweets_per_search)
		c = 1
		for tweet in tweets:
			print("\t\tScraping tweet#"+str(c))
			#tweet_info = { 'hashtag':searchTerm, 'text':tweet.text, 'location':city, 'created_at':tweet.created_at }
			#tweet_col.insert_one(tweet_info)
			try:
				f.write(tweet.text+"\n")
				f.write(">>>>>>>>>>\n") #10
				f.write(str(tweet.created_at)+"\n")
				f.write("^^^^^^^^^^\n") #10
				f.write("@@@@@@@@@@@@@@@@@@@@\n") #20
				c+=1
			except:
				print("Failed, scraping next tweet....")
				continue
		f.close()
			#break
		#break
	#break