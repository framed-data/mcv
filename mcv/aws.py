'''AWS utilities'''

import subprocess
import os
import json

aws_cmd = '/usr/local/bin/aws'

def my_assert(cond, message):
    if not cond:
        print message
        os._exit(1)

def has_key_pair(key_pair):
    with open('/dev/null', 'w') as devnull:
        cmd = [aws_cmd, 'ec2', 'describe-key-pairs', '--key-names', key_pair]
        return subprocess.call(cmd, stdout=devnull, stderr=devnull) == 0

def has_bucket(bucket):
    with open('/dev/null', 'w') as devnull:
        cmd = [aws_cmd, 's3api', 'list-buckets']
        output = subprocess.check_output(cmd, stderr=devnull)
    buckets = json.loads(output)['Buckets']
    bkt_names = [ bkt['Name'] for bkt in buckets ]
    return bucket in bkt_names

def has_s3_object(bucket, path):
    s3_obj = 's3://%s/%s' % (bucket, path.lstrip('/'))
    with open('/dev/null', 'w') as devnull:
        cmd = [aws_cmd, 's3', 'ls', s3_obj]
        output = subprocess.check_output(cmd, stderr=devnull)
    return len(output) > 0

def assert_key_pair(key_pair):
    my_assert(has_key_pair(key_pair), '''
Error: unable to find key-pair '%s'.
Perhaps the key-pair does not exist, or you do not have access to it?
(You can check this with `aws ec2 describe-key-pairs`.)
'''.strip() % key_pair)

def assert_bucket(bucket):
    my_assert(has_bucket(bucket), '''
Error: unable to find bucket '%s'.
Perhaps the bucket does not exist, or you do not have access to it?
(You can check this with `aws s3api list-buckets`.)
'''.strip() % bucket)

def assert_s3_object(bucket, path):
    my_assert(has_s3_object(bucket, path), '''
Error: unable to find S3 object '%s' in bucket '%s'.
Perhaps the bucket or file does not exist, or you do not have access to it?
(You can check this with `aws s3api list-buckets` and `aws s3 ls S3_PATH`.)
'''.strip() % (path, bucket))
