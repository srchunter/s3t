import json


def get():
    config = None

    try:
        with open("s3t/config.json", "r") as f_in:
            config = json.load(f_in)
    except FileNotFoundError:
        config = init()
        pass
    except json.decoder.JSONDecodeError as e:
        print("Config file JSON invalid -", e)
        pass

    return config

def init():
    config = {
        "access_key_id": "",
        "access_key": "",
        "default_bucket": ""
    }

    with open("config.json", "w") as f_out:
        json.dump(config, f_out)

    return config

def settings():
    config = get()
    access_key_id = input("Access Key ID [" + config["access_key_id"] + "]: ")
    access_key = input("Access Key [" + config["access_key"] + "]: ")
    default_bucket = input("Default Bucket [" + config["default_bucket"] + "]: ")

    if access_key_id == "":
        config["access_key_id"] = config["access_key_id"]
    else:
        config["access_key_id"] = access_key_id

    if access_key == "":
        config["access_key"] = config["access_key"]
    else:
        config["access_key"] = access_key

    if default_bucket == "":
        config["default_bucket"] = config["default_bucket"]
    else:
        config["default_bucket"] = default_bucket

    with open("s3t/config.json", "w") as f_out:
        json.dump(config, f_out)