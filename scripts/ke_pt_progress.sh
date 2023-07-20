#！/bin/sh

dt=$1

# shellcheck disable=SC2046
# shellcheck disable=SC2164
# shellcheck disable=SC2006
base_dir=$(
  cd $(dirname "$0")
  pwd
)

# shellcheck disable=SC2039
source "${base_dir}"/ke_env.sh


cd ..

echo "to be done"
