"""Helper functions for the print-my-brain frontend. These handle most of the
   communication between AWS services and and web-app. Also some file checking
"""

import boto3 
import botocore
from config import (
    S3_KEY,
    S3_SECRET,
    S3_BUCKET,
    BATCH_JOB_DEFINITION,
    S3_URL_EXPIRATION_TIME
    )

s3 = boto3.client('s3',
                  aws_access_key_id=S3_KEY,
                  aws_secret_access_key=S3_SECRET
                  )

batch = boto3.client('batch',
                     aws_access_key_id=S3_KEY,
                     aws_secret_access_key=S3_SECRET
                     )

def get_url_to_s3(filename):
    """Get a self-signed and expiring url to an object in the S3 bucket"""
    print(filename)

    url = s3.generate_presigned_url('get_object',
                                    Params={
                                        'Bucket': S3_BUCKET,
                                        'Key': filename
                                        },
                                    ExpiresIn=S3_URL_EXPIRATION_TIME
                                    )
    return url


def upload_file_to_s3(file):
    """Upload the input file to the S3 bucket"""
    file.filename = f'input/{file.filename}'

    try:
        print('file', file)
        print('bucket_name', S3_BUCKET)
        print('file.filename', file.filename)
        s3.upload_fileobj(
            file,
            S3_BUCKET,
            file.filename,
            ExtraArgs={
                'ContentType': file.content_type
            }
        )

    except Exception as e:
        print('Something Happened: ', e)
        return e

    return f'http://print-my-brain.s3.amazonaws.com/{file.filename}'

def submit_batch_job(username):
    """Submit the job to the AWS Batch queue"""
    response = batch.submit_job(jobName=username,
                                jobQueue='print-my-brain-job-queue',
                                jobDefinition=BATCH_JOB_DEFINITION,
                                containerOverrides={
                                    'environment': [
                                        {'name': 'BRAIN_PRINTER_USER',
                                         'value': username}
                                    ]
                                })

    print(response)
    return response['jobId']

def is_processing_complete(username) -> bool:
    """Check if we have files for this user"""
    try:
        result = s3.head_object(Bucket='print-my-brain', Key=f'output/user-{username}-lh.stl')
    except botocore.exceptions.ClientError as ex:
        if ex.response['Error']['Code'] == '404':
            return False
    return True

def is_allowed_file(filename) -> bool:
    """Check file name extension"""
    return filename.endswith('.nii.gz')
