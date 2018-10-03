import boto3
import botocore
import sys
import datetime 
import os
import threading

def print_key(key, showSize=True):
    if showSize:
        print(key['Key'], "\t\t", str(round(key["Size"] / 1024 / 1024, 3)) + "mb")
    else:
        print(key['Key'])

class ProgressPercentageUp(object):
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\rUploading %s  %s / %s  (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()

class ProgressPercentageDown(object):
    def __init__(self, client, bucket, key):
        self._key = key
        self._size = float(client.head_object(Bucket=bucket, Key=key)["ContentLength"])
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\rDownloading %s  %s / %s  (%.2f%%)" % (
                    self._key, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()

def list_keys(bucket, prefix, all=False, access_key_id=None, access_key=None, showSize=True):
    
    conn = boto3.client('s3')

    d = datetime.date.today()
    default_key = "year=" + str(d.year) + "/month=" + str(d.month) + "/date=" + d.strftime("%-d") + "/"
    if prefix == "*":
        prefix = default_key

    last_key = None
    try:
        key_list = conn.list_objects(Bucket=bucket, Prefix=prefix)['Contents']
        for key in key_list:
            print_key(key, showSize=showSize)
            last_key = key['Key']
    except KeyError:
        print("No results found with prefix '" + prefix + "'")
        sys.exit(0)

    while True:
        try:
            key_list = conn.list_objects(Bucket=bucket, Prefix=prefix, Marker=last_key)['Contents']
        except KeyError:
            sys.exit(0)
        
        try:
            if not all:
                input("Next page? [ENTER]")
        except KeyboardInterrupt:
            print("Aborted")
            sys.exit(0)
        
        for key in key_list:
                print_key(key, showSize=showSize)
                last_key = key['Key']


def download(bucket, key, filename=None, showProgress=True):
   
    client = boto3.client('s3')
    
    if filename is None:
        filename = os.path.basename(key)

    try:
        if showProgress:
            client.download_file(bucket, key, filename, Callback=ProgressPercentageDown(client, bucket, key))
        else:
            client.download_file(bucket, key, filename)
        print("\n" + bucket, "-", key, "finished Download")
    except botocore.exceptions.ClientError as e:
        print("S3 Error:", e)

def upload(bucket, path, key):
    client = boto3.client("s3")

    config = boto3.s3.transfer.TransferConfig(
            multipart_threshold=100 * 1024 * 1024,
            max_concurrency=10
        )

    transfer = boto3.s3.transfer.S3Transfer(client, config)

    try:
        transfer.upload_file(path, bucket, key, callback=ProgressPercentageUp(path))
        print("\n" + bucket, "-", key, "finished Upload")
    except botocore.exceptions.ClientError as e:
        print("S3 Error:", e)

def copy(bucket, key, target, target_key=None):
    client = boto3.client("s3")

    if target_key is None:
        target_key = key
    
    try:
        client.copy({"Bucket" : bucket, "Key" : key}, target, target_key)
    except botocore.exceptions.ClientError as e:
        print("S3 Error:", e)

    print(bucket, "-", key, "copied to", target, "-", target_key)

def remove(bucket, key):
    client = boto3.client("s3")
    
    try:
        i = input("Really delete " + bucket + " - " + key + " ? [N/y]: ")
    except KeyboardInterrupt:
        sys.exit(0)

    if i == "y":
        try:
            client.delete_object(Key=key, Bucket=bucket)
            print(bucket, "-", key, "deleted")
        except botocore.exceptions.ClientError as e:
            print("S3 Error:", e)
    else:
        sys.exit(0)
