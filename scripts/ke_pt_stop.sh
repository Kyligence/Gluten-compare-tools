#!/bin/sh

# shellcheck disable=SC2046
# shellcheck disable=SC2164
# shellcheck disable=SC2006
base_dir=$(
  cd $(dirname "$0")
  pwd
)

# shellcheck disable=SC2039
source "${base_dir}"/ke_env.sh
# shellcheck disable=SC2039
source "${base_dir}"/common/aws-instance.sh

ps aux | grep ke_pt_bootstrap.sh | grep -v grep | awk '{print $2}' | xargs kill -9
ps aux | grep locust_pt.py | grep -v grep | awk '{print $2}' | xargs kill -9

manager_instance stop "$COMPARE_INSTANCE_IDS"
