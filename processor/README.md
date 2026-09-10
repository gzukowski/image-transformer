# processor

Long-running worker: long-polls the SQS queue, fetches uploaded images from S3 (Floci),
generates a thumbnail with Pillow, uploads it back to S3, and updates the upload's status/
thumbnail in Postgres.

## Development

```
uv sync
uv run processor
```

Requires the same `DB_*` env vars as `backend`, plus:

- `AWS_ENDPOINT_URL`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`
- `S3_BUCKET_NAME`, `SQS_QUEUE_NAME`
- `THUMBNAIL_MAX_SIZE` (optional, default `256`)
