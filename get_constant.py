import argparse

from config import csv_config


parser = argparse.ArgumentParser(description='command line arguments')
parser.add_argument('--configName', type=str,
                    help='config name in config.py,support csv_config only now', required=True,
                    default="csv_config")
parser.add_argument('--key', type=str,
                    help='key for config map', required=True,
                    default="")

if __name__ == '__main__':
    args = vars(parser.parse_args())
    config_name = args["configName"]
    key = args["key"]
    if config_name != "csv_config":
        print("support csv_config only now")
    if key == "":
        print("need a key")

    print(csv_config[key])


