#!/bin/bash

# run image
docker run --name mariadb-backup --rm \
-v /var/log/:/var/log \
-e DB_EXCLUDE="mysql performance_schema information_schema" \
-e DB_PASSWORD=wzkehrAjyIP3hsaH \
-e DB_USER=root \
-e DB_HOST="10.40.0.212" \
-e MINIO_HOST="10.0.0.83:9000" \
-e MINIO_ACCESS_KEY=minio \
-e MINIO_SECRET_KEY=yVyI54Lh9QgH \
-e MINIO_BUCKET_NAME=backup-all-dbs \
-it mariadb-backup:v2.0.0
# -it registry.gitlab.com/invisible_bits/docker/mysql-backups:latest

# build image
# docker build -t mariadb-backup:v1.0.0 .
