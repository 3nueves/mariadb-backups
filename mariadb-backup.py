""" Module to do db backups  """

import os
import gzip
import shutil
import logging
import datetime
from subprocess import PIPE, CalledProcessError, run

from minio import Minio
from minio.error import S3Error

# Logging
logger = logging.getLogger('bkup')
logging.basicConfig(handlers=[logging.StreamHandler()],
                    format="%(asctime)s - %(name)s - "
                           "[%(levelname)s] - %(message)s", 
                    level=logging.INFO)


# Env to mariadb connection
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_exclude = os.getenv("DB_EXCLUDE")


# Env to minio connection
minio_host = os.getenv("MINIO_HOST")
minio_access_key = os.getenv("MINIO_ACCESS_KEY")
minio_secret_key = os.getenv("MINIO_SECRET_KEY")
minio_bucket_name = os.getenv("MINIO_BUCKET_NAME")


# Build command to get all dbs
mysql_list_dbs = ['mysql',
                    '-u', db_user,
                    '-p' + db_password,
                    '-h', db_host, 
                    '--skip-column-names', 
                    '--execute',
                    'show databases;'
                ]

def save_backup_in_minio(local_file_path, object_name_in_minio):
    """ Create client and Upload backups """
    minio_client = Minio(
        minio_host,
        access_key=minio_access_key,
        secret_key=minio_secret_key,
        secure=False  # Change to True if your MinIO server uses HTTPS
    )
        # Check if the bucket exists, create it if not
    if not minio_client.bucket_exists(minio_bucket_name):
        minio_client.make_bucket(minio_bucket_name)

    try:
        # Upload the file to MinIO
        minio_client.fput_object(
            minio_bucket_name,
            object_name_in_minio,
            local_file_path
        )
    except S3Error as err:
        logger.error("> ##MinIO Error: %s", err)

def get_dbs():
    """ Get all databases """
    try:
        dbs = run(mysql_list_dbs, check=True, stdout=PIPE, stderr=PIPE, text=True)
        return filter(None, dbs.stdout.split(os.linesep))
    except CalledProcessError as err:
        logger.error("> ##Error during backup: %s", err)
        exit()


def exclude_dbs(databases):
    """ Exclude databases """
    return filter(lambda db: db not in db_exclude, databases)


def build_file_backup(datab):
    """ Build file to save dbs """
    return f'backup_{datab}_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.sql'


def gzip_dbs(file):
    """ Compress dbs """
    try:
        with open(file, 'rb') as file_in:
            with gzip.open(file + "." + "gz", 'wb') as file_out:
                shutil.copyfileobj(file_in, file_out)
    except FileNotFoundError:
        logger.warning("> Warning, the file '%s' does not exist.", file)


def remove_file(file_path):
    """ Delete sql file """
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except FileNotFoundError as file:
            logger.error("> Error while removing file: %s", file)
    else:
        logger.warning("> File '%s' does not exist.", file_path)


def dump_dbs(datab, bk):
    """ Backup dbs with mysqldump """
    return run(['mysqldump',
                '-h', db_host, 
                '-u', db_user, 
                '-p' + db_password, 
                datab
                ], stdout=bk, stderr=PIPE, check=True)


def exec_backups(databases):
    """ Execute backups """
    for db_name in databases:
        backup_file = build_file_backup(db_name)

        with open(backup_file, mode='w', encoding="UTF8") as backup:
            try:
                dump_dbs(db_name, backup)
                gzip_dbs(backup_file)
                remove_file(backup_file)
                save_backup_in_minio(backup_file + "." + "gz", backup_file + "." + "gz")
                remove_file(backup_file + "." + "gz")
                logger.info('> %s - ok', db_name)

            except CalledProcessError as errors:
                logger.error("> Error during backup: %s", errors)
                remove_file(backup_file)


def main():
    """ Main process to create backups """
    logger.info("> Starting bkup...")
    logger.info("> Load configuration...")
    logger.info('> Mariadb host: %s', db_host)
    logger.info('> Minio host: %s', minio_host)
    logger.info('> Minio bucket: %s', minio_bucket_name)
    logger.info('> Exclude databases: %s', db_exclude)
    logger.info("> Init Backups...")
    exec_backups(exclude_dbs(get_dbs()))
    logger.info("> Finish Backups...")

if __name__ == '__main__':
    main()
