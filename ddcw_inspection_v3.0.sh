#!/usr/bin/env bash
# write by ddcw @https://github.com/ddcw/inspection
# mysql巡检脚本 . 仅支持本机巡检. 是 ddcw_inspection 的一个简化版本.
# v3.0 change log #版本和ddcw_inspection无关.
# 只有md格式的

#注: shell不方便数字比较.... 所以使用mysql来做

source /etc/profile
export LANG="en_US.UTF-8"
stty erase ^H

MDFILENAME="/tmp/ddcw_inspection_`hostname`_$(date '+%Y%m%d_%H%M%S').md"
START_DATETIME="`date '+%Y:%m:%d %H:%M:%S'`"
MYSQL_COM="mysql"
MYSQL_BIN="mysql"
MYSQL_COM_COMMENT="${MYSQL_COM}"
HELP_FLAG=false
PARAMS=$@
HOSTNAME=`hostname`
PORT=3306
SUGGESTION=""
SUMMARY=""
REQUIRE_PASSWORD=true
SHOW_DETAIL=false

#添加建议信息
add_suggestion(){
	SUGGESTION="${SUGGESTION}${@}\n"
}

#添加汇总信息
add_summary(){
	SUMMARY="${SUMMARY}\n${@}"
}

#使用mysql来做一些计算. 主要是大小比较
sql_com(){
	sql=$1
	value=$2
	[ -z ${value} ] && value=1
	if [ "`${MYSQL_COM} -NB -e \"${sql}\" 2>/dev/null`" == "${value}" ];then
		return 0
	else
		return 1
	fi
}

exit1(){
	echo "[`date "+%Y-%m-%d %H:%M:%S"]` [ERROR] ${@}"
	exit 1
}

#输出日志, 放到STDERROR 主要是方便重定向
log(){
	_msg="[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $@"
	echo -e ${_msg} >&2
}

TMD(){
	title_level=$1 #
	title_name=$2  #
	header=$3      #表头
	value=$4       #表
	echo -e "\n$(printf '%*s' ${title_level}'' | tr ' ' '#') ${title_name}" >> ${MDFILENAME}
	add_summary "\n\n############${title_name}#########"
	if [ "${value}" == "" ];then
		echo "无" >> ${MDFILENAME}
		add_summary "无\n"
	else
		echo -e "${header}" >> ${MDFILENAME}
		echo -e "${header}" | sed 's/[^|]/-/g' >> ${MDFILENAME}
		echo "${value}" | sed 's/\t/ | /g;s/^/| /;s/$/ |/' >> ${MDFILENAME}
		add_summary "${header}\n${value}"
	fi
}

# 仅输出header 和 普通内容
HTMD(){
	title_level=$1
	title_name=$2
	msg=$3
	echo -e "\n$(printf '%*s' ${title_level}'' | tr ' ' '#') ${title_name}" >> ${MDFILENAME}
	echo -e "\n${msg}\n" >> ${MDFILENAME}
}

params_init(){
	SHORT_OPTS="h:P:u:p:m:S:l:H:d"
	LONG_OPTS="host:,port:,user:,password:,mysql:,socket:,login-path:,help:,detail"
	PARSED_OPTS=$(getopt -o "$SHORT_OPTS" --long "$LONG_OPTS" --name "$0" -- "$@")
	MYSQL_COM=""
	MYSQL_COM_COMMENT=""
	if [[ $? -ne 0 ]]; then
		exit 2
	fi
	eval set -- "$PARSED_OPTS"
	
	while true; do
		case "$1" in
			-h|--host)
				MYSQL_COM="${MYSQL_COM} --host $2"
				MYSQL_COM_COMMENT="${MYSQL_COM_COMMENT} --host $2"
				HOSTNAME="$2"
				shift 2
				;;
			-P|--port)
				MYSQL_COM="${MYSQL_COM} --port $2"
				MYSQL_COM_COMMENT="${MYSQL_COM_COMMENT} --port $2"
				PORT=$2
				shift 2
				;;
			-u|--user)
				MYSQL_COM="${MYSQL_COM} --user $2"
				MYSQL_COM_COMMENT="${MYSQL_COM_COMMENT} --user $2"
				shift 2
				;;
			-p|--password)
				MYSQL_COM="${MYSQL_COM} -p$2"
				MYSQL_COM_COMMENT="${MYSQL_COM_COMMENT} -p******"
				shift 2
				;;
			-S|-s|--socket)
				MYSQL_COM="${MYSQL_COM} --socket $2"
				MYSQL_COM_COMMENT="${MYSQL_COM_COMMENT} --socket $2"
				shift 2
				;;
			-l|--login-path)
				MYSQL_COM="${MYSQL_COM} --login-path=$2"
				MYSQL_COM_COMMENT="${MYSQL_COM_COMMENT} --login-path=$2"
				shift 2
				;;
			-m|--mysql)
				MYSQL_BIN="$2"
				shift 2
				;;
			-H|--help)
				HELP_FLAG=true
				shift 1
				;;
			-d|--detail)
				SHOW_DETAIL=true
				shift 1
				;;
			--|-)
				shift
				break
				;;
			*)
				echo "Programming error. Please run --help ."
				echo "$@ ?????????????" | grep --color -- "${1}"
				exit 3
				;;
				
		esac
	done
	MYSQL_COM="${MYSQL_BIN} ${MYSQL_COM}"
	MYSQL_COM_COMMENT="${MYSQL_BIN} ${MYSQL_COM_COMMENT}"
}

help_this(){
	cat << EOF
MySQL巡检脚本 v3.0
    --host       host
    --port       port
    --user       user
    --password   password
    --socket     socket
    --login-path login-path-name
    --mysql      mysql command, example:/usr/bin/mysql
    --help       print this
    --detail     show detail

例子:
    sh $0 -h127.0.0.1 -P3314 -p123456
EOF
	exit 0
}

