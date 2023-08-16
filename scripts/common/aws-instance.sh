#！/bin/sh

base_dir=$(
  cd $(dirname "$0")
  pwd
)

function manager_instance() {
  op=$1
  instance_ids=$2

  echo "$op aws instance."

  OLD_IFS="$IFS"
  IFS=","
  # shellcheck disable=SC2206
  instanceIdsArr=(${instance_ids})

  # shellcheck disable=SC2068
  for instance_id in ${instanceIdsArr[@]}; do
    echo "$(date '+%F %T'): $op instance ${instance_id}"

    if [ "$op" == "start" ]; then
      echo "do start ${instance_id}"
      python3 "$base_dir"/common/aws-instance.py --instance-ids "${instance_id}" --operator start
    elif [ "$op" == "stop" ]; then
      echo "do stop ${instance_id}"
      python3 "$base_dir"/common/aws-instance.py --instance-ids "${instance_id}" --operator stop
    else
      echo "$(date '+%F %T'): Not support $op"
      exit 110
    fi

    # shellcheck disable=SC2181
    if [ $? -ne 0 ]; then
      echo "$(date '+%F %T'): $op instance failed"
      exit 110
    fi
  done

  IFS="${OLD_IFS}"
}
