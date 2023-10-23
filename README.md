# Basic Hosting Demo
This repo contains a demo of hosting a machine learning model with FastAPI, docker, and minikube.

## Pre-requisites
- [Docker](https://docs.docker.com/get-docker/)
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [Kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [hyperkit](https://minikube.sigs.k8s.io/docs/drivers/hyperkit/)
- python and virtual environment if you'd like to run the demo locally via uvicorn.


## Running the demo
### Locally via uvicorn

1. Create a virtual environment and install the requirements
Example uses conda but other alternatives works as well.

- Create and activate a new virtual environment:
    ```
    conda create -n <YOUR_ENV_NAME> python=3.10
    conda activate <YOUR_ENV_NAME>
    ```

- Install requirements
    ```
    cd basic_hosting_demo/prediction_service
    pip install -r requirements.txt
    ```
- Run the service
    ```
    cd basic_hosting_demo/prediction_service
    python -m uvicorn prediction_service.service:app --port=8080
    ```

### Locally in minikube
- If minikube and kubectl are not installed, follow the instructions [here](https://minikube.sigs.k8s.io/docs/start/) and [here](https://kubernetes.io/docs/tasks/tools/install-kubectl/) respectively.

-  Start minikube and enable metrics server
    ```
    minikube start --cpus 4 --memory 16000 --extra-config=kubelet.housekeeping-interval=10s --driver=hyperkit
    minikube addons enable metrics-server
    ```
     
    Docker driver will also be starting the service without any issue.
   
    But use **hyperkit** as driver if you'd like to run the load test. Docker driver may be slower performance.
   
- Deploy the service
    ```
    cd basic_hosting_demo
    kubectl apply -f api.yaml
    kubectl apply -f autoscale.yaml (optional, it won't trigger the autosacle at this point)
  
    kubectl get pods
    kubectl get svc baisc-hosting-demo-svc
    ```
- obtain the url
    ```
    minikube service baisc-hosting-demo-svc --url
    example output:  http://192.168.65.2:32130
    ```
- curl
    ```
   curl -X POST "http://192.168.65.2:32130/api/v1/query/predict" -d '{"query": "magnetic glow rods"}' -H "Content-Type: application/json"
    ```


## Load testing
- Load testing are under the `load_test` directory.
- load testing is done using [locust](https://locust.io/).
- To run the load test, first install locust
    ```
    pip install locust
    ```

minikube start --cpus 4 --memory 8000 --extra-config=kubelet.housekeeping-interval=10s
minikube dashboard
minikube addons enable metrics-server
kubectl delete deployment  baisc-hosting-demo
