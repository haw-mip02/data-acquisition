import json
import sys
from threading import Lock

import requests
import tweepy
import yaml
from tweepy.streaming import StreamListener


class ThreadSafeList():
    def __init__(self):
        self.list = []
        self.edit_mutex = Lock()

    def length(self):
        self.edit_mutex.acquire()
        try:
            result = len(self.list)
        finally:
            self.edit_mutex.release()
        return result

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
    def __init__(self, database_rest_url, tweet_threshold):
        self.tweet_list = ThreadSafeList()
        self.tweet_threshold = tweet_threshold
        self.database_rest_url = database_rest_url

    def on_data(self, data):
        if debugging:
            print('tweet received: {}'.format(str(data)))
        self.tweet_list.append(data)
        if self.tweet_list.length() > self.tweet_threshold:
            tweet_list = self.tweet_list.flush_and_return_all()
            if debugging:
                print('send tweet-list to persistency: {}'.format(json.dumps(tweet_list)))
            self.send_data(tweet_list)
        return True

    def on_error(self, status):
        print('TweetListener had a error: {}'.format(status))

    def send_data(self, data):
        if debugging:
            print('started http-request to persistency with tweet-list: {}'.format(str(data)))
        data_json = json.dumps(data)
        url = self.database_rest_url.rstrip('/') + '/tweets'
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=data_json, headers=headers)
        if debugging:
            print('finished http-request tweet-list to persistency with response: {}'.format(str(response)))

if __name__ == '__main__':
    path = '../../../config.yml'
    if len(sys.argv) > 1:
        path = sys.argv[1]
    config = {}
    with open(path, 'r') as file:
        try:
            config = yaml.load(file)
        except yaml.YAMLError as exc:
            print(exc)
    print('Starting with config: {}'.format(json.dumps(config)))
    consumer_key = config['twitter_credentials']['consumer_key']
    consumer_secret = config['twitter_credentials']['consumer_secret']
    access_token = config['twitter_credentials']['access_token']
    access_token_secret = config['twitter_credentials']['access_token_secret']
    tweet_threshold = int(config['tweet_threshold'])
    database_rest_url = config['database_rest_url'].rstrip('/')
    debugging = bool(config['debugging'])

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    stream = tweepy.streaming.Stream(api.auth, TweetListener(database_rest_url, tweet_threshold))

    up_right_longitude = config['listening_area']['upper_right']['longitude']
    up_right_latitude = config['listening_area']['upper_right']['latitude']
    down_left_longitude = config['listening_area']['lower_left']['longitude']
    down_left_latitude = config['listening_area']['lower_left']['latitude']
    stream.filter(locations=[up_right_longitude, up_right_latitude, down_left_longitude, down_left_latitude],
                  async=True)