# 检查mysql能否连接, 是否有权限
check_pre(){
	#检查连接性
	if ${MYSQL_COM} -e 'select 1+1' >/dev/null 2>&1;then
		log "${MYSQL_COM_COMMENT} Connect Success"
	else
		exit1 "${MYSQL_COM_COMMENT} Connect Failed!!!"
	fi

	#检查权限
	#current_version=`${MYSQL_COM} -NB -e "show grants for current_user();"`
	#if echo "${current_version}" | grep "REPLICATION CLIENT" >/dev/null 2>&1 && echo "${current_version}" | grep "EXECUTE"  >/dev/null 2>&1 && echo "${current_version}" | grep "SELECT" >/dev/null 2>&1  ;then
	#	log "Privileges OK"
	#fi
	if ${MYSQL_COM} -e 'select * from sys.memory_global_total;' >/dev/null 2>&1 && ${MYSQL_COM} -e 'show slave status;' >/dev/null 2>&1; then
		log "Privileges OK"
	else
		exit1 "Privileges Failed"
	fi
	
}

i_baseinfo(){
	log "GET BASE INFO"
	log "GET HOST CPU INFO"
	cpu_socket=$(lscpu | awk -F ':' '{if ($1=="Socket(s)") print $2}' | awk '{print $1}')          #CPU物理数量(颗)
	cpu_cores=$(lscpu | awk -F ':' '{if ($1=="Core(s) per socket") print $2}' | awk '{print $1}')  #每颗CPU多少核
	cpu_thread=$(lscpu | awk -F ':' '{if ($1=="Thread(s) per core") print $2}' | awk '{print $1}') #每核多小线程
	cpu_type=$(lscpu | awk -F ':' '{if ($1=="Model name") print $2}' | sed 's/^\s*//g')           #CPU牌子

	log "GET HOST MEM INFO"
	mem_total=$(grep 'MemTotal' /proc/meminfo  | awk '{print $2}')  #总内存
	mem_free=$(grep 'MemFree' /proc/meminfo  | awk '{print $2}')    #未使用过的内存
	mem_available=$(grep 'MemAvailable' /proc/meminfo  | awk '{print $2}') #可用内存(包括buffer)
	swap_total=$(grep 'SwapTotal' /proc/meminfo  | awk '{print $2}')
	swap_available=$(grep 'SwapFree' /proc/meminfo  | awk '{print $2}')
	mem_pagesize=$(getconf PAGESIZE)
	
	mysql_status="`${MYSQL_COM} -NB -e 'status' 2>/dev/null`"
	msg="INSPECTION DATETIME\t${START_DATETIME}"
	msg="${msg}\nHOSTNAME\t${HOSTNAME}\nPORT\t${PORT}\nUPTIME\t`uptime | awk -F ',' '{print $1}'`\nLOAD\t`uptime | awk -F ',' '{print $(NF-2)$(NF-1)$NF}' | awk -F ':' '{print $NF}'`"
	msg="${msg}\nCPU_TYPE\t${cpu_type}\nCPU\t${cpu_socket} * ${cpu_cores} * ${cpu_thread} = $[ ${cpu_socket} * ${cpu_cores} * ${cpu_thread} ]"
	msg="${msg}\nMEM\t $[ ${mem_available} / 1024 ] MB / $[ ${mem_total} / 1024 ] MB"
	msg="${msg}\nSWAPPINESS\t`cat /proc/sys/vm/swappiness`"
	msg="${msg}\nMYSQL CLIENT VERSION\t`${MYSQL_BIN} --version --verbose`"
	server_version="`${MYSQL_COM} -NB -e 'select @@version;' 2>/dev/null`"
	msg="${msg}\nMYSQL SERVER VERSION\t${server_version}"
	msg="${msg}\nMYSQL UPTIME\t`echo -e \"${mysql_status}\" | awk '{if ($1==\"Uptime:\") {$1=\"\"; print $0}}'` (`${MYSQL_COM} -NB -e \"show global status like 'uptime';\" 2>/dev/null | awk '{print $NF}'` s)"
	log "GET MYSQL INNODB_BUFFER_POOL"
	innodb_buffer_pool_size_gb=`${MYSQL_COM} -NB -e 'select round(@@innodb_buffer_pool_size/1024/1024/1024,2);' 2>/dev/null`
	innodb_buffer_pool_hitrate=`${MYSQL_COM} -NB -e 'select round(avg(HIT_RATE)/10,2) from information_schema.INNODB_BUFFER_POOL_STATS;' 2>/dev/null`
	innodb_buffer_pool_used=`${MYSQL_COM} -NB -e 'select round(sum(FREE_BUFFERS)/sum(POOL_SIZE)*100,2) from information_schema.INNODB_BUFFER_POOL_STATS;' 2>/dev/null`
	msg="${msg}\nINNODB BUFFER POOL SIZE\t${innodb_buffer_pool_size_gb} GB"
	msg="${msg}\nINNODB BUFFER POOL HIT RATE\t${innodb_buffer_pool_hitrate} %"
	msg="${msg}\nINNODB BUFFER POOL USED\t${innodb_buffer_pool_used} %"
	log "GET MYSQL CONNECTION"
	current_connect=`${MYSQL_COM} -NB -e "show global status like 'Threads_connected';" 2>/dev/null | awk '{print $NF}'`
	connect_var=`${MYSQL_COM} -NB -e "select @@max_connections;" 2>/dev/null | awk '{print $NF}'`
	max_connect=`${MYSQL_COM} -NB -e "show global status like 'Max_used_connections';" 2>/dev/null | awk '{print $NF}'`
	msg="${msg}\nCONNECTION\t${current_connect}/${connect_var}"
	msg="${msg}\nMAX_CONNECTION\t${max_connect}/${connect_var}"
	msg="${msg}\nDATABASE COUNT\t`${MYSQL_COM} -NB -e \"select count(*) from information_schema.SCHEMATA where SCHEMA_NAME not in ('sys','performance_schema','mysql','information_schema');\" 2>/dev/null` ( `${MYSQL_COM} -NB -e \"select round(sum(data_length)/1024/1024/1024,2) from information_schema.tables where table_schema not in ('sys','performance_schema','mysql','information_schema');\" 2>/dev/null` GB)"
	msg="${msg}\nTABLE COUNT\t`${MYSQL_COM} -NB -e \"select count(*) from information_schema.tables where table_schema not in ('sys','performance_schema','mysql','information_schema');\" 2>/dev/null`"

	if [ "`echo \"${server_version}\" | grep -o '\b[0-9]\+\b' | head -2 | tr '\n' ' '`" == "5 7 " ];then
		if [ `echo "${server_version}" | grep -o '\b[0-9]\+\b' | tail -1` -lt 44 ];then
			add_suggestion "当前版本为: ${server_version} , 低于最新版 5.7.44 . 建议升级"
		fi
	fi
	sql_com "select ${innodb_buffer_pool_hitrate} < 99.5" 1 && add_suggestion "当前 innodb buffer pool 命中率较低(${innodb_buffer_pool_hitrate} < 99.5), 可考虑适当添加内存"
	sql_com "select ${max_connect}/${connect_var} > 0.75" 1 && add_suggestion "历史连接数较高(${max_connect}/${connect_var}) 建议增加 max_connections"
	TMD 1 "基础信息" "|对象|值|" "`echo -e \"${msg}\"`"

	#文件系统信息
	msg=""
	#datadir (肯定是绝对路径, 就直接查询了)
	datadir="`${MYSQL_COM} -NB -e \"select @@datadir\" 2>/dev/null`"
	msg="datadir\t${datadir}\t`df -hPT ${datadir} | tail -1 | awk '{print $1\"\t\"$2\"\t\"$3\"\t\"$4\"\t\"$5\"\t\"$6\"\t\"$7}' `"
	usage_persent=`df -hPT ${datadir} | awk '{sub(/\%/," "); if ($(NF-1) >  90) print $(NF-1)}'  | tail -n +2 `
	[ "${usage_persent}" == "" ] || add_suggestion "数据目录 ${datadir} 使用率超过90(当前使用率:${usage_persent}%). 建议扩空间"

	#binlogdir
	sql="SELECT 
    CASE 
        WHEN @@log_bin_basename is null THEN @@datadir
        WHEN LEFT(@@log_bin_basename, 1) = '/' THEN @@log_bin_basename
        ELSE CONCAT(@@datadir, @@log_bin_basename) 
    END AS result_path;"
	binlogdir="`${MYSQL_COM} -NB -e \"${sql}\" 2>/dev/null`"
	msg="${msg}\nbinlogdir\t${binlogdir}\t`df -hPT ${binlogdir%/*} | tail -1 | awk '{print $1\"\t\"$2\"\t\"$3\"\t\"$4\"\t\"$5\"\t\"$6\"\t\"$7}' `"
	usage_persent=`df -hPT ${binlogdir%/*} | awk '{sub(/\%/," "); if ($(NF-1) >  90) print $(NF-1)}'  | tail -n +2 `
	[ "${usage_persent}" == "" ] || add_suggestion "binlog目录 ${binlogdir%/*} 使用率超过90(当前使用率:${usage_persent}%). 建议扩空间"

	#redologdir
	sql="SELECT 
    CASE 
        WHEN @@innodb_log_group_home_dir is null THEN @@datadir
        WHEN LEFT(@@innodb_log_group_home_dir, 1) = '/' THEN @@innodb_log_group_home_dir
        ELSE CONCAT(@@datadir, @@innodb_log_group_home_dir) 
    END AS result_path;"
	redologdir="`${MYSQL_COM} -NB -e \"${sql}\" 2>/dev/null`"
	msg="${msg}\nredologdir\t${redologdir}\t`df -hPT ${redologdir} | tail -1 | awk '{print $1\"\t\"$2\"\t\"$3\"\t\"$4\"\t\"$5\"\t\"$6\"\t\"$7}' `"
	usage_persent=`df -hPT ${redologdir} | awk '{sub(/\%/," "); if ($(NF-1) >  90) print $(NF-1)}'  | tail -n +2 `
	[ "${usage_persent}" == "" ] || add_suggestion "redo log目录 ${redologdir} 使用率超过90(当前使用率:${usage_persent}%). 建议扩空间"

	#tmpdir
	sql="SELECT 
    CASE 
        WHEN @@tmpdir is null THEN @@datadir
        WHEN LEFT(@@tmpdir, 1) = '/' THEN @@tmpdir
        ELSE CONCAT(@@datadir, @@tmpdir) 
    END AS result_path;"
	tmpdir="`${MYSQL_COM} -NB -e \"${sql}\" 2>/dev/null`"
	msg="${msg}\ntmpdir\t${tmpdir}\t`df -hPT ${tmpdir} | tail -1 | awk '{print $1\"\t\"$2\"\t\"$3\"\t\"$4\"\t\"$5\"\t\"$6\"\t\"$7}' `"
	usage_persent=`df -hPT ${tmpdir} | awk '{sub(/\%/," "); if ($(NF-1) >  90) print $(NF-1)}'  | tail -n +2 `
	[ "${usage_persent}" == "" ] || add_suggestion "tmp目录 ${tmpdir} 使用率超过90(当前使用率:${usage_persent}%). 建议扩空间"
	
	TMD 0 "文件系统信息" "|对象|目录名|文件系统|类型|总大小|使用大小|可用大小|使用率|挂载点|" "`echo -e \"${msg}\"`"
}

