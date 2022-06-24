import os
import logging
import numpy as np
from joblib import load


class AlibiDetector(object):
    def __init__(self):
        self.od = load(os.environ['OUTLIER_DETECTOR_MODEL_PATH'])

    def predict(self, X, features_names):
        logging.info(X, features_names)
        return self.od.predict(X)['data']['is_outlier']


"""
Outlier Detector's "predict" output:
{'data': {'instance_score': array([0.17398582]),
  'feature_score': None,
  'is_outlier': array([1])},
 'meta': {'name': 'IForest',
  'detector_type': 'offline',
  'data_type': 'tabular',
  'version': '0.9.1'}}
"""
