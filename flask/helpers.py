import boto3, botocore
from config import S3_KEY, S3_SECRET, S3_BUCKET, BATCH_JOB_DEFINITION

s3 = boto3.client(
   "s3",
   aws_access_key_id=S3_KEY,
   aws_secret_access_key=S3_SECRET
)

batch = boto3.client(
   "batch",
   aws_access_key_id=S3_KEY,
   aws_secret_access_key=S3_SECRET
)

def get_url_to_s3(filename):
    """ resource: name of the file to download"""

    print(filename)

    url = s3.generate_presigned_url('get_object', Params = {'Bucket': 'print-my-brain', 'Key': filename}, ExpiresIn = 500)
    return url


def upload_file_to_s3(file, bucket_name, acl="public-read"):

    """
    Docs: http://boto3.readthedocs.io/en/latest/guide/s3.html
    """

    file.filename="input/{}".format(file.filename)

    try:
        print("file",file)
        print("bucket_name",bucket_name)
        print("file.filename",file.filename)
        s3.upload_fileobj(
            file,
            "print-my-brain",
            file.filename,
            ExtraArgs={
#                "ACL": acl,
                "ContentType": file.content_type
            }
        )

    except Exception as e:
        print("Something Happened: ", e)
        return e

    return "http://print-my-brain.s3.amazonaws.com/{}".format(file.filename)

def submit_batch_job(username):

    response = batch.submit_job(jobName=username,
                            jobQueue='print-my-brain-job-queue',
                            jobDefinition=BATCH_JOB_DEFINITION,
                            containerOverrides={
                                "environment": [ 
                                    {"name": "BRAIN_PRINTER_USER", "value": username}
                                ]
                            })

    print(response)
    return response['jobId']

def is_processing_complete(username):
    try:
        result=s3.head_object(Bucket='print-my-brain',Key='output/user-'+username+'-lh.stl')
    except botocore.exceptions.ClientError as ex:
        if ex.response['Error']['Code'] == '404':
            return False
    return True



#TODO: filename checking
def allowed_file(filename):
	return True