import random
import string
import kfp
import os
import yaml
import kfp.dsl as dsl
import kfp.components as comp
from kubernetes.client import V1Toleration


def generate_dataset(dataset_path: str):
    import os
    import pandas as pd
    import feast
    from feast.infra.offline_stores.file_source import SavedDatasetFileStorage

    store = feast.FeatureStore(repo_path=os.path.join(os.getcwd(), 'feature_store/'))

    entity_df = pd.DataFrame.from_dict({"HouseId": [i for i in range(1, 20641)]})
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

    dataset = pd.read_parquet(f'{dataset_path}/dataset.parquet').dropna()

    profile = ProfileReport(dataset, title="Dataset Profiling Report")

    metadata = {
        'outputs': [{
            'storage': 'inline',
            'source': profile.to_html(),
            'type': 'web-app',
        }]
    }

    with open(mlpipeline_ui_metadata_path, 'w') as f:
        json.dump(metadata, f)

    print('Dataset validation completed')


def training(dataset_path: str, mlpipeline_metrics_path: kfp.components.OutputPath('Metrics'), mlpipeline_ui_metadata_path: kfp.components.OutputPath()):
    import pandas as pd
    import numpy as np
    import json
    import boto3
    import python_pachyderm
    from sklearn.tree import DecisionTreeRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import cross_validate
    from joblib import dump
    from io import BytesIO

    def dump_to_bytes(model):
        bytes_container = BytesIO()
        dump(model, bytes_container)
        bytes_container.seek(0)
        return bytes_container.read()

    TARGET_COLUMN = 'MedHouseVal'

    dataset = pd.read_parquet(f'{dataset_path}/dataset.parquet').dropna()
    dataset = dataset.drop(columns=['event_timestamp'])
    X, y = dataset.drop(columns=[TARGET_COLUMN]), dataset[TARGET_COLUMN]

    print(f"Train features: {X.columns}")

    scaler = StandardScaler()
    X_transformed = scaler.fit_transform(X)
    y_log = np.log(y)

    regressor = DecisionTreeRegressor()
    cv_scores = cross_validate(estimator=regressor, X=X_transformed, y=y_log, cv=10,
                               scoring=('r2', 'neg_mean_squared_error'))
    regressor.fit(X_transformed, y_log)

    client = python_pachyderm.Client(host='pachd.pachyderm.svc', port=30650)
    with client.commit("feast", "master") as commit:
        client.put_file_bytes(commit, 'models/model.joblib', dump_to_bytes(regressor))
        client.put_file_bytes(commit, 'models/preprocessing.joblib', dump_to_bytes(scaler))

    print('PACHYDERM COMMIT INFO:')
    print(client.wait_commit(commit.id))

    print('PACHYDERM COMMIT FILES:')
    print(list(client.list_file(commit, 'models')))

    metrics = {
        'metrics': [{
            'name': 'cv-mean-r-squared',
            'numberValue': cv_scores['test_r2'].mean(),
            'format': "RAW",
        }, {
            'name': 'cv-mean-neg-mean-sq-error',
            'numberValue': cv_scores['test_neg_mean_squared_error'].mean(),
            'format': "RAW",
        }]
    }
    with open(mlpipeline_metrics_path, 'w') as f:
        json.dump(metrics, f)


    metadata = {
        'outputs': [{
            'storage': 'inline',
            'source': pd.DataFrame({
                'feature_name': X.columns,
                'feature_importance': regressor.feature_importances_
            }).sort_values('feature_importance', ascending=False).to_html(),
            'type': 'web-app',
        }]
    }
    with open(mlpipeline_ui_metadata_path, 'w') as f:
        json.dump(metadata, f)

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

    generate_dataset_op = comp.func_to_container_op(generate_dataset, base_image='dvoitekh/kfp_feast_pachyderm:workshop4')

    data_validation_op = comp.func_to_container_op(data_validation, base_image='dvoitekh/kfp_feast_pachyderm:workshop4')

    training_op = comp.func_to_container_op(training, base_image='dvoitekh/kfp_feast_pachyderm:workshop4')

    generate_dataset_container = generate_dataset_op(data_path) \
                                    .add_pvolumes({data_path: vop.volume}) \
                                    .add_resource_request('memory', '100Mi') \
                                    .add_resource_request('cpu', '100m') \
                                    .add_resource_limit('memory', '200Mi') \
                                    .add_resource_limit('cpu', '200m')

    data_validation_container = data_validation_op(data_path) \
                                    .add_pvolumes({data_path: generate_dataset_container.pvolume}) \
                                    .add_resource_request('memory', '100Mi') \
                                    .add_resource_request('cpu', '100m') \
                                    .add_resource_limit('memory', '1000Mi') \
                                    .add_resource_limit('cpu', '1000m')

    training_container = training_op(data_path) \
                                    .add_pvolumes({data_path: generate_dataset_container.pvolume}) \
                                    .add_resource_request('memory', '500Mi') \
                                    .add_resource_request('cpu', '500m') \
                                    .add_resource_limit('memory', '1000Mi') \
                                    .add_resource_limit('cpu', '1000m')
                                    #   in case you have custom node with taints: https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/#concepts
                                    #   .add_toleration(V1Toleration(effect='NoSchedule',
                                    #                                key='gpu',
                                    #                                operator='Equal',
                                    #                                value='ml'))


if __name__ == '__main__':
    def random_string(length):
        pool = string.ascii_letters + string.digits
        return ''.join(random.choice(pool) for i in range(length))

    experiment_name = 'house_pricing_kubeflow'

    # Compile pipeline to generate compressed YAML definition of the pipeline.
    kfp.compiler.Compiler().compile(pipeline_func, f'{experiment_name}.zip')

    # Don't forget to proxy ml-pipeline API: kubectl port-forward svc/ml-pipeline-ui 3000:80 -n kubeflow
    client = kfp.Client(host='http://localhost:3000', namespace='kubeflow-user-example-com')
    pipeline_name = f"pipeline_{experiment_name}_{random_string(4)}"
    client.upload_pipeline(f'{experiment_name}.zip', pipeline_name)

    # Submit pipeline directly from pipeline function
    # run_name = pipeline_func.__name__ + f' run {random_string(4)}'
    # arguments = {"data_path": '/tmp'}
    # ex = client.create_experiment(experiment_name, namespace='kubeflow-user-example-com')
    # run_result = client.create_run_from_pipeline_func(pipeline_func,
    #                                                  experiment_name=experiment_name,
    #                                                  run_name=run_name,
    #                                                  arguments=arguments)
