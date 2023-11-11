#！/bin/sh

task_id=$1
package_version=$2
dt=$3
mod=$4
p_cnt=$5

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

#sudo git stash
#sudo git fetch origin
#sudo git checkout origin/main
#sudo git stash pop

### install python requirements.txt
pip3 install -r "${base_dir}"/../requirements.txt

cd "${base_dir}" || return

## Start Env
manager_instance start "$COMPARE_INSTANCE_IDS"

## Replace jars
#latest_gluten="$tmp_dir"/latest_gluten.tar.gz
#rm -f "$latest_gluten"
#rm -rf "$tmp_dir"/latest_gluten
#mkdir -p "$tmp_dir"/latest_gluten

#aws s3 cp "$s3_package" "$latest_gluten"
#tar -zxf "$latest_gluten" -C "$tmp_dir"/latest_gluten

### update libch.so
#echo "Update libch.so"
#scp -i "${COMPARE_USER_KEY}" "$tmp_dir"/latest_gluten/gluten-"${package_version}"-amzn2023-x86_64/libs/libch.so "${COMPARE_USER}"@"${COMPARE_KE_SERVER}":/opt/libch/libch.so
#scp -i "${COMPARE_USER_KEY}" "$tmp_dir"/latest_gluten/gluten-"${package_version}"-amzn2023-x86_64/libs/libch.so "${COMPARE_USER}"@"${COMPARE_KE_WORKER}":/opt/libch/libch.so

### update gluten.jar
#echo "Update gluten.jar"
#scp -i "${COMPARE_USER_KEY}" "$tmp_dir"/latest_gluten/gluten-"${package_version}"-amzn2023-x86_64/jars/gluten.jar "${COMPARE_USER}"@"${COMPARE_KE_SERVER}":/opt/kyligence/engine/server/jars/gluten.jar
#scp -i "${COMPARE_USER_KEY}" "$tmp_dir"/latest_gluten/gluten-"${package_version}"-amzn2023-x86_64/jars/gluten.jar "${COMPARE_USER}"@"${COMPARE_KE_WORKER}":/opt/spark/jars/gluten.jar
### update shims.jar
#echo "Update shims.jar"
#scp -i "${COMPARE_USER_KEY}" "$tmp_dir"/latest_gluten/gluten-"${package_version}"-amzn2023-x86_64/extraJars/spark33/gluten-spark33-shims.jar "${COMPARE_USER}"@"${COMPARE_KE_SERVER}":/opt/kyligence/engine/server/jars/gluten-spark33-shims.jar
#scp -i "${COMPARE_USER_KEY}" "$tmp_dir"/latest_gluten/gluten-"${package_version}"-amzn2023-x86_64/extraJars/spark33/gluten-spark33-shims.jar "${COMPARE_USER}"@"${COMPARE_KE_WORKER}":/opt/spark/jars/gluten-spark33-shims.jar

## restart ke
echo "Start KE"
ssh -i "${COMPARE_USER_KEY}" "${COMPARE_USER}"@"${COMPARE_KE_SERVER}" "sudo systemctl restart kylin"
echo "Starting KE"
sleep 300

## Begin compare with double run
echo "Begin compare"
python3 "${base_dir}"/../begin_compare.py --process "$p_cnt" --date "$dt" --batch "$task_id" --mod "$mod"
echo "End compare"




## Backup original csv
cp -r /opt/zen-compare/goreplay_data/result/"$task_id" /opt/zen-compare/goreplay_data/result/"$task_id"0
cp -r /opt/zen-compare/goreplay_data/backup/"$task_id" /opt/zen-compare/goreplay_data/backup/"$task_id"0
cp -r /opt/zen-compare/goreplay_data/server_result/"$task_id" /opt/zen-compare/goreplay_data/server_result/"$task_id"0

