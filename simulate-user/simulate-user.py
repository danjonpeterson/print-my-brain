#!/usr/bin/env python3

import argparse
import boto3
from boto3.s3.transfer import TransferConfig
import tempfile
import os


parser = argparse.ArgumentParser(description='Simulate a print-my-brain user, from the HCP data')
parser.add_argument('--user', help='user name',default='164030')
args = parser.parse_args()

# TODO: randomly select user if none given




# setup HCP S3
f = open('/Users/danjonpeterson/insight/credentials/HCP_keys.txt')
hcp_keys_text = f.readlines()
hcp_access_key_id = hcp_keys_text[1].split("=")[1].strip('\n')
hcp_secret_access_key = hcp_keys_text[2].split("=")[1].strip('\n')

source_client = boto3.client('s3',aws_access_key_id=hcp_access_key_id,aws_secret_access_key=hcp_secret_access_key)

# setup temp dir

tmpdir = tempfile.gettempdir()
print(tmpdir)

# copy data from HCP S3 to tmp

source_client.download_file('hcp-openaccess','HCP/'+args.user+'/unprocessed/3T/T1w_MPR1/164030_3T_T1w_MPR1.nii.gz', ''+tmpdir+'/hcp'+args.user+'.nii.gz')


# setup print-my-brain S3 (uses environment variables for credentials)

desination_client = boto3.client('s3')


# copy data from tmp to print-my-brain S3. increase multipart threshold to 5gb

desination_client.upload_file(tmpdir+'/hcp'+args.user+'.nii.gz','print-my-brain', 'input/user-hcp'+args.user+'.nii.gz',Config=TransferConfig(multipart_threshold=5*(1024 ** 3)))

# cleanup tmp file

os.remove(tmpdir+'/hcp'+args.user+'.nii.gz')



# Make entry into dynamodb table
