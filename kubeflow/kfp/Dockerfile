FROM python:3.9.5

RUN apt update && apt install -y libjemalloc-dev libboost-dev \
                       libboost-filesystem-dev \
                       libboost-system-dev \
                       libboost-regex-dev \
                       python-dev \
                       autoconf \
                       flex \
                       bison

ADD ./requirements.txt /tmp/requirements.txt

RUN pip install setuptools==41.2.0 pip==21.0.1 && \
    pip install -r /tmp/requirements.txt

ADD . /app
WORKDIR /app

# will be overwritten by kf pipeline
ENTRYPOINT [ "python3", "pipeline.py" ]
