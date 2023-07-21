#！/bin/sh

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
dt_f=$(date +%F)
cat pt_results/${dt_f}/ke_with_gluten_progress
cat pt_results/${dt_f}/ke_without_gluten_progress
