"""AWS utilities"""

import subprocess
import sys
import json

aws_cmd = "/usr/local/bin/aws"


def has_key_pair(key_pair, require=False):
    with open("/dev/null", 'w') as devnull:
        cmd = [aws_cmd, "ec2", "describe-key-pairs", "--key-names", key_pair]
        status = subprocess.call(cmd, stdout=devnull, stderr=devnull)
    success = status == 0

    if require and not success:
        print("""
Error: unable to find key-pair '{}'.
Perhaps the key-pair does not exist, or you do not have access to it?
(You can check this with `aws ec2 describe-key-pairs`.)
""".strip().format(key_pair))
        sys.exit(1)
    return success


def has_bucket(bucket, require=False):
    with open("/dev/null", 'w') as devnull:
        cmd = [aws_cmd, 's3api', 'list-buckets']
        output = subprocess.check_output(cmd, stderr=devnull)
    buckets = json.loads(output)['Buckets']
    bkt_names = [bkt['Name'] for bkt in buckets]
    success = bucket in bkt_names

    if require and not success:
        print("""
    Error: unable to find bucket '{}'.
    Perhaps the bucket does not exist, or you do not have access to it?
    (You can check this with `aws s3api list-buckets`.)
    """.strip().format(bucket))
        sys.exit(1)
    return success


def has_s3_object(bucket, path, require=False):
    s3_obj = "s3://{}/{}".format(bucket, path.lstrip("/"))
    with open("/dev/null", 'w') as devnull:
        cmd = [aws_cmd, 's3', 'ls', s3_obj]
        output = subprocess.check_output(cmd, stderr=devnull)
    success = len(output) > 0

    if require and not success:
        print("""
Error: unable to find S3 object '{}' in bucket '{}'.
Perhaps the bucket or file does not exist, or you do not have access to it?
(You can check this with `aws s3api list-buckets` and `aws s3 ls S3_PATH`.)
""".strip().format(path, bucket))
        sys.exit(1)
    return success
