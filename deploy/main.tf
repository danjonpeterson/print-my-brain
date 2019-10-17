# Deploys clould infrastructure for print-my-brain project
#
# working from https://github.com/jkahn117/aws-batch-image-processor as an example
# https://medium.com/@joshua.a.kahn/understanding-aws-batch-a-brief-introduction-and-sample-project-5a3885dda0ce

#
# VARIABLES
#
variable "aws_region" {
  description = "AWS region to launch brain_printer"
  default = "us-west-2"
}


#
# PROVIDER
#
provider "aws" {
  region = "${var.aws_region}"
  version = "~> 2.29"
}


#
# DATA
#

# retrieves the default vpc for this region
data "aws_vpc" "default" {
  default = true
}

# retrieves the subnet ids in the default vpc
data "aws_subnet_ids" "all" {
  vpc_id = "${data.aws_vpc.default.id}"
}

resource "aws_iam_role" "instance-role" {
  name = "aws-batch-print-my-brain-role"
  path = "/print-my-brain/"
  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement":
    [
      {
          "Action": "sts:AssumeRole",
          "Effect": "Allow",
          "Principal": {
            "Service": "ec2.amazonaws.com"
          }
      }
    ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "instance-role" {
  role = "${aws_iam_role.instance-role.name}"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

resource "aws_iam_instance_profile" "instance-role" {
  name = "aws-batch-print-my-brain-role"
  role = "${aws_iam_role.instance-role.name}"
}

resource "aws_iam_role" "aws-batch-service-role" {
  name = "aws-batch-service-role"
  path = "/print-my-brain/"
  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement":
    [
      {
          "Action": "sts:AssumeRole",
          "Effect": "Allow",
          "Principal": {
            "Service": "batch.amazonaws.com"
          }
      }
    ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "aws-batch-service-role" {
  role = "${aws_iam_role.aws-batch-service-role.name}"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBatchServiceRole"
}

resource "aws_security_group" "print-my-brain-batch" {
  name = "aws-batch-print-my-brain-security-group"
  description = "AWS Batch Security Group for print-my-brain"
  vpc_id = "${data.aws_vpc.default.id}"

  egress {
    from_port       = 0
    to_port         = 65535
    protocol        = "tcp"
    cidr_blocks     = [ "0.0.0.0/0" ]
  }
}

resource "aws_batch_compute_environment" "print-my-brain-compute-environment" {
  compute_environment_name = "print-my-brain-compute-environment"
  compute_resources {
    instance_role = "${aws_iam_instance_profile.instance-role.arn}"
    instance_type = [
      "optimal"
    ]
    #RETURN TO THIS
    max_vcpus = 6
    desired_vcpus = 2
    min_vcpus = 0
    security_group_ids = [
      "${aws_security_group.print-my-brain-batch.id}"
    ]
    #TODO: read dynamically
    subnets = [
      "subnet-3caaba45"
    ]
    type = "EC2"
  }
  service_role = "${aws_iam_role.aws-batch-service-role.arn}"
  type = "MANAGED"
  depends_on = [ "aws_iam_role_policy_attachment.aws-batch-service-role" ]
}

resource "aws_batch_job_queue" "print-my-brain-job-queue" {
  name = "print-my-brain-job-queue"
  state = "ENABLED"
  priority = 1
  compute_environments = [ 
    "${aws_batch_compute_environment.print-my-brain-compute-environment.arn}"
  ]
}

# 
# This will throw an error if the bucket already exists
#

resource "aws_s3_bucket" "print-my-brain" {
  bucket = "print-my-brain"
}



# 
# This will throw an error if the table already exists
#

resource "aws_dynamodb_table" "print-my-brain" {
  name = "print-my-brain"
  hash_key = "userid"

  read_capacity = 5
  write_capacity = 5

  attribute {
    name = "userid"
    type = "S"
  }
}


resource "aws_iam_role" "job-role" {
  name = "aws-batch-print-my-brain-job-role"
  path = "/print-my-brain/"
  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement":
    [
      {
          "Action": "sts:AssumeRole",
          "Effect": "Allow",
          "Principal": {
            "Service": "ecs-tasks.amazonaws.com"
          }
      }
    ]
}
EOF
}


resource "aws_iam_policy" "job-policy" {
  name = "aws-batch-print-my-brain-job-policy"
  path = "/print-my-brain/"
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "dynamodb:PutItem"
      ],
      "Effect": "Allow",
      "Resource": "${aws_dynamodb_table.print-my-brain.arn}"
    },
    {
      "Action": [
        "s3:Get*"
      ],
      "Effect": "Allow",
      "Resource": [
        "${aws_s3_bucket.print-my-brain.arn}",
        "${aws_s3_bucket.print-my-brain.arn}/*"
      ]
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "job-role" {
  role = "${aws_iam_role.job-role.name}"
  policy_arn = "${aws_iam_policy.job-policy.arn}"
}



resource "aws_batch_job_definition" "brain_printer" {
  name = "brain_printer"
  type = "container"

  container_properties = <<CONTAINER_PROPERTIES
{
    "command": ["/brain_printer/run.sh", "-u","tf-batch-test","-t"],
    "image": "danjonpeterson/brain_printer",
    "memory": 8048,
    "vcpus": 2,
    "volumes": [
      {
        "host": {
          "sourcePath": "/tmp"
        },
        "name": "tmp"
      }
    ],
    "environment": [
        {"name": "VARNAME", "value": "VARVAL"}
    ],
    "mountPoints": [
        {
          "sourceVolume": "tmp",
          "containerPath": "/tmp",
          "readOnly": false
        }
    ],
    "ulimits": [ ]
}
CONTAINER_PROPERTIES
}

