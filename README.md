# Local K8s cluster with Kubeflow, Seldon, and Feast (Ubuntu)

1. install (docker)[https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04]

    increase max limit for open file descriptors: https://github.com/kubeflow/manifests/issues/2087#issuecomment-1101482095

2. install (kubectl)[https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/]

3. install (kustomize 3.2.0)[https://github.com/kubernetes-sigs/kustomize/releases/tag/v3.2.0]

4. start local k8s cluster via (minikube)[https://minikube.sigs.k8s.io/docs/start/]

    ```bash
    minikube start --kubernetes-version=v1.20.2 --memory 30000 --cpus 4
    ```

5. clone repo and install (kubeflow)[https://github.com/kubeflow/manifests]

    (test installation)[https://www.kubeflow.org/docs/components/central-dash/overview]

6. install (feast)[https://github.com/kubeflow/manifests/tree/master/contrib/feast]

    architecture: https://docs.feast.dev/project/feast-0.9-vs-feast-0.10+

7. install (seldon)[https://github.com/kubeflow/manifests/tree/master/contrib/seldon]

    (test installation)[https://www.kubeflow.org/docs/external-add-ons/serving/seldon]

## Katib for hyperopt

1. (Getting started)[https://www.kubeflow.org/docs/components/katib/hyperparameter], (github link)[https://github.com/kubeflow/katib/tree/master/examples/v1beta1/trial-images/mxnet-mnist]

2. (PyTorch example)[https://github.com/kubeflow/katib/tree/master/examples/v1beta1/trial-images/pytorch-mnist]

3. (PyTorch training job)[https://github.com/kubeflow/pytorch-operator/tree/master/examples/mnist]

## Feast

1. Show kubeflow notebooks

2. Show feast architecture:
    https://docs.feast.dev/project/feast-0.9-vs-feast-0.10+

3. FeatureSource available fields:
    https://github.com/feast-dev/feast/blob/b3ba8aaf3a87343d756a2996376865096d543515/sdk/python/feast/infra/offline_stores/file_source.py

4. Workshop:
    https://github.com/feast-dev/feast-workshop



3. Example of the end-to-end feature store usage in the notebook

## Pachyderm

1. Just show documentation

## Seldon

1. Show predefined format (e.g. sklearn) serving example

2. Show custom model serving via Python class

3. Show monitoring (Prometheus, Graphana)

4. Custom routers and bandits (A/B tests). Endpoints for feedback

5. Outlier detection via Alibi Detect https://docs.seldon.io/projects/seldon-core/en/stable/examples/outlier_cifar10.html






