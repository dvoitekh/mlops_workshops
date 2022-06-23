#!/bin/bash

cp -r ../feast/feature_store ./ && \
    pachctl get file feast@master:/models/ --recursive --output . && \
    docker build -t dvoitekh/seldon_feast:workshop9 . && \
    rm -rf feature_store && \
    docker push dvoitekh/seldon_feast:workshop9
