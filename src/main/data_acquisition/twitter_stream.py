import json
import os
import sys
import traceback
from threading import Lock

import requests
import tweepy
import yaml
from tweepy.streaming import StreamListener


def debug_print(message):
    if debugging:
        print(message)


def dry_run_print(message):
    if dry_run:
        print(message)


class ThreadSafeList():
    def __init__(self):
        self.list = []
        self.edit_mutex = Lock()
        self.counter = 0

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
            dry_run_print('added tweet no {}'.format(self.counter))
            self.counter += 1
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
        debug_print('tweet received: {}'.format(str(data)))
        self.tweet_list.append(json.loads(data))
        if self.tweet_list.length() >= self.tweet_threshold:
            tweet_list = self.tweet_list.flush_and_return_all()
            debug_print('send tweet-list to persistency: {}'.format(json.dumps(tweet_list)))
            self.send_data(tweet_list)
        return True

    def on_error(self, status):
        print('TweetListener had a error: {}'.format(status))

    def send_data(self, data):
        if data and not dry_run:
            # read "API token" from environment variable
            db_access_token = os.environ['DBT']
            # tweets in data are already json-strings, so simply concat them into list
            payload = json.dumps(data)
            url = self.database_rest_url + '/tweets?token=' + db_access_token
            debug_print('started http-request to persistency with tweet-list: {}'.format(payload))
            headers = {'Content-Type': 'application/json'}
            try:
                response = requests.post(url, data=payload, headers=headers)
                debug_print(
                    'finished sending tweet-list to persistency with response: {} : {}'.format(str(response),
                                                                                               response.text))
            except:
                print('ERROR while sending tweet-list to persistency. Traceback is: {}'.format(traceback.format_exc()))

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
    dry_run = bool(config['dry_run'])

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    stream = tweepy.streaming.Stream(api.auth, TweetListener(database_rest_url, tweet_threshold))

    upper_right_longitude = float(config['listening_area']['upper_right']['longitude'])
    upper_right_latitude = float(config['listening_area']['upper_right']['latitude'])
    lower_left_longitude = float(config['listening_area']['lower_left']['longitude'])
    lower_left_latitude = float(config['listening_area']['lower_left']['latitude'])
    stream.filter(locations=[lower_left_longitude, lower_left_latitude, upper_right_longitude, upper_right_latitude],
                  async=True)
