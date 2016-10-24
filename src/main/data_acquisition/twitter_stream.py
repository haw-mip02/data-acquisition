import json
import sys
from threading import Lock

import requests
import tweepy
from tweepy.streaming import StreamListener


class ThreadSafeList():
    def __init__(self):
        self.list = []
        self.edit_mutex = Lock()

    def length(self):
        return len(self.list)

    def append(self, item):
        self.edit_mutex.acquire()
        try:
            self.list.append(item)
        finally:
            self.edit_mutex.release()

    def flush_and_return_all(self):
        self.edit_mutex.acquire()
        try:
            result = list(self.list)
            self.list.clear()
        finally:
            self.edit_mutex.release()
        return result


class TweetListener(StreamListener):
    def __init__(self):
        self.tweet_list = ThreadSafeList()
        self.tweet_threshold = sys.argv[5]
        self.database_rest_url = sys.argv[6]

    def on_data(self, data):
        self.tweet_list.append(data)
        if self.tweet_list.length() > self.tweet_threshold:
            tweet_list = self.tweet_list.flush_and_return_all()
            self.send_data(tweet_list)
        return True

    def on_error(self, status):
        print(status)

    def send_data(self, data):
        data_json = json.dumps(data)
        url = self.database_rest_url.rstrip('/') + '/tweets'
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=data_json, headers=headers)

if __name__ == '__main__':
    consumer_key = sys.argv[1]
    consumer_secret = sys.argv[2]
    access_token = sys.argv[3]
    access_token_secret = sys.argv[4]

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    stream = tweepy.streaming.Stream(api.auth, TweetListener())

    stream.filter(locations=[9.391045899999995, 53.11264, 11.451602200000025, 53.8979416], async=True)