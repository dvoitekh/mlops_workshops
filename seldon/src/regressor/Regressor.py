import os
import logging
import numpy as np
from joblib import load


class Regressor(object):
    def __init__(self):
        self.model = load(os.environ['MODEL_PATH'])

    def predict(self, X, features_names):
        logging.info(X, features_names)
        y_log = self.model.predict(X)
        return np.exp(y_log)