i_check_database(){
	log "GET DATABASE INFO"
	#sql="select table_schema,sys.format_bytes(sum(data_length)),sys.format_bytes(sum(index_length)),sys.format_bytes(sum(data_free)) from information_schema.tables where table_schema not in ('sys','information_schema','performance_schema','mysql') group by table_schema order by 2;"
	sql="SELECT 
    a.table_schema,
    ROUND(SUM(a.data_length) / 1024 / 1024 / 1024,
            2) AS data_length_GB,
    ROUND(SUM(a.index_length / 1024 / 1024 / 1024),
            2) AS index_length_GB,
    ROUND(SUM(a.data_free / 1024 / 1024 / 1024), 2) AS data_free_GB,
    b.DEFAULT_CHARACTER_SET_NAME,
    b.DEFAULT_COLLATION_NAME
FROM
    information_schema.tables AS a join
    information_schema.schemata AS b
WHERE
    a.table_schema = b.SCHEMA_NAME
        AND a.table_schema NOT IN ('sys' , 'information_schema',
        'performance_schema',
        'mysql')
GROUP BY a.table_schema,b.DEFAULT_CHARACTER_SET_NAME,b.DEFAULT_COLLATION_NAME
ORDER BY 2 DESC
"
	msg="`${MYSQL_COM} -NB -e \"${sql}\" 2>/dev/null`"
	#add_summary "${msg}"
	TMD 2 "数据库大小" "|数据库名字|数据大小(GB)|索引大小(GB)|碎片大小(GB)|默认字符集|默认排序规则|" "`echo -e \"${msg}\"`"
}

