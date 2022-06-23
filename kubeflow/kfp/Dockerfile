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
ENV HOME /app
ENV FEAST_S3_ENDPOINT_URL http://pachd.pachyderm.svc:30600
