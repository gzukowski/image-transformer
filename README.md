# image-transformer

## Setup

### Helm charts

Install

```
helm install image-transformer charts/image-transformer -n image-transformer --create-namespace --set postgres.password=postgres --set minio.rootPassword=minio123
```

