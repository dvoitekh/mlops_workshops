#!/bin/bash

cp ../../feast/feature_store ./ && \
    docker build -t kfp_feast_pachyderm . && \
    docker push kfp_feast_pachyderm:latest
