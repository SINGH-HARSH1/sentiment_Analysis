# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 12:51:25 2019

@author: Harsh
"""

"""
In this script we have Tweets scraped through Twitter API for a user realDonaldTrump
and  basic sentiment analysis being performed on the tweets(text) and a 
corresponding sentiment column has been created in the DataFreame(df).
For the purpose of Scraping Tweets, please refer to the tweet_sraping_poc . 
"""

"""
Please check TweetAnalyzer class for Functionality reference for sentiment Analysis.
"""

from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener 
# Class from tweepy module that allows us to listen to the tweets.
from tweepy import OAuthHandler 
# Class is responsible for authenticating based on the credentials we provide.
from tweepy import Stream 
# Class handles Streams

# This will be used to check sentiments
from textblob import TextBlob

import twitter_credentials
import re
import numpy as np
import pandas as pd


class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)
        
        self.twitter_user = twitter_user
        
    def get_twitter_client_api(self):
        """Function to get twitter client API (adding binary search)"""
        return self.twitter_client
        
    def get_user_timeline_tweets(self, num_tweets):
        """Function to get user timeline tweets"""
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets
    
    def get_friend_list(self,num_friends):
        """Function to get user friend list"""
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list
    
    def get_home_timeline_tweets(self, num_tweets):
        """Function to get users home timeline tweets"""
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets
    
    
        
# Class is responsible for twitter authentication
class TwitterAuthenticator():
    """This class handles Twitter authentication"""
    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
        return auth


# Class responsible for streaming the tweets
class TwitterStreamer():
    """Class for streaming and processing live tweets."""
    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()
    
    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        """This handles Twitter authentication and the connection to the
        twitter streaming API"""
        listener = TwitterListner(fetched_tweets_filename)
        auth = self.twitter_authenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)
        stream.filter(track=hash_tag_list)        


# Class to print the tweets

class TwitterListner(StreamListener):
    """This is a basic listener class that just prints received tweets to stdout"""
    
    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename
    
    def on_data(self, data):
        """This is an overrun method which will take in the data
        that is streamed in from the StreamListner(the one that is listening 
        for tweets)"""
        try:
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(data)
            return True
        except BaseException as e:
            print("Error on_data: %s" %str(e))
        return True
        
    def on_error(self, status):
        """This is an overrun method from streamlistner class that happens 
        when there is an error"""
        if status == 420:
            #Returning False on data_Method in case rate limit occurs.
            return False
        print(status) # Prints the status message of the error


class TweetAnalyzer():
    """Functionality for analyzing and categorizing content from tweets.""" 
    
    def clean_tweets(self, tweet):
        """Function using regular expressions to clean Tweets and hyperlinks"""
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
    
    def analyze_sentiment(self, tweet):
        """Function is responsible TextBlob and using sentiment analyzer and using the sentiment."""
        analysis = TextBlob(self.clean_tweets(tweet))
        
        if analysis.sentiment.polarity > 0:
            return 1
        elif analysis.sentiment.polarity == 0:
            return 0
        else:
            return -1
    
    def tweets_to_dataframe(self, tweets):
        """This function converts scraped tweets to dataframe"""
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=["tweets"])
        
        df["id"] = np.array([tweet.id for tweet in tweets])
        df["len_tweets"] = np.array([len(tweet.text) for tweet in tweets])
        df["date"] = np.array([ tweet.created_at for tweet in tweets])
        df["source"] = np.array([tweet.source for tweet in tweets])
        df["likes"] = np.array([tweet.favorite_count for tweet in tweets])
        df["retweets"] = np.array([tweet.retweet_count for tweet in tweets])
        
        return df
 
# This will be the main part of the program

if __name__ == "__main__":
        twitter_client = TwitterClient()
        tweet_analyzer = TweetAnalyzer()
        api = twitter_client.get_twitter_client_api()
        
        tweets = api.user_timeline(screen_name="realDonaldTrump", count=20) # Please increase the count here for more tweets.
        df = tweet_analyzer.tweets_to_dataframe(tweets)
        df["sentiment"] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df["tweets"]])
        print(df.head(10))
        
        