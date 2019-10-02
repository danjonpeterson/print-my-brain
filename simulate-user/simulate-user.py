#!/usr/bin/env python3

import argparse
import boto3
import botocore
from boto3.s3.transfer import TransferConfig
import tempfile
import os, sys
import random


parser = argparse.ArgumentParser(description='Simulate a print-my-brain user, from the HCP data')
parser.add_argument('--user', help='user name',default='random')
args = parser.parse_args()

print('INFO: setup HCP S3')

f = open('/Users/danjonpeterson/insight/credentials/HCP_keys.txt')
hcp_keys_text = f.readlines()
hcp_access_key_id = hcp_keys_text[1].split("=")[1].strip('\n')
hcp_secret_access_key = hcp_keys_text[2].split("=")[1].strip('\n')


source_client = boto3.client('s3',aws_access_key_id=hcp_access_key_id,aws_secret_access_key=hcp_secret_access_key)

print('INFO: setup print-my-brain S3 (uses environment variables for credentials)')

desination_client = boto3.client('s3')

def is_new_subject(subject):
    try:
        result=desination_client.head_object(Bucket='print-my-brain',Key='input/user-hcp'+subject+'.nii.gz')
    except botocore.exceptions.ClientError as ex:
        if ex.response['Error']['Code'] == '404':
            return True
    return False

def get_random_subject():
	
    with open(os.path.join(sys.path[0], "subject_list.txt"), "r") as f:
    	subject_list = f.read().splitlines()

    subject=random.choice(subject_list)
    if is_new_subject(subject):
    	return subject
    else:
    	return get_random_subject()


if args.user=='random':
	args.user=get_random_subject()

print('INFO: user:' + args.user)


print('INFO: setup temp dir')

tmpdir = tempfile.gettempdir()

print('INFO: copy data from HCP S3 to tmpdir:' + tmpdir)

source_client.download_file('hcp-openaccess','HCP/'+args.user+'/unprocessed/3T/T1w_MPR1/'+args.user+'_3T_T1w_MPR1.nii.gz', ''+tmpdir+'/hcp'+args.user+'.nii.gz')


print('INFO: copy data from tmp to print-my-brain S3')

# increase multipart threshold to 5gb

desination_client.upload_file(tmpdir+'/hcp'+args.user+'.nii.gz','print-my-brain', 'input/user-hcp'+args.user+'.nii.gz',Config=TransferConfig(multipart_threshold=5*(1024 ** 3)))

print('INFO: cleanup tmp file')

os.remove(tmpdir+'/hcp'+args.user+'.nii.gz')


print('INFO: submitting job')

batch = boto3.client('batch')

response = batch.submit_job(jobName='hcp'+args.user,
                            jobQueue='print-my-brain-job-queue',
                            jobDefinition='brain-printer-live-run',
                            containerOverrides={
                                "environment": [ 
                                    {"name": "BRAIN_PRINTER_USER", "value": 'hcp'+args.user}
                                ]
                            })

print("Job ID is {}.".format(response['jobId']))


def get_random_subject():

    with open(os.path.join(sys.path[0], "subject_list.txt"), "r") as f:
    	subject_list = f.read().splitlines()

    subject=random_choice(subjects)
    #TODO: check if we've done this one
    return subject