i_check_table(){
	log "GET TABLE INFO"
	log "GET TOP10 TABLE"
	sql="SELECT 
    table_schema,
    table_name,
    TABLE_ROWS,
    ROUND(data_length / 1024 / 1024 / 1024, 2) AS data_length_GB,
    ROUND(index_length / 1024 / 1024 / 1024, 2) AS index_free_GB,
    ROUND(data_free / 1024 / 1024 / 1024, 2) AS data_free_GB
FROM
    information_schema.tables
WHERE
    table_schema NOT IN ('sys' , 'information_schema',
        'performance_schema',
        'mysql')
ORDER BY 4 DESC
LIMIT 10;"
	msg="`${MYSQL_COM} -NB -e \"${sql}\" 2>/dev/null`"
	TMD 2 "TOP10 表" "|数据库名|表名|行数|数据大小(GB)|索引大小(GB)|碎片大小(GB)|" "`echo -e \"${msg}\"`"

	#冷表 超过365天未使用的表 (information_schema.table是update_time 重启后就不准了. 所以直接查看OS)
	log "GET COLD TABLE"
	sql="SELECT 
    TABLE_SCHEMA,
    TABLE_NAME,
    ROUND(data_length / 1024 / 1024 / 1024, 2) AS data_length_GB,
    TABLE_ROWS,
    ENGINE,
    CREATE_TIME,
    UPDATE_TIME
FROM
    information_schema.tables
WHERE
    UPDATE_TIME < DATE_SUB(CURRENT_TIMESTAMP(),
        INTERVAL 365 DAY)
        AND TABLE_SCHEMA NOT IN ('sys' , 'information_schema',
        'mysql',
        'performance_schema');"
	datadir="`${MYSQL_COM} -NB -e 'select @@datadir' 2>/dev/null`"
	#find ${datadir} -mtime +180 -name '*.ibd' | awk -F '/' '{print $(NF-1)"\t"$NF}' | sed 's/.ibd$//'
	msg=""
	for filename in `find ${datadir} -mtime +365 -name '*.ibd'`;do
		msg="${msg}`echo ${filename} | awk -F '/' '{print $(NF-1)\"\t\"$NF}' | sed 's/.ibd$//'`\t`stat -c \"%y\" ${filename}`\n"
	done
	TMD 2 "冷表(超过1年未写的表)" "|数据库名|表名|最后修改时间|" "`echo -e \"${msg}\"`"
	[ "${msg}" == "" ] || add_suggestion "存在 `echo -e \"${msg}\" | wc -l` 张超过 1年 未使用的表, 建议对其进行归档"
	
	#非innodb表
	msg="`${MYSQL_COM} -NB -e \"select TABLE_SCHEMA,TABLE_NAME,ENGINE from information_schema.tables where ENGINE != 'InnoDB' and TABLE_SCHEMA not in ('sys','information_schema','mysql','performance_schema');\" 2>/dev/null`"
	TMD 2 "非INNODB表" "|数据库名|表名|存储引擎|" "`echo -e \"${msg}\"`"
	[ "${msg}" == "" ] || add_suggestion "存在 `echo -e \"${msg}\" | wc -l` 张 非Innodb表, 建议更改其存储引擎为Innodb."


	#碎片较高的表
	log "GET fragmented table"
	sql="SELECT 
    *
FROM
    (SELECT 
        TABLE_SCHEMA,
            TABLE_NAME,
            TABLE_ROWS,
            round(data_length/1024/1024/1024,2) as data_length_GB,
            round(data_free/1024/1024/1024,2) as data_free_GB, 
            ROUND(DATA_FREE / (DATA_LENGTH + DATA_FREE) * 100, 2) AS fragment_rate
    FROM
        information_schema.tables
    WHERE
        DATA_LENGTH > 0 and TABLE_ROWS > 1000000
            AND TABLE_SCHEMA NOT IN ('sys' , 'information_schema', 'mysql', 'performance_schema')) AS aa
WHERE
    aa.fragment_rate > 70 order by aa.fragment_rate desc;"
	msg="`${MYSQL_COM} -NB -e \"${sql}\" 2>/dev/null`"
	TMD 2 "碎片表" "|数据库名|表名|数据行数|数据大小(GB)|碎片大小(GB)|碎片率(%)|" "`echo -e \"${msg}\"`"
	[ "${msg}" == "" ] || add_suggestion "存在 `echo -e \"${msg}\" | wc -l` 张 碎片表, 建议优化碎片(OPTIMIZE TABLE TABLE_NAME or ALTER TABLE TABLE_NAME engine=Innodb. and then analyze table table_name)"
}

