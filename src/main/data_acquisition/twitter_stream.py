import tweepy
from tweepy.streaming import StreamListener

consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""


class GermanChristmasListener(StreamListener):
    def on_data(self, data):
        # TODO: send data to database
        print(data)
        return True

    def on_error(self, status):
        print(status)


if __name__ == '__main__':
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    germanListener = GermanChristmasListener()

    streamGerman = tweepy.streaming.Stream(api.auth, germanListener)

    streamGerman.filter(locations=[9.391045899999995, 53.11264, 11.451602200000025, 53.8979416], async=True)
