#!/bin/bash

if ! [ -z $REST_PORT_3000_TCP_ADDR ] && ! [ -z $REST_PORT_3000_TCP_PORT ]; then
    export DATABASE_REST_URL="http://$REST_PORT_3000_TCP_ADDR:$REST_PORT_3000_TCP_PORT"
fi

dockerize -template /config.yml.j2:/config.yml

python3 /twitter_stream.py /config.yml