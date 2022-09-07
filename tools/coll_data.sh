#!/usr/bin/env bash
MYSQL_HOST='127.0.0.1'
MYSQL_PORT='3308'
MYSQL_USER='root'
MYSQL_PASSWORD='123456'

DATA_COLLECTION_TIME=3 #show global status的时间, 每隔1秒采集一次
CONF=$1

MYSQL_COMM="mysql -h${MYSQL_HOST} -P${MYSQL_PORT} -u${MYSQL_USER} -p${MYSQL_PASSWORD}"
SHELL_COMM='sh' #暂不支持远程巡检 ssh -c
XML_FILENAME="${MYSQL_HOST}_${MYSQL_PORT}_$(date +%Y%m%d_%H%M%S).xml" #采集的数据保存的文件


setkv(){
name=$1
value=$2
filename=$3
echo "<${name}>" >> ${filename}
echo "${value}" >> ${filename}
echo "</${name}>" >> ${filename}
}

#setdir(){
#basedir=$(${MYSQL_COMM} -e 'select @@basedir' 2>/dev/null | tail -1)
#datadir=$(${MYSQL_COMM} -e 'select @@datadir' 2>/dev/null | tail -1)
#redodir=$(${MYSQL_COMM} -e 'select @@innodb_data_home_dir' 2>/dev/null | tail -1)
#binlogdir=$(${MYSQL_COMM} -e 'select @@log_bin_index' 2>/dev/null | tail -1)
#tmpdir=$(${MYSQL_COMM} -e 'select @@tmpdir' 2>/dev/null | tail -1)
#if [ ${datadir::1} != '/' ];then datadir=${basedir}/${datadir} fi
#if [ ${redodir::1} != '/' ];then datadir=${datadir}/${redodir} fi
#if [ ${binlogdir::1} != '/' ];then datadir=${datadir}/${binlogdir} fi
#if [ ${tmpdir::1} != '/' ];then datadir=${datadir}/${tmpdir} fi
#echo "<datadir>" >> ${XML_FILENAME}
#echo "</datadir>" >> ${XML_FILENAME}
#echo "<redodir>" >> ${XML_FILENAME}
#echo "</redodir>" >> ${XML_FILENAME}
#echo "<binlogdir>" >> ${XML_FILENAME}
#echo "</binlogdir>" >> ${XML_FILENAME}
#echo "<tmpdir>" >> ${XML_FILENAME}
#echo "</tmpdir>" >> ${XML_FILENAME}
#}

stty erase ^H

#检查MYSQL连接信息
if $MYSQL_COMM -e 'select 1' >/dev/null 2>&1;then
	echo 'MYSQL连接正常, 即将开始采集数据'
else
	echo 'MYSQL连接失败, 请检查连接信息'
	exit 2
fi
#echo $MYSQL_COMM

#检查SSH连接信息
#TO BE CONTINUED

#XML头部信息
echo "<inspection version='2.2'>" >> ${XML_FILENAME}

#MYSQL巡检信息 开始
echo "<mysql>" >> ${XML_FILENAME}
#MYSQL巡检信息固定巡检项, 持续巡检项 开始
echo "<data1>" >> ${XML_FILENAME}
echo "<global_status>" >> ${XML_FILENAME}
while ((${DATA_COLLECTION_TIME}>1));do
echo "<row time='$(date +%s)'>" >> ${XML_FILENAME}
$MYSQL_COMM -X -e 'show global status' 2>/dev/null | tail -n +2 >> ${XML_FILENAME}
echo "</row>" >> ${XML_FILENAME}
DATA_COLLECTION_TIME=$[${DATA_COLLECTION_TIME}-1]
sleep 1
done
echo "</global_status>" >> ${XML_FILENAME}
echo "</data1>" >> ${XML_FILENAME}
#MYSQL巡检信息固定巡检项, 持续巡检项 结束

#MYSQL固定巡检项 开始
echo "<data2>" >> ${XML_FILENAME}
echo "<global_variables>" >> ${XML_FILENAME}
$MYSQL_COMM -X -e 'show global variables' 2>/dev/null | tail -n +2 >> ${XML_FILENAME}
echo "</global_variables>" >> ${XML_FILENAME}
echo "<global_status>" >> ${XML_FILENAME}
$MYSQL_COMM -X -e 'show global status' 2>/dev/null | tail -n +2 >> ${XML_FILENAME}
echo "</global_status>" >> ${XML_FILENAME}
echo "<sys.metrics>" >> ${XML_FILENAME}
$MYSQL_COMM -X -e 'select * from sys.metrics' 2>/dev/null | tail -n +2 >> ${XML_FILENAME}
echo "</sys.metrics>" >> ${XML_FILENAME}
echo "<sys.memory_global_total>" >> ${XML_FILENAME}
$MYSQL_COMM -X -e 'select * from sys.memory_global_total' 2>/dev/null | tail -n +2 >> ${XML_FILENAME}
echo "</sys.memory_global_total>" >> ${XML_FILENAME}
echo "<slave_status>" >> ${XML_FILENAME}
$MYSQL_COMM -X -e 'show slave status' 2>/dev/null | tail -n +2 >> ${XML_FILENAME}
echo "</slave_status>" >> ${XML_FILENAME}
echo "<performance_schema.replication_group_members>" >> ${XML_FILENAME}
$MYSQL_COMM -X -e 'select * from performance_schema.replication_group_members' 2>/dev/null | tail -n +2 >> ${XML_FILENAME}
echo "</performance_schema.replication_group_members>" >> ${XML_FILENAME}
echo "<performance_schema.replication_group_member_stats>" >> ${XML_FILENAME}
$MYSQL_COMM -X -e 'select * from performance_schema.replication_group_member_stats' 2>/dev/null | tail -n +2 >> ${XML_FILENAME}
echo "</performance_schema.replication_group_member_stats>" >> ${XML_FILENAME}
echo "<master_info>" >> ${XML_FILENAME}
$MYSQL_COMM -X -e 'select * from information_schema.processlist where COMMAND = "Binlog Dump";' 2>/dev/null | tail -n +2 >> ${XML_FILENAME}
echo "</master_info>" >> ${XML_FILENAME}
echo "<db_table_info>" >> ${XML_FILENAME}
$MYSQL_COMM -X -e "select bb.*,aa.DEFAULT_CHARACTER_SET_NAME from information_schema.SCHEMATA as aa left join (select table_schema, sum(data_length) as data_length, sum(index_length) as index_length from information_schema.tables where TABLE_SCHEMA not in ('sys','mysql','information_schema','performance_schema') group by table_schema) as bb on aa.SCHEMA_NAME=bb.table_schema where bb.table_schema is not null;" 2>/dev/null | tail -n +2 >> ${XML_FILENAME}
echo "</db_table_info>" >> ${XML_FILENAME}
echo "</data2>" >> ${XML_FILENAME}
#MYSQL固定巡检项 结束

