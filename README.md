# s3t
Tool for python3 to assist development of projects with AWS S3

- [List objects](#list-objects)
- [Download object](#download-object)
- [Upload object](#upload-object)
- [Copy object](#copy-object)
- [Remove object](#remove-object)

## Installation
 Install these dependencies with pip:
 - boto3
 - botocore

 To define defaults run:
    
    s3t -s

If you are on a node with permissions for the bucket you can ignore setting the access key.

## Usage

### List objects

    s3t -l [PREFIX] [-a]

**PREFIX** (optional): Filter items with given prefix. If no prefix is specified, the current date will be used in this format: `year=YYYY/month=M/date=D/`

**-a, --all** (optional): Ignore pagination and list all items

---

### Download object

    s3t -d <KEY> [-k <FILENAME>]

**KEY**: The key to be downloaded from the bucket

**-k, --key FILENAME** (optional): The name of the file that will be saved locally

---

### Upload object

    s3t -u <PATH> -k <KEY>

**PATH**: The path to the local file

**-k, --key KEY**: The key of the object that will be saved on the bucket

---

### Copy object

    s3t -c <SOURCE_KEY> -t <TARGET_BUCKET> [-k <KEY>]

**SOURCE_KEY**: The key of the object that will be copied

**-t, --target TARGET_BUCKET**: The name of the bucket the object will be copied to

**-k, --key KEY** (optional): The name of the object that will be saved on the target bucket

---

### Remove object

    s3t -r <KEY>

**KEY**: The key that should be removed