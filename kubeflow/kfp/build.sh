#!/bin/bash

cp -r ../../feast/feature_store ./ && \
    docker build -t dvoitekh/kfp_feast_pachyderm:workshop4 . && \
    rm -rf feature_store && \
    docker push dvoitekh/kfp_feast_pachyderm:workshop4
