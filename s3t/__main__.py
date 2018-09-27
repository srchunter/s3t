import argparse
import sys
import config
import os
import s3operation

s3tdir = os.path.dirname(os.path.realpath(__file__))
with open(s3tdir + "/VERSION", "r") as f:
    VERSION = f.readline()

def parse_args():

    conf = config.get()

    parser = argparse.ArgumentParser(description="Python s3 tools")
    
    parser.add_argument("-d", "--download", type=str, help="Download a file from a bucket")
    parser.add_argument("-u", "--upload", type=str, help="Upload a file to a bucket")
    parser.add_argument("-c", "--copy", type=str, help="Copy a file from one bucket to another")
    parser.add_argument("-r", "--remove", type=str, help="Remove a file from a bucket")
    parser.add_argument("-t", "--target", type=str, help="Target bucket (for use with --copy)")
    parser.add_argument("-k", "--key", type=str, help="Name to save a file as (for --upload, --copy, --download)")
    parser.add_argument("-l", "--list", type=str, nargs="?", const="*", help="List files on a bucket")
    parser.add_argument("-a", "--all", action="store_true", default=False, help="List all files (no pagination)")
    parser.add_argument("-s", "--settings", action="store_true", default=False, help="Define default settings")
    parser.add_argument("-v", "--version", action="version", version=VERSION)
    parser.add_argument("-b", "--bucket", default=conf["default_bucket"], help="Use specified bucket")
    parser.add_argument("--creds", type=str, nargs="?", const="?", help="Run the tool with credentials")
    parser.add_argument("-n", "--nosize", action="store_true", default=False, help="Don't show size of files")
    
    args = parser.parse_args()

    args.access_key_id = conf["access_key_id"]
    args.access_key = conf["access_key"]

    if not args.settings:
        
        if args.creds:
            split = args.creds.split(":")
            if len(split) == 2:
                args.access_key_id = split[0] 
                args.access_key = split[1] 
            elif args.access_key_id == "" or args.access_key == "":
                parser.error("Please provide credentials in format <access_key_id>:<access_key>")

        if args.bucket == "":
            parser.error("No bucket found. Provide it with -b <bucket> or save a default in the settings by running s3t -s")

        op = args.download != None
        if args.upload != None and op:
            parser.error("Can't combine operations. Choose one of -l, -d, -c, -r or -u")
        else:
            op = op or args.upload != None

        if args.copy != None and op:
            parser.error("Can't combine operations. Choose one of -l, -d, -c, -r or -u")
        else:
            op = op or args.copy != None

        if args.list != None and op:
            parser.error("Can't combine operations. Choose one of -l, -d, -c, -r or -u")
        else:
            op = op or args.list != None

        if args.remove != None and op:
            parser.error("Can't combine operations. Choose one of -l, -d, -c, -r or -u")
        else:
            op = op or args.remove != None

        if op is False:
            parser.error("Please specify an operation (-l, -d, -c, -u, -r)")

        if args.copy and args.target is None:
            parser.error("Please specify a target bucket (-t)")

        if args.upload and args.key is None:
            parser.error("Please specify a target key (-k)")
            
    return args


def main():
    args = parse_args()
    if args.settings:
        config.settings()
        exit(0)
    
    if args.list:
        s3operation.list_keys(args.bucket, args.list, all=args.all, access_key_id=args.access_key_id, access_key=args.access_key, showSize=(not args.nosize))
    elif args.download:
        s3operation.download(args.bucket, args.download, filename=args.key)
    elif args.copy:
        s3operation.copy(args.bucket, args.copy, args.target, target_key=args.key)
    elif args.upload:
        s3operation.upload(args.bucket, args.upload, args.key)
    elif args.remove:
        s3operation.remove(args.bucket, args.remove)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