i_check_index(){
	#无主键的大表 大于500W
	log "GET NO PK TABLE"
	sql="SELECT 
    t.table_schema, t.table_name, t.table_rows, round(t.data_length/1024/1024/1024,2),CREATE_TIME
FROM
    information_schema.tables t
        LEFT JOIN
    information_schema.table_constraints tc ON t.table_schema = tc.table_schema
        AND t.table_name = tc.table_name
        AND tc.constraint_type = 'PRIMARY KEY'
WHERE
    t.table_schema NOT IN ('mysql' , 'information_schema',
        'performance_schema',
        'sys')
        AND tc.constraint_name IS NULL
        AND t.table_type = 'BASE TABLE' and t.table_rows >= 500000;"
	msg="`${MYSQL_COM} -NB -e \"${sql}\" 2>/dev/null`"
	TMD 2 "无主键的表" "|数据库名|表名|数据行数|数据大小(GB)|表创建时间|" "`echo -e \"${msg}\"`"
	[ "${msg}" == "" ] || add_suggestion "存在 `echo -e \"${msg}\" | wc -l` 张 无主键的表, 建议添加主键(实在没得合适的字段, 可以使用自增ID)"

	#未使用的索引 uptime>30
	mysql_uptime="`${MYSQL_COM} -NB -e \"show global status like 'uptime';\" 2>/dev/null | awk '{print $NF}'`"
	greate_tiem=$[ 30 * 24 * 3600 ]
	if [ ${mysql_uptime} -ge ${greate_tiem} ];then
		log "GET NO USED INDEX"
		sql="select object_schema,object_name,index_name from sys.schema_unused_indexes where object_schema not in ('mysql' , 'information_schema', 'performance_schema','sys');"
		msg="`${MYSQL_COM} -NB -e \"${sql}\" 2>/dev/null`"
		TMD 2 "未使用的索引" "|数据库名|表名|索引名|" "`echo -e \"${msg}\"`"
		[ "${msg}" == "" ] || add_suggestion "存在 `echo -e \"${msg}\" | wc -l` 个 未使用的索引, 可考虑删掉这部分未使用的索引, 以提高数据写入速度.)"
	fi

	#无索引的表 (无主键可以包含这个的...)
	log "GET NO INDEX TABLE"
	sql="SELECT 
    t.TABLE_SCHEMA, t.TABLE_NAME
FROM
    information_schema.TABLES t
        LEFT JOIN
    information_schema.STATISTICS s ON t.TABLE_SCHEMA = s.TABLE_SCHEMA
        AND t.TABLE_NAME = s.TABLE_NAME
WHERE
    t.TABLE_SCHEMA NOT IN ('information_schema' , 'mysql', 'performance_schema', 'sys')
GROUP BY t.TABLE_SCHEMA , t.TABLE_NAME
HAVING COUNT(s.INDEX_NAME) = 0;"
	msg="`${MYSQL_COM} -NB -e \"${sql}\" 2>/dev/null`"
	TMD 2 "无索引的表" "|数据库名|表名|" "`echo -e \"${msg}\"`"
	[ "${msg}" == "" ] || add_suggestion "存在 `echo -e \"${msg}\" | wc -l` 张无索引的表, 可考虑加个索引"

	#冗余索引
	log "GET redundant_indexes"
	sql="select table_schema,table_name,dominant_index_name,dominant_index_columns,redundant_index_name,redundant_index_columns,sql_drop_index from sys.schema_redundant_indexes"
	msg="`${MYSQL_COM} -NB -e \"${sql}\" 2>/dev/null`"
	#msg=`echo -e "${msg}" | sed 's/\`/\\\\\`/g'`
	TMD 2 "冗余索引" "|数据库名|表名|主索引名|主索引字段|冗余索引名|冗余索引字段|建议SQL|" "`echo -e \"${msg}\"`"
	[ "${msg}" == "" ] || add_suggestion "存在 `echo -e \"${msg}\" | wc -l` 个 冗余索引, 建议删掉冗余索引 (可提高数据写入速度,可节省磁盘空间))"

}

i_check_user(){
	#密码相同的账号
	log "GET SAME PASSWORD FOR ACCOUNT"
	sql="SELECT 
    '*****' as password,
    GROUP_CONCAT(CONCAT(user, '@', host)
        SEPARATOR ', ') AS user_hosts
FROM
    mysql.user
WHERE
    authentication_string <> ''
        AND user NOT IN ('mysql.sys' , 'mysql.session', 'mysql.infoschema')
GROUP BY authentication_string
HAVING COUNT(*) > 1;"
	msg="`${MYSQL_COM} -NB -e \"${sql}\" 2>/dev/null`"
	TMD 2 "密码相同的账号" "|密码(脱敏)|账号|" "`echo -e \"${msg}\"`"
	[ "${msg}" == "" ] || add_suggestion "存在 `echo -e \"${msg}\" | wc -l` 套 密码相同的账号, 建议修改其密码"

	#密码快过期的账号(<30天)
	sql="SELECT 
    CONCAT(user, '@', host) AS account,
    password_last_changed,
    CASE
        WHEN
            password_lifetime IS NOT NULL
                AND password_lifetime < 30
        THEN
            password_last_changed + INTERVAL 30 DAY
        ELSE password_last_changed + INTERVAL GREATEST(password_lifetime - 30, 0) DAY
    END AS expire_date
FROM
    mysql.user
WHERE
    (password_lifetime IS NOT NULL
        AND password_lifetime < 30)
        OR (password_last_changed <= CURDATE() - INTERVAL GREATEST(password_lifetime - 30, 0) DAY);"
	msg="`${MYSQL_COM} -NB -e \"${sql}\" 2>/dev/null`"
	TMD 2 "密码快过期的账号" "|账号||上次修改时间|到期时间|" "`echo -e \"${msg}\"`"
	[ "${msg}" == "" ] || add_suggestion "存在 `echo -e \"${msg}\" | wc -l` 个密码要过期的账号, 请注意及时修改密码"

	#弱口令(含账号密码相同的账号)
	password_dic="123456 123 1234 12345678 admin abc123 qwerty P@ssw0rd mysql root password 1234567890 abc abcdefg" #弱密码字典, 可自行添加
	sql="SELECT CONCAT(user, '@', host) as account FROM mysql.user where authentication_string = CONCAT('*', UPPER(SHA1(UNHEX(SHA1(user)))))"
	msg="`${MYSQL_COM} -NB -e \"${sql}\" 2>/dev/null`"
	for password in ${password_dic}; do 
		tmpsql="SELECT CONCAT(user, '@', host) as account FROM mysql.user where authentication_string = CONCAT('*', UPPER(SHA1(UNHEX(SHA1('${password}')))));"
		tmpmsg="`${MYSQL_COM} -NB -e \"${tmpsql}\" 2>/dev/null`"
		[ "${tmpmsg}" == "" ] || msg="${msg}\n${tmpmsg}"
	done
	TMD 2 "弱口令账号" "|弱口令账号|" "`echo -e \"${msg}\"`"
	[ "${msg}" == "" ] || add_suggestion "存在 `echo -e \"${msg}\" | wc -l` 个账号 的密码是弱口令, 建议修改其密码"

	#host为%的账号 感觉没必要. 本脚本偏向巡检,而非安全. 就先不写了吧..

	#user为''的账号
	nulluser="`${MYSQL_COM} -NB -e \"select concat(user,'@',host) from mysql.user where user='';\" 2>/dev/null`"
	if [ "${nulluser}" != "" ];then
		TMD 2 "用户名为空的账号" "|用户名为空的账号|" "`echo -e \"${nulluser}\"`"
		add_suggestion "存在 `echo -e \"${nulluser}\" | wc -l` 个 用户名为空的账号, 建议删除该账号"
	fi

	#有super权限的非root账号
	sql="select concat(user,'@',host) from mysql.user where user not in ('root','mysql.session') and Super_priv='Y';"
	msg="`${MYSQL_COM} -NB -e \"${sql}\" 2>/dev/null`"
	TMD 2 "Super权限的账号" "|有Super权限的账号|" "`echo -e \"${msg}\"`"
	[ "${msg}" == "" ] || add_suggestion "存在 `echo -e \"${msg}\" | wc -l` 个含有Super权限的非root账号, 建议回收其超级权限"
	
}

