#!/bin/bash

dockerize -template /config.yml.j2:/config.yml

python3 /twitter_stream.py /config.yml