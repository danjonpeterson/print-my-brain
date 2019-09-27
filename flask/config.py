import os

S3_BUCKET                 = os.environ.get("print-my-brain")
S3_KEY                    = os.environ.get("AWS_ACCESS_KEY_ID")
S3_SECRET                 = os.environ.get("AWS_SECRET_ACCESS_KEY")
S3_LOCATION               = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)

SECRET_KEY                = os.urandom(32)
DEBUG                     = True
PORT                      = 5000

