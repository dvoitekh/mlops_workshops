FROM python:3.7.12
WORKDIR /app

RUN apt update && apt install -y libjemalloc-dev libboost-dev \
                       libboost-filesystem-dev \
                       libboost-system-dev \
                       libboost-regex-dev \
                       autoconf \
                       flex \
                       bison \
                       ffmpeg \
                       libsm6 \
                       libxext6

# Install python packages
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy source code
COPY . .

# Define environment variables
ENV HOME /app
ENV MODEL_NAME src.Preprocessor
ENV SERVICE_TYPE MODEL
ENV FEATURE_STORE_PATH /app/feature_store/
ENV PREPROCESSSING_PATH /app/preprocessing.joblib
ENV MODEL_PATH /app/model.joblib
ENV OUTLIER_DETECTOR_MODEL_PATH /app/od.joblib
ENV FEAST_S3_ENDPOINT_URL http://pachd.pachyderm.svc:30600

# Changing folder to default user
RUN chown -R 8888 /app

CMD exec seldon-core-microservice $MODEL_NAME --service-type $SERVICE_TYPE
