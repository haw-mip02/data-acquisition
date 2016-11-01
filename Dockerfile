FROM ubuntu:16.10

ENV TWEET_THRESHOLD 20
ENV DOCKERIZE_VERSION v0.2.0

RUN apt-get update && \
    apt-get install -y python3 python3-pip curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ADD ./src/main/data_acquisition/twitter_stream.py /
ADD ./docker/config.yml.j2 /
ADD ./docker/run.sh /
ADD ./requirements.txt /

RUN chmod +x /run.sh && \
    pip3 install -r requirements.txt

# install dockerize
RUN curl -L -O https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz && \
    tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz && \
    rm -rf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz


CMD /run.sh