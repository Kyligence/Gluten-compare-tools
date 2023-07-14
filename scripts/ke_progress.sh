#！/bin/sh

dt=$1
mod=$2

# shellcheck disable=SC2046
# shellcheck disable=SC2164
# shellcheck disable=SC2006
base_dir=$(
  cd $(dirname "$0")
  pwd
)

# shellcheck disable=SC2039
source "${base_dir}"/ke_env.sh

left=$(redis-cli llen query)
total=0

if [ "$mod" == "date" ]; then
  total=$(cat $GOREPLAY_DATA_PATH/goreplay/${dt}.csv | wc -l)
elif [ "$mod" == "error" ]; then
  total=$(ls $GOREPLAY_DATA_PATH/backup/${dt}/*.csv | grep -v FALLBACK.csv | grep -v SUCCESS.csv | xargs cat | wc -l)
fi

echo "Total: $total, left: $left"
