# image-transformer

## Setup

### Helm charts

Install

```
helm install image-transformer charts/image-transformer -n image-transformer --create-namespace --set postgres.password=postgres
```

Verify
```
kubectl get pods,pvc,statefulsets -n image-transformer
```


### Backend image

`kind` doesn't see your local Docker daemon's images automatically — after any change to
`backend/`, rebuild the image and load it into the cluster before upgrading, otherwise the
running pod keeps the old code (builds are cache-fast, so just always rebuild):

```
docker build -t image-transformer-backend:local backend
kind load docker-image image-transformer-backend:local --name lab
```

Upgrading
```
helm upgrade image-transformer charts/image-transformer -n image-transformer

```
Verify s3 bucket + sqs
```
kubectl logs job/floci-bootstrap -n image-transformer
```

```
make_bucket: uploads
{
    "QueueUrl": "http://localhost:4566/000000000000/image-processing"
}
Floci bootstrap complete: bucket=uploads queue=image-processing
```



### Development

for testing backend forward port to host
```
kubectl port-forward -n image-transformer svc/backend 8000:8000

```


processing image
```
kubectl port-forward -n image-transformer svc/backend 8000:8000

```


upload hero.png
```
curl -X POST http://localhost:8000/uploads -F "file=hero.png;type=image/png"

```

checking processor
```
kubectl logs -n image-transformer deploy/processor -f
```



download from bucket

```
kubectl port-forward -n image-transformer svc/floci 4566:4566
```
```
curl -o thumb.png "http://localhost:4566/uploads/thumbnails/<id>/hero.png"

```


# build all three images
```
docker build -t image-transformer-backend:local backend
docker build -t image-transformer-processor:local processor
docker build -t image-transformer-frontend:local frontend
```

# load them into the kind
```
kind load docker-image image-transformer-backend:local image-transformer-processor:local image-transformer-frontend:local --name lab
```
# upgrade the release (reuses previously-set values, e.g. postgres.password, by default)
```
helm upgrade image-transformer charts/image-transformer -n image-transformer
```

# forward the frontend to your host
```
kubectl port-forward -n image-transformer svc/frontend 8080:80
```

### Ingress

The kind cluster needs to be created with `extraPortMappings` for 80/443 and the
`ingress-ready=true` node label before ingress-nginx will work — recreate it with the
committed config (this deletes and rebuilds the cluster, so any images loaded into it
will need `kind load docker-image` again):

```
kind delete cluster --name lab
kind create cluster --name lab --config kind-config.yaml
```

Install ingress-nginx (kind-specific manifest — deploys the controller with hostPort
80/443 on the node labeled `ingress-ready=true`):

```
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
```

It is required to set `nodeSelector: {ingress-ready: "true"}` on the
controller Deployment, so it can land on a worker node with 80/443
`extraPortMappings` from `kind-config.yaml`. Force it onto
the control-plane node:

```
kubectl patch deployment ingress-nginx-controller -n ingress-nginx --type=json \
  -p='[{"op":"add","path":"/spec/template/spec/nodeSelector/ingress-ready","value":"true"}]'
kubectl wait --namespace ingress-nginx --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=180s
```

Rebuild the app images, load them into the fresh cluster, and install the release (it's a new
cluster so `helm install`,):

```
docker build -t image-transformer-backend:local backend
docker build -t image-transformer-processor:local processor
docker build -t image-transformer-frontend:local frontend
kind load docker-image image-transformer-backend:local image-transformer-processor:local image-transformer-frontend:local --name lab
helm install image-transformer charts/image-transformer -n image-transformer --create-namespace --set postgres.password=postgres
kubectl get pods,ingress -n image-transformer
```

Test in the browser at `http://localhost/` — the frontend is served at `/`, and its
uploads go through `http://localhost/api/uploads` (routed straight to the backend
Service by the ingress, bypassing the frontend's own nginx `/api` proxy).
