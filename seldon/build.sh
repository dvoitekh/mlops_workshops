#!/bin/bash

IMAGE=dvoitekh/seldon_feast:workshop14
cp -r ../feast/feature_store ./ && \
    pachctl get file feast@master:/models/ --recursive --output . && \
    docker build -t $IMAGE . && \
    rm -rf feature_store && \
    docker push $IMAGE