#这一块内容较多: 主要是从 global status获取信息
i_check_innodb(){
	msg=""
	#innodb buffer pool 命中率 和大小(要求尽可能>=1GB, 尽量维持在40-60%的MEM)

	#innodb读命中率 Innodb_buffer_pool_read_requests / (Innodb_buffer_pool_reads+Innodb_buffer_pool_read_requests)
	Innodb_buffer_pool_read_requests="`${MYSQL_COM} -NB -e \"show global status like 'Innodb_buffer_pool_read_requests';\" 2>/dev/null | awk '{print $NF}'`" #逻辑读
	Innodb_buffer_pool_reads="`${MYSQL_COM} -NB -e \"show global status like 'Innodb_buffer_pool_reads';\" 2>/dev/null | awk '{print $NF}'`" #物理读
	Innodb_read_hits="`${MYSQL_COM} -NB -e \"select round(${Innodb_buffer_pool_read_requests}/(${Innodb_buffer_pool_read_requests}+${Innodb_buffer_pool_reads})*100,2)\" 2>/dev/null`"
	if [ "`${MYSQL_COM} -NB -e \"select ${Innodb_read_hits} < 99.5\" 2>/dev/null`" == "1" ];then
		if [ "`${MYSQL_COM} -NB -e \"select ${Innodb_read_hits} > 95.0\" 2>/dev/null`" == "1" ];then
			add_suggestion "Innodb读命中率(${Innodb_read_hits}%)较低. 可以找找原因."
			msg="${msg}innodb读命中率\t${Innodb_read_hits}\t还行\n"
		else
			add_suggestion "Innodb读命中率(${Innodb_read_hits}%)非常低. 建议跑路."
			msg="${msg}innodb读命中率\t${Innodb_read_hits}\t较低\n"
		fi
	else
		msg="${msg}innodb读命中率\t${Innodb_read_hits}\t很高, 棒棒哒!\n"
	fi

	#table open cache 命中率
	Table_open_cache_hits="`${MYSQL_COM} -NB -e \"show global status like 'Table_open_cache_hits';\" 2>/dev/null | awk '{print $NF}'`" #表缓存命中数量
	Table_open_cache_misses="`${MYSQL_COM} -NB -e \"show global status like 'Table_open_cache_misses';\" 2>/dev/null | awk '{print $NF}'`" #表缓存未命中数量
	Table_open_cache_overflows="`${MYSQL_COM} -NB -e \"show global status like 'Table_open_cache_overflows';\" 2>/dev/null | awk '{print $NF}'`" #The number of overflows for the open tables cache
	Table_open_cache_hit="`${MYSQL_COM} -NB -e \"select round(${Table_open_cache_hits}/(${Table_open_cache_hits}+${Table_open_cache_misses})*100,2)\" 2>/dev/null`"
	msg="${msg}Table_open_cache_hit\t${Table_open_cache_hit}%\t表缓存命中率(${Table_open_cache_hits}/(${Table_open_cache_hits}+${Table_open_cache_misses}))\n"

	#redo 等待 Innodb_log_waits (太大的话, 可以考虑增加innodb log 大小或者数量)
	msg="${msg}innodb日志等待\t`${MYSQL_COM} -NB -e\"show global status like 'Innodb_log_waits';\" 2>/dev/null`\tInnodb_log_waits\n"

	#读写比(行数)
	Innodb_rows_read="`${MYSQL_COM} -NB -e \"show global status like 'Innodb_rows_read';\" 2>/dev/null | awk '{print $NF}'`"
	Innodb_rows_inserted="`${MYSQL_COM} -NB -e \"show global status like 'Innodb_rows_inserted';\" 2>/dev/null | awk '{print $NF}'`"
	Innodb_rows_deleted="`${MYSQL_COM} -NB -e \"show global status like 'Innodb_rows_deleted';\" 2>/dev/null | awk '{print $NF}'`"
	Innodb_rows_updated="`${MYSQL_COM} -NB -e \"show global status like 'Innodb_rows_updated';\" 2>/dev/null | awk '{print $NF}'`"
	Innodb_rows_rw_rate="`${MYSQL_COM} -NB -e \"select round(${Innodb_rows_read}/(0.001+${Innodb_rows_inserted}+${Innodb_rows_deleted}+${Innodb_rows_updated})*100,2)\" 2>/dev/null`"
	msg="${msg}innodb读写比\t${Innodb_rows_rw_rate}%\tread_rows:${Innodb_rows_read} insert_rows:${Innodb_rows_inserted} delete_rows:${Innodb_rows_deleted} update_rows:${Innodb_rows_updated}\n"

	# tmp_table_size 是否合理  Created_tmp_disk_tables / Created_tmp_tables 要小于10万分之1
	Created_tmp_disk_tables="`${MYSQL_COM} -NB -e \"show global status like 'Created_tmp_disk_tables';\" 2>/dev/null | awk '{print $NF}'`"
	Created_tmp_tables="`${MYSQL_COM} -NB -e \"show global status like 'Created_tmp_tables';\" 2>/dev/null | awk '{print $NF}'`"
	Created_tmp_table_disk_rate="`${MYSQL_COM} -NB -e \"select round(${Created_tmp_disk_tables}/(0.00001+${Created_tmp_tables})*10000,2)\" 2>/dev/null`"
	msg="${msg}磁盘临时表占比\t万分之 ${Created_tmp_table_disk_rate}\tCreated_tmp_disk_tables:${Created_tmp_disk_tables} Created_tmp_tables:${Created_tmp_tables}\n"
	if [ "`${MYSQL_COM} -NB -e \"select ${Created_tmp_table_disk_rate} > 5\" 2>/dev/null`" == "1" ];then
		add_suggestion "磁盘临时表使用率(万分之${Innodb_read_hits})较高. 可以考虑增加@@tmp_table_size."
	fi

	# 文件打开使用比 show global status like 'Open_files';

	#慢查询百分比 Slow_queries/Questions
	Slow_queries="`${MYSQL_COM} -NB -e \"show global status like 'Slow_queries';\" 2>/dev/null | awk '{print $NF}'`"
	Questions="`${MYSQL_COM} -NB -e \"show global status like 'Questions';\" 2>/dev/null | awk '{print $NF}'`"
	Slow_queries_rate="`${MYSQL_COM} -NB -e \"select round((${Slow_queries}+0)/${Questions}*10000,2)\" 2>/dev/null`"
	msg="${msg}慢查询占比\t万分之 ${Slow_queries_rate}\tSlow_queries:${Slow_queries} Questions:${Questions}\n"
	if [ "`${MYSQL_COM} -NB -e \"select ${Slow_queries_rate} > 1\" 2>/dev/null`" == "1" ];then
		add_suggestion "慢查询占比有点高(万分之${Slow_queries_rate}), 可以看下慢查询日志."
	fi

	
	# PS内存使用 SHOW ENGINE PERFORMANCE_SCHEMA STATUS performance_schema.memory
	psmem=`${MYSQL_COM} -NB -e "SHOW ENGINE PERFORMANCE_SCHEMA STATUS;" 2>/dev/null | awk '{if ($2=="performance_schema.memory") {printf "%.2fMB" , $NF/1024/1024}}'`
	msg="${msg}performance内存\t${psmem}\tperformance_schema.memory"

	TMD 2 "状态" "|对象|值|描述|" "`echo -e \"${msg}\"`"

	
}

