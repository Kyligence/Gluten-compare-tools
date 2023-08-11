#！/bin/sh

ke_addr=$1
single_point_test_duration=$2
continuous_test_duration=$3
start_con=$4
end_con=$5
con_step=$6
progress_file=$7


PARENT_DIR=$(cd $(dirname $0);cd ..; pwd)

echo "$(date '+%F %T'): current dir is:$(pwd)"

echo "$(date '+%F %T'): update config.py to make query set the latest SUCCESS.csv"
back_dir=$(python3 get_constant.py --configName csv_config --key backup)
query_set_base_dir=$(python3 get_constant.py --configName csv_config --key file_dir)/${back_dir}
latest_sub_dir=$(ls -t ${query_set_base_dir}|head -n 1)

sed -ri "s/('pt_source_parent_dir': \")[^\"]*/'pt_source_parent_dir': \"${back_dir}\/${latest_sub_dir}/" config.py

dt_f=$(date +%F)
dt_ft=$(date +%F_%T)

mkdir -p pt_results/${dt_f}

for((i=${start_con};i<${end_con};i+=${con_step}));do
  echo "$(date '+%F %T'): single point pt:locust -f locust_pt.py --headless -u ${i} -r 50 -t ${single_point_test_duration}s --host=${ke_addr} --csv=pt_results/${dt_f}/sp_${dt_ft}_${i}"
  locust -f locust_pt.py --headless -u ${i} -r 50 -t ${single_point_test_duration}s --host=${ke_addr} --csv=pt_results/${dt_f}/sp_${dt_ft}_${i}
  echo "ke_with_gluten, start_con:${start_con}, end_con:${end_con}, current_con:${i}" > ${progress_file}
done

top_rps=0
concurrency_number=10
echo "$(date '+%F %T'): get submit rps value(no failed query) and the related concurrency number"
echo "concurrency,failedCount,rps" | tee -a pt_results/${dt_f}/SUMMARY
for result in $(ls -tr pt_results/${dt_f}/sp_${dt_ft}_*_stats.csv);do
  con=$(echo ${result}| awk -F '_' '{print $(NF-1)}')
	arr=($(sed -n "2, 1p" ${result}| awk -F ',' '{print $4,$10}'))
	echo ${con},${arr[0]},${arr[1]} | tee -a pt_results/${dt_f}/SUMMARY
  if [ ${arr[0]} -eq 0 ] && [ 1 -eq "$(echo "${top_rps} < ${arr[1]}" | bc)" ];then
    top_rps=${arr[1]}
    concurrency_number=${con}
  fi

done

echo "top_rps: ${top_rps},  concurrency_number: ${concurrency_number}" | tee -a pt_results/${dt_f}/SUMMARY
echo ""
if [ ${continuous_test_duration} -ne 0 ];then
  echo "$(date '+%F %T'): use the concurrency that made the most submit rps to do continuous stress test"
  echo "$(date '+%F %T'): locust -f locust_pt.py --headless -u ${concurrency_number} -r 50 -t ${continuous_test_duration}s --host=${ke_addr} --csv=pt_results/${dt_f}/c_${dt_ft}_${concurrency_number}"
  echo "ke continuous test begin" >> ${progress_file}
  locust -f locust_pt.py --headless -u ${concurrency_number} -r 50 -t ${continuous_test_duration}s --host=${ke_addr} --csv=pt_results/${dt_f}/c_${dt_ft}_${concurrency_number}
  echo "ke continuous test end" >> ${progress_file}
  echo "$(date '+%F %T'): pt_results/${dt_f}/c_${dt_ft}_${concurrency_number}_exceptions.csv:"
  cat pt_results/${dt_f}/c_${dt_ft}_${concurrency_number}_exceptions.csv
  echo "$(date '+%F %T'): pt_results/${dt_f}/c_${dt_ft}_${concurrency_number}_failures.csv:"
  cat pt_results/${dt_f}/c_${dt_ft}_${concurrency_number}_exceptions.csv
  echo "$(date '+%F %T'): pt_results/${dt_f}/c_${dt_ft}_${concurrency_number}_stats.csv:"
  cat pt_results/${dt_f}/c_${dt_ft}_${concurrency_number}_stats.csv | tee -a pt_results/${dt_f}/SUMMARY
fi

echo ""
echo ""
echo ""
