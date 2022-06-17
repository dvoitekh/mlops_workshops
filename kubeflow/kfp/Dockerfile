FROM smizy/scikit-learn:0.23-alpine

ADD ./requirements.txt /tmp/requirements.txt

RUN pip install setuptools==41.2.0 pip==21.0.1 && \
    pip install -r /tmp/requirements.txt

ADD . /app
WORKDIR /app

# will be overwritten by kf pipeline
ENTRYPOINT [ "python3", "pipeline.py" ]
