import logging
import boto3
from botocore.exceptions import ClientError
import os
import time

def upload_file(s3_client, file_name, bucket, object_name=None):
    if object_name is None:
        object_name = os.path.basename(file_name)

    try:
        s3_client.upload_file(file_name, bucket, object_name)

    except ClientError as e:
        logging.error(e)
        return False
    return True

if __name__ == '__main__':
    previous = {}
    s3_client = boto3.client(
        's3',
        region_name='nyc3',
        endpoint_url='https://nyc3.digitaloceanspaces.com',
        aws_access_key_id=os.environ.get('KEY'),
        aws_secret_access_key=os.environ.get('SECRET')

    )
    dirname = './output/linksys/'
    bucket = 'firmamoredata'
    while True:
        if len(os.listdir(dirname)) == 0:
            break
        for f in os.listdir(dirname):
            if os.path.isfile(os.path.join(dirname, f)):
                s = os.stat(os.path.join(dirname, f))
                last_modification = s.st_mtime
                try:
                    if previous[f] == last_modification:
                        logging.info('sending %s' % os.path.join(dirname, f))
                        upload_file(s3_client,
                                    os.path.join(dirname, f),
                                    bucket
                        )
                        os.remove(os.path.join(dirname, f))
                except KeyError:
                    previous[f] = last_modification
        time.sleep(15)
