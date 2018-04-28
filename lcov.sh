function genxml()
{
	number=$#
	param=("$@")
	sources_path=${SRC_PATH}
	test_sources_path=${SRC_TEST_PATH}
	for arg in "${param[@]}"
	do
		sources_path=${sources_path}/${arg}
	done
	cd ${SRC_PATH}/../../
	#重置计数器
	#lcov --directory . --zerocounters
	#收集当前状态到一个文件夹
	mkdir ${param[${number}-1]}
	lcov --directory ${sources_path} --capture --output-file $(pwd)/${param[${number}-1]}/${param[${number}-1]}.info  &>/dev/null
	#获取HTML输出
	cp ${TEXTSRC}/ut_incremental_coverage_report.template .
	gensummary $(pwd)/${param[${number}-1]}/${param[${number}-1]}.info $(pwd)/${param[${number}-1]}/lcov.xml &>/dev/null
	genhtml $(pwd)/${param[${number}-1]}/${param[${number}-1]}.info  --output-directory ${param[${number}-1]}/coverage &>/dev/null
}
function ipmi()
{
	
	genxml IPMI
	cp ${TEXTSRC}/ut_incremental_coverage_report.template .
	if [ -d ./IPMI/coverage/ipmi ]
	then
		/usr/local/bin/python ${TEXTSRC}/ut_incremental_check.py '["IPMI"]' "IPMI/coverage/ipmi" $threshold "IPMI"
		res=$?
	elif [ -d ./IPMI/coverage/src/IPMI/src/ipmi ]
	then
		/usr/local/bin/python ${TEXTSRC}/ut_incremental_check.py '["IPMI"]' "IPMI/coverage/src/IPMI/src/ipmi" $threshold "IPMI"
		res=$?
	else
		echo "coverage/ipmi cannot found! please check"
		res=1
	fi
	if [ $res -ne 0 ];then
		exit 1
	fi
}
