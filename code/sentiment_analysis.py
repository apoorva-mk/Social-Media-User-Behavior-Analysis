import os
from textblob import TextBlob
import matplotlib.pyplot as plt

def get_tweets(file):
	f = open(file, 'r', encoding='utf-8')
	tweets = []
	tweet_info = f.read().split("@" * 20)
	tweet_text = [tweet_info_single.split(">" * 10)[0].strip() for tweet_info_single in tweet_info]
	return tweet_text

def get_term_wise_tweets(base_path):
	tweets_collection_term = {}
	for searchTerm in os.listdir(base_path):
		tweets_collection_term[searchTerm] = {}
		for city_file in os.listdir(os.path.join(base_path, searchTerm)):
			city = city_file[:-4]
			file_path = os.path.join(base_path, searchTerm, city_file)
			tweets = get_tweets(file_path)
			tweets_collection_term[searchTerm][city] = tweets
	return tweets_collection_term

def get_city_wise_tweets(base_path):
	tweets_collection_city = {}
	cities = ['Kolkata', 'Mumbai', 'Delhi', 'Bangalore', 'Chennai']
	for city in cities:
		tweets_collection_city[city] = {}
		for searchTerm in os.listdir(base_path):
			file_path = os.path.join(base_path, searchTerm, city) + ".txt"
			tweets = get_tweets(file_path)
			tweets_collection_city[city][searchTerm] = tweets
	return tweets_collection_city

def get_score(analysis):
	return analysis.sentiment.polarity

def get_sentiment_classes():
	return ['Strongly Negative', 'Slightly Negative', 'Slightly Positive', 'Strongly Positive']

def get_sentiment_colors():
	return ['red', 'pink', 'lightskyblue', 'blue']

def create_graph(sizes, colors, labels, searchTerm, city):
	patches, texts = plt.pie(sizes, colors=colors, startangle=90)
	plt.legend(patches, labels, loc="best")
	plt.title("Sentiment distribution towards \""+searchTerm+"\" in the city of "+city)
	plt.axis('equal')
	plt.tight_layout()
	#plt.show()
	plt.savefig(os.path.join(os.pardir, "results", "sentiment_analysis", searchTerm+"_"+city+".png"))

def create_city_wise_sentiment_graph(tweets_collection_city):
	for city in tweets_collection_city.keys():
		for searchTerm in tweets_collection_city[city].keys():
			sizes = get_sentiment(tweets_collection_city[city][searchTerm])
			classes = get_sentiment_classes()
			colors = get_sentiment_colors()
			labels = [ classes[i]+" ["+str(sizes[i])+"%]" for i in range(len(sizes)) ]
			create_graph(sizes, colors, labels, searchTerm, city)

def get_sentiment(tweets):
	st_neg, sl_neg, sl_pos, st_pos = 0, 0, 0, 0
	num_tweets = len(tweets)
	for tweet in tweets:
		analysis = TextBlob(tweet)
		score = get_score(analysis)
		if score <= -0.5:
			st_neg+= 1
		elif score <= 0:
			sl_neg+= 1
		elif score <= 0.5:
			sl_pos+= 1
		else:
			st_pos+= 1
	return [percentage(st_neg, num_tweets), 
			percentage(sl_neg, num_tweets), 
			percentage(sl_pos, num_tweets), 
			percentage(st_pos, num_tweets)]

def percentage(part, whole):
	return format(float(part) / float(whole) * 100.0, '.2f')


def create_term_wise_sentiment_graph(tweets_collection_term):
	pass


def main():
	base_path = os.path.join(os.pardir, "dataset", "tweets")
	tweets_collection_city = get_city_wise_tweets(base_path)
	tweets_collection_term = get_term_wise_tweets(base_path)
	create_city_wise_sentiment_graph(tweets_collection_city)



if __name__ == '__main__':
	main()