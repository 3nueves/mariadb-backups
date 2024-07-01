#!/bin/bash

# run image
docker run --name mariadb-backup --rm \
-v /var/log/:/var/log \
-e DB_EXCLUDE="mysql performance_schema information_schema" \
-e DB_PASSWORD=password \
-e DB_USER=user \
-e DB_HOST="10.50.0.212" \
-e MINIO_HOST="10.20.0.83:9000" \
-e MINIO_ACCESS_KEY=minio \
-e MINIO_SECRET_KEY=password \
-e MINIO_BUCKET_NAME=backup-all-dbs \
-it mariadb-backup:v2.0.0

# build image
# docker build -t mariadb-backup:v1.0.0 .