#参数检查
i_check_variables(){
	msg=""
	# 双1
	innodb_flush_log_at_trx_commit=`${MYSQL_COM} -NB -e 'select @@innodb_flush_log_at_trx_commit;' 2>/dev/null`
	if [ "${innodb_flush_log_at_trx_commit}" != "1" ];then
		add_suggestion "innodb_flush_log_at_trx_commit 当前是 ${innodb_flush_log_at_trx_commit} 建议设置为 1"
	fi
	msg="${msg}innodb_flush_log_at_trx_commit\t${innodb_flush_log_at_trx_commit}\tredo log刷盘策略.<br />0: 每秒刷盘.<br />1:每个事务提交时刷盘(默认,建议)<br />2:每个事务提交后写日志, 每秒刷1次盘"

	sync_binlog=`${MYSQL_COM} -NB -e 'select @@sync_binlog;' 2>/dev/null`
	if [ "${sync_binlog}" != "1" ];then
		add_suggestion "sync_binlog 当前是 ${sync_binlog} 建议设置为 1"
	fi
	msg="${msg}sync_binlog\t${sync_binlog}\tbinlog刷盘策略.<br />0: OS去刷日志.<br />1:每个事务提交时刷盘(默认,建议)<br />N:每N个事务提交后刷盘\n"

	# 内存, 最上面有(仅展示)
	msg="${msg}innodb_buffer_pool_size\t`${MYSQL_COM} -NB -e 'select round(@@innodb_buffer_pool_size/1024/1024/1024,2);' 2>/dev/null` GB\tinnodb buffer\n"
	msg="${msg}innodb_buffer_pool_instances\t`${MYSQL_COM} -NB -e 'select @@innodb_buffer_pool_instances;' 2>/dev/null` \tinnodb buffer 实例数量\n"
	msg="${msg}innodb_buffer_pool_chunk_size\t`${MYSQL_COM} -NB -e 'select round(@@innodb_buffer_pool_chunk_size/1024/1024/1024,2);' 2>/dev/null` GB\tinnodb buffer 每个实例大小\n"

	
	# 每个线程会使用的内存
	msg="${msg}read_buffer_size\t`${MYSQL_COM} -NB -e 'select round(@@read_buffer_size/1024,2);' 2>/dev/null` KB\tfor myisam\n"
	msg="${msg}read_rnd_buffer_size\t`${MYSQL_COM} -NB -e 'select round(@@read_rnd_buffer_size/1024,2);' 2>/dev/null` KB\tfor myisam\n"
	msg="${msg}sort_buffer_size\t`${MYSQL_COM} -NB -e 'select round(@@sort_buffer_size/1024/1024,2);' 2>/dev/null` MB\t排序\n"
	msg="${msg}thread_stack\t`${MYSQL_COM} -NB -e 'select round(@@thread_stack/1024/1024,2);' 2>/dev/null` MB\t堆\n"
	msg="${msg}join_buffer_size\t`${MYSQL_COM} -NB -e 'select round(@@join_buffer_size/1024/1024,2);' 2>/dev/null` MB\tjoin\n"
	msg="${msg}binlog_cache_size\t`${MYSQL_COM} -NB -e 'select round(@@binlog_cache_size/1024,2);' 2>/dev/null` KB\tbinlog缓存\n"
	msg="${msg}tmp_table_size\t`${MYSQL_COM} -NB -e 'select round(@@tmp_table_size/1024/1024,2);' 2>/dev/null` MB\t临时表\n"
	

	TMD 2 "变量" "|变量名|值|描述|" "`echo -e \"${msg}\"`"
}

i_check_error_log(){
	sql="SELECT 
    CASE 
        WHEN @@log_error is null THEN @@datadir
        WHEN LEFT(@@log_error, 1) = '/' THEN @@log_error
        ELSE CONCAT(@@datadir, @@log_error) 
    END AS result_path;"
	errorlog="`${MYSQL_COM} -NB -e \"${sql}\" 2>/dev/null`"
	# 最近一次启停记录. 感觉没必要...

	# 升级记录
	versionlist=`grep 'Version: ' ${errorlog} | awk -F 'Version:' '{print $2}' | awk -F "'" '{print $2}' | sed '/^$/d' | uniq -c`
	if [ `echo -e "${versionlist}" | wc -l` -ge 2 ];then
		add_suggestion "存在升级记录, ${versionlist}"
	fi

	# 最近10000条 里面包含的ERROR , 取最近10条
	errorloglist=`tail -2000 ${errorlog} | grep '\[ERROR\]' | tail -10`
	if [ "${errorloglist}" != "" ];then
		TMD 2 "ERROR LOG" "|LOG|" "`echo -e \"${errorloglist}\"`"
		add_suggestion "存在ERROR LOG, error log:${errorlog}"
		
	fi
}