## Check all slow queries again and again
echo "Begin check slow queries the first time"
mkdir -p /opt/zen-compare/goreplay_data/backup/"$task_id"1
cp /opt/zen-compare/goreplay_data/backup/"$task_id"/DIFF_DURATION_ALL_SLOW.csv /opt/zen-compare/goreplay_data/backup/"$task_id"1/
python3 "${base_dir}"/../begin_compare.py --process "$p_cnt" --date "$task_id"1 --batch "$task_id" --mod "error"

## /opt/zen-compare/goreplay_data/result/333/SUMMARY.csv
echo "" >> /opt/zen-compare/goreplay_data/result/"$task_id"0/SUMMARY.csv
echo "" >> /opt/zen-compare/goreplay_data/result/"$task_id"0/SUMMARY.csv
echo "result of checking slow queries the first time:" >> /opt/zen-compare/goreplay_data/result/"$task_id"0/SUMMARY.csv
cat /opt/zen-compare/goreplay_data/result/"$task_id"/SUMMARY.csv >> /opt/zen-compare/goreplay_data/result/"$task_id"0/SUMMARY.csv
echo "End check slow queries the first time"

## Backup check slow _1 csv
rm -rf /opt/zen-compare/goreplay_data/backup/"$task_id"1
cp -r /opt/zen-compare/goreplay_data/result/"$task_id" /opt/zen-compare/goreplay_data/result/"$task_id"1
cp -r /opt/zen-compare/goreplay_data/backup/"$task_id" /opt/zen-compare/goreplay_data/backup/"$task_id"1
cp -r /opt/zen-compare/goreplay_data/server_result/"$task_id" /opt/zen-compare/goreplay_data/server_result/"$task_id"1


echo "Begin check slow queries the second time"
mkdir -p /opt/zen-compare/goreplay_data/backup/"$task_id"2
cp /opt/zen-compare/goreplay_data/backup/"$task_id"/DIFF_DURATION_ALL_SLOW.csv /opt/zen-compare/goreplay_data/backup/"$task_id"2/
python3 "${base_dir}"/../begin_compare.py --process "$p_cnt" --date "$task_id"2 --batch "$task_id" --mod "error"

echo "" >> /opt/zen-compare/goreplay_data/result/"$task_id"0/SUMMARY.csv
echo "" >> /opt/zen-compare/goreplay_data/result/"$task_id"0/SUMMARY.csv
echo "result of checking slow queries the second time:" >> /opt/zen-compare/goreplay_data/result/"$task_id"0/SUMMARY.csv
cat /opt/zen-compare/goreplay_data/result/"$task_id"/SUMMARY.csv >> /opt/zen-compare/goreplay_data/result/"$task_id"0/SUMMARY.csv
echo "End check slow queries the second time"

## Backup check slow _2 csv
rm -rf /opt/zen-compare/goreplay_data/backup/"$task_id"2
cp -r /opt/zen-compare/goreplay_data/result/"$task_id" /opt/zen-compare/goreplay_data/result/"$task_id"2
cp -r /opt/zen-compare/goreplay_data/backup/"$task_id" /opt/zen-compare/goreplay_data/backup/"$task_id"2
cp -r /opt/zen-compare/goreplay_data/server_result/"$task_id" /opt/zen-compare/goreplay_data/server_result/"$task_id"2

## restore original csv
rm -rf /opt/zen-compare/goreplay_data/result/"$task_id"
mv /opt/zen-compare/goreplay_data/result/"$task_id"0 /opt/zen-compare/goreplay_data/result/"$task_id"
rm -rf /opt/zen-compare/goreplay_data/backup/"$task_id"
mv /opt/zen-compare/goreplay_data/backup/"$task_id"0 /opt/zen-compare/goreplay_data/backup/"$task_id"
rm -rf /opt/zen-compare/goreplay_data/server_result/"$task_id"
mv /opt/zen-compare/goreplay_data/server_result/"$task_id"0 /opt/zen-compare/goreplay_data/server_result/"$task_id"

## stop ke
echo "Stop KE"
ssh -i "${COMPARE_USER_KEY}" "${COMPARE_USER}"@"${COMPARE_KE_SERVER}" "sudo systemctl stop kylin"
echo "Stopping KE"
sleep 300
