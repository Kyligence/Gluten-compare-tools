#！/bin/sh

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
      aws ec2 start-instances --instance-ids "${instance_id}"
    elif [ "$op" == "stop" ]; then
      echo "do stop ${instance_id}"
      aws ec2 stop-instances --instance-ids "${instance_id}"
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
  echo "Wait for ec2 $op..."
  echo "See you 60s latter..."
  sleep 60
}