i_check_slow_log(){
	# 最慢的10条SQL(sys.format_statement 脱敏)
	sql="SELECT 
    CASE 
        WHEN @@slow_query_log_file is null THEN @@datadir
        WHEN LEFT(@@slow_query_log_file, 1) = '/' THEN @@slow_query_log_file
        ELSE CONCAT(@@datadir, @@slow_query_log_file) 
    END AS result_path;"
	slowlog="`${MYSQL_COM} -NB -e \"${sql}\" 2>/dev/null`"
	msg=`tail -2000 ${slowlog} | grep  "^# Query_time: " | sort -n -k 3 -r | head | awk '{print $3"\t"$5"\t"$7"\t"$9}'`
	TMD 2 "慢日志" "|Query_time|Lock_time|Rows_sent|Rows_examined|" "`echo -e \"${msg}\"`"
	[ "${msg}" == "" ] || add_suggestion "存在慢日志, slow log${slowlog}"
}

#使用Python2 解析上一个binlog.
#如果没得python2 或者上一个binlog < 10MB 就跳过
i_check_binlog(){
	# 大事务 参考:anabinlog_3.py

	# TOP10表 参考:anabinlog_3.py

	#binlog_cache_size 是否合理, Binlog_cache_disk_use/Binlog_cache_use
	Binlog_cache_disk_use="`${MYSQL_COM} -NB -e \"show global status like 'Binlog_cache_disk_use';\" 2>/dev/null | awk '{print $NF}'`"
	Binlog_cache_use="`${MYSQL_COM} -NB -e \"show global status like 'Binlog_cache_use';\" 2>/dev/null | awk '{print $NF}'`"
	Binlog_cache_disk_use_rate="`${MYSQL_COM} -NB -e \"select round(${Binlog_cache_disk_use}/(0.00001+${Binlog_cache_use})*100,2)\" 2>/dev/null`"
	if [ "`${MYSQL_COM} -NB -e \"select ${Binlog_cache_disk_use_rate} > 1\" 2>/dev/null`" == "1" ];then
		add_suggestion "binlog_cache_disk_useage(百分之${Binlog_cache_disk_use_rate})较高. 可以考虑增加@@binlog_cache_size (参考值计算脚本: binlog_trx_4kf.py )"
	fi
}

i_check_cluster(){
	#主从
	show_slave_status="`${MYSQL_COM} -B -e 'show slave status\G' 2>/dev/null | awk -F ': ' '{print $1\"\t\"$2}'`"
	show_processlist="`${MYSQL_COM} -NB -e 'select user,host from information_schema.processlist where Command=\"Binlog Dump\";' 2>/dev/null`"
	current_role=""
	if [ "${show_slave_status}" != "" ];then
		current_role="${current_role}从库 "
		TMD 2 "主从信息(当前为从库)" "|对象|值|" "`echo -e \"${show_slave_status}\"`"
		if [ "`echo \"${show_slave_status}\" |  awk '{if (($1=="Slave_IO_Running"||$1=="Slave_SQL_Running") && $2!="Yes") print $2}'`" != "" ];then
			add_suggestion "主从存在异常. 请查看 <主从信息>"
		fi
	fi
	if [ "${show_processlist}" != "" ];then
		current_role="${current_role}主库 "
		TMD 2 "主从信息(当前为主库)" "|用户|主机地址|" "`echo -e \"${show_processlist}\"`"
	fi

	#MGR TODO

	#PXC TODO
	return 0
}

i_check_resource(){
	#资源检查
	#CPU
	cpu_info=`top -n 1 | grep '^%Cpu(s)'` #0.0 us  0.0 wa
	#内存
	#网络
	net_drop=`ifconfig  | grep dropped`
	#磁盘
	return 0
}

i_check_backup(){
	#备份要自己根据环境写
	return 0
}

#自定义的
i_check_post(){
	#暂无
	return 0
}

params_init ${PARAMS}
${HELP_FLAG} && help_this
echo -e "${PARAMS}" | grep -- '--help' >/dev/null 2>&1 && help_this
log "MYSQL_COM: ${MYSQL_COM}"
log "MYSQL_BIN:${MYSQL_BIN}"
check_pre
#value=`${MYSQL_COM} -NB -e "select user,host,plugin from mysql.user;" 2>/dev/null`
#TMD 1 "账号信息" "|USER|HOST|PLUGIN|" "${value}"
i_baseinfo
log "GET DETAIL"
HTMD 1 "巡检详情" "巡检项详情. 涉及到库, 表, 所以, 账号, 存储引擎, 日志, 集群(主从,MGR) 资源(CPU,内存,IO,网络)"
i_check_database #库表大小和字符集等信息
i_check_table #大表, 冷表,非innodb表, 碎片率较高的表(表行数大于100W,碎片率达到70%)
i_check_index #无主键, 无效索引(未使用的, 开机时间必须大于7天才检查), 冗余索引
i_check_user #权限, 弱口令, 密码重复, host为%
i_check_innodb  #主要是global status 的 innodb信息, 再加上一些其它信息 比较杂 
i_check_variables #变量检查.
i_check_error_log #ERROR, 启停
i_check_slow_log #tail -20000 /data/mysql_3314/mysqllog/dblogs/slow3314.log | grep  "^# Query_time: " | sort -n -k 3 | tail
i_check_binlog  #大事务.
i_check_cluster #主从,mgr,pxc
i_check_resource #资源检查, cup, 内存, IO, 网络(发包,丢包等, OS以及数据库的)
i_check_backup #备份检查, 要自定义, 我也不知道你备份在哪的...
#value1=`${MYSQL_COM} -NB -e "select user,host,plugin from mysql.user;" 2>/dev/null`
#value2=`${MYSQL_COM} -NB -e "select user,host,plugin from mysql.user;" 2>/dev/null`
#value="${value1}\n${value2}"
#value="`echo -e \"${value}\" | sort | uniq`"
#add_summary "${value}"
#TMD 1 "账号信息" "|USER|HOST|PLUGIN|" "${value}"
if ${SHOW_DETAIL};then
	echo -e "${SUMMARY}"
fi
echo -e "\n\n${SUGGESTION}" 1>&2
TMD 1 "建议" "|建议|" "`echo -e \"${SUGGESTION}\"`"
log "FILENAME:${MDFILENAME}"
