#!/usr/bin/env python3

""" User Simulator Script

This scripts simulates a user visiting http://geminaltech.com/print-my-brain,
and submitting a job to the AWS Batch queue, using publicly available HCP data.

About the Human Connectome Project: http://www.humanconnectomeproject.org/

It assumes s3 access to the print-my-brain buckets, and you have gained access
to the open-access HCP dataset as described here:
https://wiki.humanconnectome.org/display/PublicData/How+to+Get+Access+to+the+HCP+OpenAccess+Amazon+S3+Bucket

And put the credenials in a file formatted like so:
USERNAME=danjonpeterson
HCP_ACCESS_KEY_ID=XXXXXXXXXXXXXXXXXXXX
HCP_AWS_SECRET_ACCESS_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

This script only interacts with the backend, and does not test the frontend
webserver

You can pass it a specified HCP subject number, or let it randomly select from
a file called subjects_list in the same directory as this script

"""

import argparse
import tempfile
import os
import sys
import random
import logging
import botocore
import boto3
from boto3.s3.transfer import TransferConfig

HCP_CREDENTIALS_FILE = '/Users/danjonpeterson/insight/credentials/HCP_keys.txt'

# setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = logging.FileHandler('simulate-user.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# log unhandled exceptions
def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
    """Handler for unhandled exceptions that will write to the logs"""
    if issubclass(exc_type, KeyboardInterrupt):
        # if it's a ctl-C call the default excepthook saved at __excepthook__
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_unhandled_exception

# parse arguments
parser = argparse.ArgumentParser(description='Simulate a print-my-brain user, from HCP data')
parser.add_argument('--user', help='user name', default='random')
args = parser.parse_args()

logger.info('setup HCP S3')

f = open(HCP_CREDENTIALS_FILE)
hcp_keys_text = f.readlines()
hcp_access_key_id = hcp_keys_text[1].split("=")[1].strip('\n')
hcp_secret_access_key = hcp_keys_text[2].split("=")[1].strip('\n')


source_client = boto3.client('s3', aws_access_key_id=hcp_access_key_id,
                             aws_secret_access_key=hcp_secret_access_key)

logger.info('INFO: setup print-my-brain S3')

desination_client = boto3.client('s3')

def is_new_subject(subject):
    try:
        result = desination_client.head_object(Bucket='print-my-brain',
                                               Key=f'input/user-hcp{subject}.nii.gz')
    except botocore.exceptions.ClientError as ex:
        if ex.response['Error']['Code'] == '404':
            return True
    return False

def get_random_subject():
    with open(os.path.join(sys.path[0], 'subject_list.txt'), 'r') as file:
        subject_list = file.read().splitlines()

    subject = random.choice(subject_list)
    if is_new_subject(subject):
        return subject
    else:
        logger.info(f'randomly selected HCP subject: {subject} has already '
                    'been run. getting a new one')
        return get_random_subject()


if args.user == 'random':
    args.user = get_random_subject()

logger.info('user: {}'.format(args.user))

logger.info('setup temp dir')

tmpdir = tempfile.gettempdir()

logger.info(f'copy data from HCP S3 to tmpdir: {tmpdir}')

source_client.download_file('hcp-openaccess',
                            f'HCP/{args.user}/unprocessed/3T/T1w_MPR1/{args.user}_3T_T1w_MPR1.nii.gz',
                            f'{tmpdir}/hcp{args.user}.nii.gz')

logger.info('copy data from tmp to print-my-brain S3')

# increase multipart threshold to 5gb
desination_client.upload_file(f'{tmpdir}/hcp{args.user}.nii.gz',
                              'print-my-brain',
                              f'input/user-hcp{args.user}.nii.gz',
                              Config=TransferConfig(multipart_threshold=5*(1024 ** 3)))

logger.info('cleanup tmp file')

os.remove(f'{tmpdir}/hcp{args.user}.nii.gz')


logger.info('submitting job')

batch = boto3.client('batch')

response = batch.submit_job(jobName=f'hcp{args.user}',
                            jobQueue='print-my-brain-job-queue',
                            jobDefinition='brain-printer-live-run',
                            containerOverrides={
                                'environment': [{
                                    'name': 'BRAIN_PRINTER_USER',
                                    'value': f'hcp{args.user}'
                                }]
                            })
jobId = response['jobId']

logger.info(f'for user {args.user} Job ID is {jobId}')










