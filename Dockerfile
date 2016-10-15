FROM ubuntu:16.10

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ADD ./src/main/data_acquisition/twitter_stream.py /
ADD ./requirements.txt /

RUN pip3 install -r requirements.txt

CMD python3 /twitter_stream.py CONSUMER_KEY CONSUMER_SECRET ACCESS_TOKEN ACCESS_TOKEN_SECRET