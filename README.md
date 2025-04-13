## Project Summary

This project demonstrates how to deploy a single FastAPI application to Kubernetes (Minikube) and use Nginx Ingress to expose different API endpoints based on the requested hostname. It shows how to configure Ingress rules to rewrite URL paths, allowing `apiforfrontend.com/*` to route to the `/api-for-frontend/*` prefix and `apiforbackend.com/*` to route to the `/api-for-backend/*` prefix within the same application instance.


### Result
![Redirection working](docs/redirection-working.png)


### Project setup and Request flowchart
```mermaid
graph TD
    A[Developer] --> B(Build Docker Image Locally);
    B --> C(Start Minikube);
    C --> D(Enable Ingress Addon);
    A --> E(Get Minikube IP);
    E --> F(Update /etc/hosts);
    A --> G(Set Docker Env to Minikube);
    G --> H(Build Image Inside Minikube);
    H --> I(Deploy App with Helm);
    J[User] --> K["Send Request<br>(e.g., curl apiforfrontend.com/v1/hello)"];
    F --> K;
    K --> L(Request hits Minikube IP);
    D --> L;
    L --> M(Ingress Controller Receives Request);
    I --> M;
    M --> N["Route based on Host<br>(apiforfrontend.com)"];
    N --> O["Rewrite Path<br>(/v1/hello -> /api-for-frontend/v1/hello)"];
    O --> P(Forward to Service);
    P --> Q(Service routes to Pod);
    Q --> R(FastAPI App Receives Request);
    R --> S["Match Route<br>(/api-for-frontend/v1/hello)"];
    S --> T(Execute Handler Function);
    T --> U(Generate Response);
    U --> Q;
    Q --> P;
    P --> M;
    M --> J;

    style F fill:#ff4d00,stroke:#333,stroke-width:2px
    style G fill:#ff4d00,stroke:#333,stroke-width:2px
```

# Request sequence diagram

```mermaid
sequenceDiagram
    participant User
    participant OS /etc/hosts as OS/Hosts
    participant Minikube Ingress as Ingress
    participant K8s Service as Service
    participant FastAPI Pod as Pod

    User->>OS/Hosts: Resolve apiforfrontend.com
    OS/Hosts-->>User: Minikube IP
    User->>Ingress: GET /v1/hello (Host: apiforfrontend.com)
    Ingress->>Ingress: Match Ingress rule for host
    Ingress->>Ingress: Rewrite path to /api-for-frontend/v1/hello
    Ingress->>Service: GET /api-for-frontend/v1/hello
    Service->>Pod: GET /api-for-frontend/v1/hello
    Pod->>Pod: Match route /api-for-frontend/v1/hello
    Pod->>Pod: Execute frontend_hello()
    Pod-->>Service: 200 OK {"message":"This is frontend API"}
    Service-->>Ingress: 200 OK {"message":"This is frontend API"}
    Ingress-->>User: 200 OK {"message":"This is frontend API"}
```

### Run it locally

Build the image
```shell
docker build -t k8s-multiple-routers .
```

Install minikube (if you don't have it) and start it
```shell
sudo apt install minikube # Debian/Ubuntu
minikube start
```
![Minikube start](docs/minikube-start.png)

get the minikube ip in your local network
```shell
minikube ip
```

Add this two lines to your `/etc/hosts` (Replace minikube's ip)
```shell
minikube-ip-here apiforfrontend.com
minikube-ip-here apiforbackend.com
```

To build images inside minikube. It tells your local docker CLI  to talk to Minikube's Docker, so an image build, builds it inside Minikube and kubectl deployment can find it
```shell
eval $(minikube docker-env)
```

The previous command does some changes to some environment variables in your machine, so if you want to reset back to normal, run:
```shell
eval $(minikube docker-env -u)
```

If you do `docker images` after running each one of the previous two commands you should see two different list of images, here you can see how it looks inside minikube
![List docker images](docs/list-docker-images.png)

Install Helm
```shell
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh
rm get_helm.sh # if you want remove helm's installation script
```

Enable the Nginx Ingress Controller addon. This installs the controller needed to manage external access to services based on Ingress rules.
```shell
minikube addons enable ingress
```
![Enable ingress](docs/enable-ingress.png)

Deploy the application using Helm
```shell
helm install k8s-multiple-routers ./charts/k8s-mutiple-routers
```

Then you can acces to your two separated domains
```shell
curl http://apiforbackend.com/v1/hello
{"message":"This is backend API"}

curl http://apiforfrontend.com/v1/hello
{"message":"This is frontend API"}
```