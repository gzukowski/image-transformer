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