# MLOps Mini-Course 2022

This is a compact but all-encompassing set of workshops to practice cloud-native MLOps tools like [Kubeflow](https://www.kubeflow.org/), [Pachyderm](https://www.pachyderm.com/), [Feast](https://feast.dev/), and [Seldon](https://www.seldon.io). All this experiments are intended to run in k8s environment. It's recommended to use Minikube deployed on Linux server (minimum 12 GB RAM, 2 CPU, 50 GB of disk space).

## Environment setup

1. Launch a server or use your own computer if it satisfies the aforementioned requirements.

2. Install [Docker](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04). Since we'll deploy a lot of things, make sure that you increased the [max limit for open file descriptors](https://github.com/kubeflow/manifests/issues/2087#issuecomment-1101482095).

2. Install [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)

3. Install [kustomize 3.2.0](https://github.com/kubernetes-sigs/kustomize/releases/tag/v3.2.0)

4. Install [helm](https://helm.sh/docs/intro/install)

5. Install [Minikube](https://minikube.sigs.k8s.io/docs/start/). You will also need to [enable Docker to run as a non-root user](https://docs.docker.com/engine/security/rootless/)

6. Start a local k8s cluster (the following k8s version since Kubeflow is not yet compatible with latest k8s versions):

    ```bash
    minikube start --kubernetes-version=v1.20.2 --memory 30000 --cpus 4
    ```

7. Verify that it works by checking available pods. Also you can launch a dashboard:

    ```bash
    kubectl get po --all-namespaces
    minikube dashboard
    ```

8. Now let's install Kubeflow. Clone the [official repo with manifests](https://github.com/kubeflow/manifests) and install them:

    ```bash
    while ! kustomize build example | kubectl apply -f -; do echo "Retrying to apply resources"; sleep 10; done
    ```

9. Also, let's use the same repo to install [Feast manifests](https://github.com/kubeflow/manifests/tree/master/contrib/feast) and [Seldon manifests](https://github.com/kubeflow/manifests/tree/master/contrib/seldon)

10. Verify installation by [proxying istio gateway to local port](https://www.kubeflow.org/docs/components/central-dash/overview) and by checking pods within your cluster. You can login to the Kubeflow dashboard with the following credentials - `user@example.com / 12341234`

11. Also, we'll need to install Pachyderm locally. Use [this installation guide](https://www.google.com/url?q=https://docs.pachyderm.com/latest/getting-started/local-installation&sa=D&source=editors&ust=1655296135088959&usg=AOvVaw1Lel4BjoQ4hHS93eZQbniC). However, it's preferred to create a separate namespace for the service (e.g. `pachdyderm`).

## Kubernetes basics

Visit the [kubernetes directory](kubernetes/) and deploy a basic application with Service and HPA:

```bash
kubectl apply -f .
```

## Tensorboard

Create a new Kubeflow Notebook (based on pytorch) and run [this sample notebook](kubeflow/tensorboard/). Afterwards, you can go to Kubeflow Tensorboard and create a new server with a PVC of the corresponding notebook pointing to the directory with logs.

## Pachyderm

Considering that you have Pachyderm installed and configured, you can run the [starter notebook](pachyderm/).

After that, go to the [housing-prices](pachyderm/housing-prices/) directory to explore how Pachyderm can be used for model training and deployment.

You can also enable Promethus monitoring by using the following [tutorial](https://docs.pachyderm.com/latest/deploy-manage/deploy/prometheus/)

## Feast

Open Kubeflow dashboard, create a new notebook. In the notebook clone this repo. Navigate to [feast directory](feast/). Current code will use local files and registry, but it can be replaced with s3 or gcs. Run the notebook to see how Feast provides ability to query features both in the offline and online modes.

## Katib (hyper-parameter optimization)

Get familiar with [Katib](https://www.kubeflow.org/docs/components/katib/experiment).

Go to [katib directory](kubeflow/katib/) and apply the basic mnist experiment:

```bash
    kubectl apply -f .
```

After than you can navigate to Katib tab in the Kubeflow dashboard and check the newly created experiment.

[Code for the coresponding example](https://github.com/kubeflow/katib/tree/master/examples/v1beta1/trial-images/pytorch-mnist).

## KFP (Kubeflow Pipelines)

Navigate to the directory with [a sample pipeline](kubeflow/kfp/). It's integrated with Feast and Pachyderm services that were used before. You don't need to build docker image - it's already available in my public docker registry. You can run the pipeline (don't forget to port-forward ml-pipeline-ui service and change the url to localhost) or just compile it and upload it manually afterwards (disregard connection error - pipeline archive will be generated anyway):

```bash
python pipeline.py
```

## Kubeflow Kale

There's a sample [Kale notebook](kubeflow/kale/) that generates a KFP pipeline for Titanic dataset classification. In order to run it:

    1. Create a new Kubeflow notebook with a CUSTOM image: `gcr.io/arrikto/jupyter-kale:v0.5.0`

    2. Copy the contents of the Kale demo directory to the notebook

    3. Open the titanic_dataset_ml.ipynb file there and activate the Kale jupyter extension on the left bar.

    4. Change the name of your mounted volume so it's used in the pipeline

    5. Click "Compile and Upload" button

    6. Navigate to KFP dashboard in the browser and run the pipeline






