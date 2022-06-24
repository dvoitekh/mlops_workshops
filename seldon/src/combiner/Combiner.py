import logging
import numpy as np

class Combiner(object):
    def aggregate(self, X, features_names):
        logging.info(X, features_names)
        output = {
            "regressor": X[0].tolist(),
            "outliers_detector": X[1].tolist(),
        }
        return output
