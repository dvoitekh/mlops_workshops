import random
import string
import kfp
import kfp.dsl as dsl
import kfp.components as comp


def generate_dataset(dataset_path: str):
    import os
    import pandas as pd
    import feast
    from feast.infra.offline_stores.file_source import SavedDatasetFileStorage

    os.environ['FEAST_S3_ENDPOINT_URL'] = 'http://pachd.pachyderm.svc:30600'
    os.environ['AWS_ACCESS_KEY_ID'] = ''
    os.environ['AWS_SECRET_ACCESS_KEY'] = ''

    store = feast.FeatureStore(repo_path="feature_repo/")

    entity_df = pd.DataFrame.from_dict({"HouseId": [i for i in range(1, 100000)]})
    entity_df['event_timestamp'] = pd.to_datetime('now', utc=True)

    retrieval_job = store.get_historical_features(
        entity_df=entity_df,
        features=[
            "house_main_view:MedInc",
            "house_main_view:HouseAge",
            "house_main_view:AveRooms",
            "house_main_view:AveBedrms",
            "house_main_view:Population",
            "house_main_view:AveOccup",
            "house_main_view:AveOccup",
            "house_main_view:MedHouseVal",
            "house_lat_lon_view:Latitude",
            "house_lat_lon_view:Longitude",
        ],
    )

    dataset = store.create_saved_dataset(
        from_=retrieval_job,
        name='dataset',
        storage=SavedDatasetFileStorage(path=f'{dataset_path}/dataset.parquet')
    )

    print('Dataset generation completed')


def data_validation(dataset_path: str, mlpipeline_ui_metadata_path: kfp.components.OutputPath()):
    import pandas as pd
    import json
    from pandas_profiling import ProfileReport

    dataset = pd.read_parquet(f'{dataset_path}/dataset.parquet')

    profile = ProfileReport(dataset, title="Dataset Profiling Report")

    metadata = {
        'outputs': [{
            'storage': 'inline',
            'source': profile.to_html(),
            'type': 'markdown',
        }]
    }

    with open(mlpipeline_ui_metadata_path, 'w') as f:
        json.dump(metadata, f)

    print('Dataset validation completed')


def training(dataset_path: str):
    import pandas as pd
    from sklearn.tree import DecisionTreeRegressor
    from joblib import dump
    import boto3

    TARGET_COLUMN = 'MedHouseVal'

    dataset = pd.read_parquet(f'{dataset_path}/dataset.parquet')
    X, y = dataset.drop(columns=[TARGET_COLUMN]), dataset[TARGET_COLUMN]

    regressor = DecisionTreeRegressor()
    regressor.fit(X, y)
    dump(regressor, 'model.joblib')

    s3_client = boto3.client(
        's3',
        endpoint_url='http://pachd.pachyderm.svc:30600',
        aws_access_key_id='',
        aws_secret_access_key=''
    )

    s3_client.upload_file('model.joblib', 'master.feast', "model.joblib")
    print('Training completed')


# Define the pipeline
@dsl.pipeline(
   name='House Pricing Pipeline',
   description=''
)
# Define parameters to be fed into pipeline
def pipeline_func(data_path: str):
    # Define volume to share data between components.
    vop = dsl.VolumeOp(
        name="create_volume",
        resource_name="data-volume",
        size="1Gi",
        modes=dsl.VOLUME_MODE_RWM
    )

    generate_dataset_op = comp.func_to_container_op(generate_dataset, base_image='TODO')
    data_validation_op = comp.func_to_container_op(data_validation, base_image='TODO')
    training_op = comp.func_to_container_op(training, base_image='TODO')

    generate_dataset_container = generate_dataset_op(data_path) \
                                    .add_pvolumes({data_path: vop.volume})

    data_validation_container = data_validation_op(data_path) \
                                    .add_pvolumes({data_path: generate_dataset_container.pvolume})

    training_container = training_op(data_path) \
                                    .add_pvolumes({data_path: generate_dataset_container.pvolume})


if __name__ == '__main__':
    def random_string(length):
        pool = string.letters + string.digits
        return ''.join(random.choice(pool) for i in range(length))

    client = kfp.Client(host='ml-pipeline.kubeflow.svc:8888')

    experiment_name = 'house_pricing_kubeflow'
    run_name = pipeline_func.__name__ + f' run {random_string(4)}'
    arguments = {"data_path": '/tmp'}

    # Compile pipeline to generate compressed YAML definition of the pipeline.
    kfp.compiler.Compiler().compile(pipeline_func, '{}.zip'.format(experiment_name))

    # Submit pipeline directly from pipeline function
    run_result = client.create_run_from_pipeline_func(pipeline_func,
                                                     experiment_name=experiment_name,
                                                     run_name=run_name,
                                                     arguments=arguments)