#MYSQL巡检项 开始
echo "<data3>" >> ${XML_FILENAME}
sed -i 's/ \* / THISISFLAG_FOR_XINGHAO_BYDDCW /' ${CONF}
#while read 会读取错误的数据, 所以这里改用head tail读取(冤枉while了, 后来发现是select *的锅... 不过这*还是坑了我好一段时间)
while read ldata
do
iname=$(echo "${ldata}" | awk -F '__DDCW_FLAG_SPIT__' '{print $1}')
isql=$(echo "${ldata}" | awk -F '__DDCW_FLAG_SPIT__' '{print $2}')
#isql=$(echo ${isql} | sed 's/THISISFLAG_FOR_XINGHAO_BYDDCW/ \* /')
echo "<${iname}>" >> ${XML_FILENAME}
$MYSQL_COMM -X -e "${isql/THISISFLAG_FOR_XINGHAO_BYDDCW/*}" 2>/dev/null | tail -n +2 >> ${XML_FILENAME} 
#echo ${isql/THISISFLAG_FOR_XINGHAO_BYDDCW/*}
echo "</${iname}>" >> ${XML_FILENAME}
done < ${CONF}

echo "</data3>" >> ${XML_FILENAME}
#MYSQL巡检项 结束

#MYSQL巡检信息 结束
echo "</mysql>" >> ${XML_FILENAME}

#主机巡检项 开始
echo "<host enabled='True'>" >> ${XML_FILENAME}
echo "<cpu_socket>" >> ${XML_FILENAME}
lscpu | grep 'Socket(s)' | awk '{print $NF}' >> ${XML_FILENAME}
echo "</cpu_socket>" >> ${XML_FILENAME}
setkv 'cpu_core' "$(lscpu | grep 'Core(s)' | awk '{print $NF}')" ${XML_FILENAME}
setkv 'cpu_thread' "$(lscpu | grep 'Thread(s)' | awk '{print $NF}')" ${XML_FILENAME}
setkv 'cpu_name' "`lscpu | grep name | awk '$1="";$2=""; {print $0}'`" ${XML_FILENAME}
setkv 'mem_total' "`cat /proc/meminfo | awk  '{ if ( $1 == "MemTotal:") print $2}'`" ${XML_FILENAME}
setkv 'mem_free' "`cat /proc/meminfo | awk  '{ if ( $1 == "MemFree:") print $2}'`" ${XML_FILENAME}
setkv 'mem_available' "`cat /proc/meminfo | awk  '{ if ( $1 == "MemAvailable:") print $2}'`" ${XML_FILENAME}
setkv 'swappiness' "`cat /proc/sys/vm/swappiness`" ${XML_FILENAME}
setkv 'swap_total' "`cat /proc/meminfo | awk  '{ if ( $1 == "SwapTotal:") print $2}'`" ${XML_FILENAME}
setkv 'swap_free' "`cat /proc/meminfo | awk  '{ if ( $1 == "SwapFree:") print $2}'`" ${XML_FILENAME}
setkv 'hostname' "`cat /proc/sys/kernel/hostname`" ${XML_FILENAME}
setkv 'version' "`grep "^NAME=" /etc/os-release  | awk -F = '{print $2}' | sed 's/\"//g'`" ${XML_FILENAME}
setkv 'kernel' "`uname -r`" ${XML_FILENAME}
setkv 'platform' "`uname -m`" ${XML_FILENAME}
setkv 'loadavg' "`cat /proc/loadavg`" ${XML_FILENAME}
setkv 'timezone' "`ls -l /etc/localtime | awk -F /zoneinfo/ '{print $NF}'`" ${XML_FILENAME}
#setdir()
echo "</host>" >> ${XML_FILENAME}
#主机巡检项 结束

#基础信息
echo "<baseinfo>" >> ${XML_FILENAME}
setkv 'host' "${MYSQL_HOST}" ${XML_FILENAME}
setkv 'port' "${MYSQL_PORT}" ${XML_FILENAME}
echo "</baseinfo>" >> ${XML_FILENAME}

#XML头部信息 结束
echo "</inspection>" >> ${XML_FILENAME}

echo "采集完成"
