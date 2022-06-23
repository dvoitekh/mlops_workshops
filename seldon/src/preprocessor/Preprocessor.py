import feast
import logging
import os
from joblib import load

# python component details:
# https://docs.seldon.io/projects/seldon-core/en/latest/python/python_component.html

# model,combiner,router:
# https://docs.seldon.io/projects/seldon-core/en/latest/examples/graph-metadata.html#Two-Level-Graph
class Preprocessor(object):
    def __init__(self):
        self.feature_store = feast.FeatureStore(
            repo_path=os.environ['FEATURE_STORE_PATH']
        )
        self.scaler = load(os.environ['PREPROCESSSING_PATH'])

    def class_names(self):
        return [
            "house_main_view:HouseId",
            "house_main_view:MedInc",
            "house_main_view:HouseAge",
            "house_main_view:AveRooms",
            "house_main_view:AveBedrms",
            "house_main_view:Population",
            "house_main_view:AveOccup",
            "house_lat_lon_view:Latitude",
            "house_lat_lon_view:Longitude"
        ]

    def health_status(self):
        return []

    def predict(self, X, features_names):
        online_features = self.feature_store.get_online_features(
            features=[
                "house_main_view:MedInc",
                "house_main_view:HouseAge",
                "house_main_view:AveRooms",
                "house_main_view:AveBedrms",
                "house_main_view:Population",
                "house_main_view:AveOccup",
                "house_lat_lon_view:Latitude",
                "house_lat_lon_view:Longitude"
            ],
            entity_rows=[
                {"HouseId": x[0]} for x in X
            ]
        ).to_df()[['HouseId', 'MedInc', 'HouseAge', 'AveRooms', 'AveBedrms', 'Population', 'AveOccup', 'Latitude', 'Longitude']]
        features = self.scaler.transform(online_features)
        logging.info(features)
        return features

    # def metrics(self):
    #     print("metrics called")
    #     return [
    #         # a counter which will increase by the given value
    #         {"type": "COUNTER", "key": "mycounter", "value": 1},

    #         # a gauge which will be set to given value
    #         {"type": "GAUGE", "key": "mygauge", "value": 100},

    #         # a timer (in msecs) which  will be aggregated into HISTOGRAM
    #         {"type": "TIMER", "key": "mytimer", "value": 20.2},
    #     ]
