# This is an example feature definition file

from feast import Entity, FeatureService, FeatureView, Field, FileSource, PushSource, ValueType
from feast.types import Float32, Int64


main_source = FileSource(
#     local file
    # path="../data/house_dataset_main.parquet",

#     pachyderm file
    # path="s3://master.feast/house_dataset_main.parquet",
    # s3_endpoint_override="http://pachd.pachyderm.svc:30600",

#     aws s3 file
    path="s3://dvoitekh-kubeflow/feast/data/house_dataset_main.parquet",

    timestamp_field="EventTimestamp",
    created_timestamp_column="Created",
)

lat_lon_source = FileSource(
#     local file
    # path="../data/house_dataset_lat_lon.parquet",

#     pachyderm file
    # path="s3://master.feast/house_dataset_lat_lon.parquet",
    # s3_endpoint_override="http://pachd.pachyderm.svc:30600",

#     aws s3 file
    path="s3://dvoitekh-kubeflow/feast/data/house_dataset_lat_lon.parquet",
    timestamp_field="EventTimestamp",
    created_timestamp_column="Created",
)

# main_push_source = PushSource(
#     name="main_push_source", batch_source=main_source,
# )

house_id = Entity(name="HouseId", join_keys=["HouseId"], value_type=ValueType.INT64,)

house_main_view = FeatureView(
    name="house_main_view",
    entities=["HouseId"],
    schema=[
        Field(name="MedInc", dtype=Float32),
        Field(name="HouseAge", dtype=Float32),
        Field(name="AveRooms", dtype=Float32),
        Field(name="AveBedrms", dtype=Float32),
        Field(name="Population", dtype=Int64),
        Field(name="AveOccup", dtype=Float32),
        Field(name="MedHouseVal", dtype=Float32)
    ],
    online=True,
    source=main_source
)

house_lat_lon_view = FeatureView(
    name="house_lat_lon_view",
    entities=["HouseId"],
    schema=[
        Field(name="Latitude", dtype=Float32),
        Field(name="Longitude", dtype=Float32)
    ],
    online=True,
    source=lat_lon_source
)

service = FeatureService(
    name="house_service", features=[house_main_view, house_lat_lon_view]
)
