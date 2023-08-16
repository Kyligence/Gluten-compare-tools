import sys
import time

sys.path.append("../..")

import argparse
import boto3

from config import log

parser = argparse.ArgumentParser(description='')
parser.add_argument('--operator', type=str,
                    help='', required=True)
parser.add_argument('--instance-ids', type=str,
                    help='', required=True)

client = boto3.client('ec2')


def check_instance_status(instances: list, st: str) -> bool:
    need_checks = instances
    time_second = 900  # 15 minutes
    while len(need_checks) > 0 and time_second >= 0:
        log.info("{} is in {}".format(str(need_checks), st))
        need_checks_new = []
        for i in range(0, len(need_checks)):
            res: dict = client.describe_instance_status(
                InstanceIds=[need_checks[i]],
                DryRun=False,
                IncludeAllInstances=True
            )
            log.info(str(res))

            statuses = res.get("InstanceStatuses")
            if statuses is not None and len(statuses) != 0 and statuses[0]["InstanceState"]["Name"] != st:
                need_checks_new.append(need_checks[i])
                log.info("{} status is {}".format(str(need_checks[i]), statuses[0]["InstanceState"]["Name"]))

        time_second = time_second - 10
        time.sleep(10)
        need_checks = need_checks_new

    if len(need_checks) > 0:
        return False

    return True


def start_instance(instances: list):
    response: dict = client.start_instances(
        InstanceIds=instances,
        AdditionalInfo='',
        DryRun=False
    )

    log.info(str(response))
    starting_instances: list = response.get("StartingInstances")

    if starting_instances is None or len(starting_instances) != len(instances):
        log.err("Start failed")
        sys.exit(-1)

    return check_instance_status(instances, "running")


def stop_instance(instances: list):
    response: dict = client.stop_instances(
        InstanceIds=instances,
        Force=False,
        DryRun=False
    )

    log.info(str(response))
    stop_instances: list = response.get("StoppingInstances")

    if stop_instances is None or len(stop_instances) != len(instances):
        log.err("Stop failed")
        sys.exit(-1)

    return check_instance_status(instances, "stopped")


if __name__ == '__main__':
    args = vars(parser.parse_args())
    instance_ids: str = args["instance_ids"]
    operator = args["operator"]

    ids = instance_ids.split(",")

    if operator == "start":
        start_instance(ids)
    elif operator == "stop":
        stop_instance(ids)
