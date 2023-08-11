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
cat /opt/zen-compare/Gluten-compare-tools/pt_results/${dt_f}/ke_with_gluten_progress
cat /opt/zen-compare/Gluten-compare-tools/pt_results/${dt_f}/ke_without_gluten_progress
