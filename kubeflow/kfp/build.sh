#!/bin/bash

# before building the image ensure that:
# 1) feast feature store is pushed to the pachyderm registry
# 2) it contains all pachyderm urls (pachd k8s url, and k8s redis url, not localhost!!!)
IMAGE=dvoitekh/seldon_feast:workshop14
cp -r ../../feast/feature_store ./ && \
    docker build -t $IMAGE . && \
    rm -rf feature_store && \
    docker push $IMAGE
