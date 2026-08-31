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