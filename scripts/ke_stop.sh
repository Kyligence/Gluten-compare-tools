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

ps aux | grep ke_compare_bootstrap.sh | grep -v grep | awk '{print $2}' | xargs kill -9
ps aux | grep begin_compare.py | grep -v grep | awk '{print $2}' | xargs kill -9

# Don't close instance
#manager_instance stop "$COMPARE_INSTANCE_IDS"
