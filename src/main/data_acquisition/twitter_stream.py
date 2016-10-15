from threading import Lock

import tweepy
from tweepy.streaming import StreamListener

consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""


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
        print("item appended, list is" + str(self.list))

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

    def on_data(self, data):
        self.tweet_list.append(data)
        if (self.tweet_list.length() > 2):
            tweet_list = self.tweet_list.flush_and_return_all()
            # TODO: send data to database
            print(tweet_list)
        return True

    def on_error(self, status):
        print(status)

if __name__ == '__main__':

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    stream = tweepy.streaming.Stream(api.auth, TweetListener())

    stream.filter(locations=[9.391045899999995, 53.11264, 11.451602200000025, 53.8979416], async=True)
