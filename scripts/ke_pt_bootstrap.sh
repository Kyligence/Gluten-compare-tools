#！/bin/sh
package_version=$1
ke_with_gluten_addr=$2
ke_without_gluten_addr=$3
single_point_test_duration=$4
continuous_test_duration=$5
start_con=$6
end_con=$7
con_step=$8

# shellcheck disable=SC2046
# shellcheck disable=SC2164
# shellcheck disable=SC2006
base_dir=$(
  cd $(dirname "$0")
  pwd
)
tmp_dir=${base_dir}/tmp
mkdir -p "$tmp_dir"

source "${base_dir}"/ke_env.sh
source "${base_dir}"/common/aws-instance.sh

s3_package="${S3_PACKAGE_PRE}"/"${package_version}"/gluten-"${package_version}"-amzn2023-x86_64.tar.gz
## update compare code
cd "${base_dir}"/.. || return

sudo git stash
sudo git fetch origin
sudo git checkout origin/main
sudo git stash pop

## install python requirements.txt
pip3 install -r "${base_dir}"/../requirements.txt

cd "${base_dir}" || return

## Start Env
#manager_instance start "$COMPARE_INSTANCE_IDS"

## Replace jars
latest_gluten="$tmp_dir"/latest_gluten.tar.gz
rm -f "$latest_gluten"
rm -rf "$tmp_dir"/latest_gluten
mkdir -p "$tmp_dir"/latest_gluten

aws s3 cp "$s3_package" "$latest_gluten"
tar -zxf "$latest_gluten" -C "$tmp_dir"/latest_gluten

### update libch.so
echo "Update libch.so"
scp -i "${COMPARE_USER_KEY}" "$tmp_dir"/latest_gluten/gluten-"${package_version}"-amzn2023-x86_64/libs/libch.so "${COMPARE_USER}"@"${COMPARE_KE_SERVER}":/opt/libch/libch.so
scp -i "${COMPARE_USER_KEY}" "$tmp_dir"/latest_gluten/gluten-"${package_version}"-amzn2023-x86_64/libs/libch.so "${COMPARE_USER}"@"${COMPARE_KE_WORKER}":/opt/libch/libch.so

### update gluten.jar
echo "Update gluten.jar"
scp -i "${COMPARE_USER_KEY}" "$tmp_dir"/latest_gluten/gluten-"${package_version}"-amzn2023-x86_64/jars/gluten.jar "${COMPARE_USER}"@"${COMPARE_KE_SERVER}":/opt/kyligence/engine/spark/jars/gluten.jar
scp -i "${COMPARE_USER_KEY}" "$tmp_dir"/latest_gluten/gluten-"${package_version}"-amzn2023-x86_64/jars/gluten.jar "${COMPARE_USER}"@"${COMPARE_KE_WORKER}":/opt/spark/jars/gluten.jar
### update shims.jar
echo "Update shims.jar"
scp -i "${COMPARE_USER_KEY}" "$tmp_dir"/latest_gluten/gluten-"${package_version}"-amzn2023-x86_64/extraJars/spark32/spark32-shims.jar "${COMPARE_USER}"@"${COMPARE_KE_SERVER}":/opt/kyligence/engine/spark/jars/spark32-shims.jar
scp -i "${COMPARE_USER_KEY}" "$tmp_dir"/latest_gluten/gluten-"${package_version}"-amzn2023-x86_64/extraJars/spark32/spark32-shims.jar "${COMPARE_USER}"@"${COMPARE_KE_WORKER}":/opt/spark/jars/spark32-shims.jar

## restart ke
#echo "Start KE"
#ssh -i "${COMPARE_USER_KEY}" "${COMPARE_USER}"@"${COMPARE_KE_SERVER}" "sudo systemctl restart kylin"
#echo "Starting KE"
#sleep 300

pwd
## Begin locust pt
echo "$(date '+%F %T'): Begin locust pt for ke with gluten ${ke_with_gluten_addr}"
sh "${base_dir}"/ke_pt.sh ${ke_with_gluten_addr} ${single_point_test_duration} ${continuous_test_duration} ${start_con} ${end_con} ${con_step}
echo "$(date '+%F %T'): End locust pt for ke with gluten"

echo "$(date '+%F %T'): Begin locust pt for ke without gluten ${ke_without_gluten_addr}"
sh "${base_dir}"/ke_pt.sh ${ke_without_gluten_addr} ${single_point_test_duration} ${continuous_test_duration} ${start_con} ${end_con} ${con_step}
echo "$(date '+%F %T'): End locust pt for ke without gluten"
