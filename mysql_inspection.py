import pymysql
import time
import json
import argparse
import subprocess
import paramiko

#版本定义
VERSION = "0.3"

#作者
#AUTHOR = "ddcw"


	


def main(*args,**kwargs):
	HOST = kwargs["HOST"]
	PORT = kwargs["PORT"]
	USER = kwargs["USER"]
	PASSWORD = kwargs["PASSWORD"]
	SOCKET = kwargs["SOCKET"]
	SSH_PORT = kwargs["SSH_PORT"]
	SSH_USER = kwargs["SSH_USER"]
	SSH_PASSWORD = kwargs["SSH_PASSWORD"]
	SSH_PKEY = kwargs["SSH_PKEY"]
	NO_HOST = kwargs["NO_HOST"]
	SAVED_FILE = kwargs["SAVED_FILE"]
	NO_FILE = kwargs["NO_FILE"]
	AUTHOR = kwargs["AUTHOR"]
	SLOW_LOG_ROWS = kwargs["SLOW_LOG_ROWS"]

	conn = pymysql.connect(
	host=HOST,
	port=PORT,
	user=USER,
	password=PASSWORD,
	database="information_schema",
	unix_socket = SOCKET,
	)

	cursor = conn.cursor()


	local_time = time.localtime()

	#CAN_SSH
	CAN_SSH = False
	try:
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		if SSH_PKEY is not None:
			ssh.connect(hostname=HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASSWORD, pkey=paramiko.RSAKey.from_private_key_file(SSH_PKEY))
		else:
			ssh.connect(hostname=HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASSWORD, )
		CAN_SSH = True
	except Exception as e:
		#print(e)
		pass
		


	#IS_LOCAL 是否为本机
	IS_LOCAL = False


	def get_local_command_result(comm):
		timeout = 30 #超过30秒没有执行完,就kill了
		with subprocess.Popen(comm, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as f:
			try:
				return {"CODE":f.wait(timeout),"DATA":str(f.stdout.read().rstrip(),encoding="utf-8")}
			except:
				f.kill()
				return {"CODE":256, "DATA":"TIMEOUT ({timeout})".format(timeout=timeout)}
		#return str(subprocess.Popen(comm, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read().rstrip(),encoding="utf-8")



	local_ip = get_local_command_result("ifconfig | grep inet  | awk '{print $2}'")["DATA"]
	local_hostname = get_local_command_result("cat /proc/sys/kernel/hostname")["DATA"]
	if HOST in local_ip or HOST == local_hostname or HOST == "0.0.0.0" or HOST == "localhost":
		IS_LOCAL = True

	

	inspection_info = {}
	inspection_info["DATA"] = {}
	inspection_info["DATA"]["HAVE_DATA"] = True
	inspection_info["DATA"]["INFORMATION_SCHEMA"] = {}
	inspection_info["DATA"]["INFORMATION_SCHEMA"]["HAVE_DATA"] = True
	inspection_info["DATA"]["PERFORMANCE_SCHEMA"] = {}
	inspection_info["DATA"]["PERFORMANCE_SCHEMA"]["HAVE_DATA"] = True
	inspection_info["DATA"]["MYSQL"] = {}
	inspection_info["DATA"]["MYSQL"]["HAVE_DATA"] = True
	inspection_info["DATA"]["SYS"] = {}
	inspection_info["DATA"]["SYS"]["HAVE_DATA"] = True
	inspection_info["HOST_INFO"]={}
	inspection_info["HOST_INFO"]["HAVE_DATA"] = True

	inspection_info["DBTYPE"] = "MYSQL"
	inspection_info["AUTHOR"] = AUTHOR
	inspection_info["HOST"] = HOST
	inspection_info["PORT"] = PORT
	inspection_info["USER"] = USER
	inspection_info["START_TIME"] = time.strftime('%Y%m%d_%H%M%S', local_time)
	inspection_info["VERSION"] = VERSION

		
	#定义shell执行函数
	if IS_LOCAL:
		def get_comm_info(comm):
			return get_local_command_result(comm)
	elif CAN_SSH:
		def get_comm_info(comm):
			stdin, stdout, stderr = ssh.exec_command(comm)
			return {"CODE":stdout.channel.recv_exit_status(), "DATA":str(stdout.read().rstrip(),encoding="utf-8")}
			#return str(stdout.read().rstrip(),encoding="utf-8")
	else:
		inspection_info["HOST_INFO"]["HAVE_DATA"] = False

	if NO_HOST:
		inspection_info["HOST_INFO"]["HAVE_DATA"] = False


	#定义sql执行函数
	def get_info(sql):
		try:
			cursor.execute(sql)
			data = cursor.fetchall()
			code = True
		except Exception as e:
			data = " FAILED to execute ( {sql} ). ERROR IS :{e}".format(sql=sql,e=e)
			code = False
		finally:
			return {"T":code,"DATA":data}


	#定义保存文件
	if SAVED_FILE is None:
		SAVED_FILE = "ddcw_mysql_xunjian_{host}_{port}_{date}.json".format(host=HOST, port=PORT, date=time.strftime('%Y%m%d_%H%M%S', local_time))
	


	if not get_info("use mysql")["T"]:
		inspection_info["DATA"]["MYSQL"]["HAVE_DATA"] = False
	if not get_info("use sys")["T"]:
		inspection_info["DATA"]["SYS"]["HAVE_DATA"] = False
	if not get_info("use performance_schema")["T"]:
		inspection_info["DATA"]["PERFORMANCE_SCHEMA"]["HAVE_DATA"] = False
	if not get_info("use information_schema")["T"]:
		inspection_info["DATA"]["INFORMATION_SCHEMA"]["HAVE_DATA"] = False



	#基础信息已调好, 开始收集数据
	

	#收集数据库信息 information_schema库下的信息
	if inspection_info["DATA"]["INFORMATION_SCHEMA"]["HAVE_DATA"]:
		inspection_info["DATA"]["INFORMATION_SCHEMA"]["schemata"] = get_info("select CATALOG_NAME,SCHEMA_NAME,DEFAULT_CHARACTER_SET_NAME,DEFAULT_COLLATION_NAME from information_schema.schemata WHERE SCHEMA_NAME NOT IN ('mysql', 'performance_schema', 'information_schema', 'sys');")["DATA"] #数据库表
		inspection_info["DATA"]["INFORMATION_SCHEMA"]["tables"] = get_info("select TABLE_CATALOG,TABLE_SCHEMA,TABLE_NAME,TABLE_TYPE,ENGINE,VERSION,ROW_FORMAT,TABLE_ROWS,AVG_ROW_LENGTH,DATA_LENGTH,MAX_DATA_LENGTH,INDEX_LENGTH,DATA_FREE,AUTO_INCREMENT,CREATE_TIME,UPDATE_TIME,CHECK_TIME,TABLE_COLLATION,CHECKSUM,CREATE_OPTIONS,TABLE_COMMENT from information_schema.tables where TABLE_SCHEMA not in ('sys','mysql','information_schema','performance_schema');")["DATA"] #表
		inspection_info["DATA"]["INFORMATION_SCHEMA"]["columns"] = get_info("select TABLE_CATALOG,TABLE_SCHEMA,TABLE_NAME,COLUMN_NAME,ORDINAL_POSITION,COLUMN_DEFAULT,IS_NULLABLE,DATA_TYPE,CHARACTER_MAXIMUM_LENGTH,CHARACTER_OCTET_LENGTH,NUMERIC_PRECISION,NUMERIC_SCALE,DATETIME_PRECISION,CHARACTER_SET_NAME,COLLATION_NAME,COLUMN_TYPE,COLUMN_KEY,EXTRA,PRIVILEGES,COLUMN_COMMENT,GENERATION_EXPRESSION from information_schema.COLUMNS where TABLE_SCHEMA not in ('sys','mysql','information_schema','performance_schema');")["DATA"] #字段
		inspection_info["DATA"]["INFORMATION_SCHEMA"]["statistics"] = get_info("select TABLE_CATALOG,TABLE_SCHEMA,TABLE_NAME,NON_UNIQUE,INDEX_SCHEMA,INDEX_NAME,SEQ_IN_INDEX,COLUMN_NAME,COLLATION,CARDINALITY,SUB_PART,PACKED,NULLABLE,INDEX_TYPE,COMMENT,INDEX_COMMENT from information_schema.statistics where TABLE_SCHEMA not in ('sys','mysql','information_schema','performance_schema') ;")["DATA"] 
		inspection_info["DATA"]["INFORMATION_SCHEMA"]["user_pri"] = get_info("select GRANTEE,TABLE_CATALOG,PRIVILEGE_TYPE,IS_GRANTABLE from information_schema.USER_PRIVILEGES;")["DATA"] #权限表
		inspection_info["DATA"]["INFORMATION_SCHEMA"]["db_pri"] = get_info(" select Host,Db,User,Select_priv,Insert_priv,Update_priv,Delete_priv,Create_priv,Drop_priv,Grant_priv,References_priv,Index_priv,Alter_priv,Create_tmp_table_priv,Lock_tables_priv,Create_view_priv,Show_view_priv,Create_routine_priv,Alter_routine_priv,Execute_priv,Event_priv,Trigger_priv from mysql.db;")["DATA"]
		inspection_info["DATA"]["INFORMATION_SCHEMA"]["innodb_trx"] = get_info("select trx_id,trx_state,trx_started,trx_requested_lock_id,trx_wait_started,trx_weight,trx_mysql_thread_id,trx_query,trx_operation_state,trx_tables_in_use,trx_tables_locked,trx_lock_structs,trx_lock_memory_bytes,trx_rows_locked,trx_rows_modified,trx_concurrency_tickets,trx_isolation_level,trx_unique_checks,trx_foreign_key_checks,trx_last_foreign_key_error,trx_adaptive_hash_latched,trx_adaptive_hash_timeout,trx_is_read_only,trx_autocommit_non_locking from information_schema.INNODB_TRX;")["DATA"] #innodb事务表
		inspection_info["DATA"]["INFORMATION_SCHEMA"]["processlist"] = get_info("select ID,USER,HOST,DB,COMMAND,TIME,STATE,INFO from information_schema.PROCESSLIST;")["DATA"]
		inspection_info["DATA"]["INFORMATION_SCHEMA"]["plugins"] = get_info("select PLUGIN_NAME,PLUGIN_VERSION,PLUGIN_STATUS,PLUGIN_TYPE,PLUGIN_TYPE_VERSION,PLUGIN_LIBRARY,PLUGIN_LIBRARY_VERSION,PLUGIN_AUTHOR,PLUGIN_DESCRIPTION,PLUGIN_LICENSE,LOAD_OPTION from information_schema.plugins;")["DATA"]
	

	#收集数据库信息 MYSQL库下的信息
	if inspection_info["DATA"]["MYSQL"]["HAVE_DATA"]:
		inspection_info["DATA"]["MYSQL"]["users"] = get_info("select Host,User,Select_priv,Insert_priv,Update_priv,Delete_priv,Create_priv,Drop_priv,Reload_priv,Shutdown_priv,Process_priv,File_priv,Grant_priv,References_priv,Index_priv,Alter_priv,Show_db_priv,Super_priv,Create_tmp_table_priv,Lock_tables_priv,Execute_priv,Repl_slave_priv,Repl_client_priv,Create_view_priv,Show_view_priv,Create_routine_priv,Alter_routine_priv,Create_user_priv,Event_priv,Trigger_priv,Create_tablespace_priv,ssl_type,ssl_cipher,x509_issuer,x509_subject,max_questions,max_updates,max_connections,max_user_connections,plugin,authentication_string,password_expired,password_last_changed,password_lifetime,account_locked from mysql.user;")["DATA"] #用户权限表
		inspection_info["DATA"]["MYSQL"]["slave_master_info"] = get_info("select Number_of_lines,Master_log_name,Master_log_pos,Host,User_name,Port,Connect_retry,Enabled_ssl,Heartbeat,Retry_count from mysql.slave_master_info;")["DATA"]
		inspection_info["DATA"]["MYSQL"]["slave_relay_log_info"] = get_info("select Number_of_lines,Relay_log_name,Relay_log_pos,Master_log_name,Master_log_pos,Sql_delay,Number_of_workers,Id,Channel_name from mysql.slave_relay_log_info;")["DATA"]
		inspection_info["DATA"]["MYSQL"]["slave_worker_info"] = get_info("select Id,Relay_log_name,Relay_log_pos,Master_log_name,Master_log_pos,Channel_name from mysql.slave_worker_info;")["DATA"]
		inspection_info["DATA"]["MYSQL"]["innodb_table_stats"] = get_info("select database_name,table_name,last_update,n_rows,clustered_index_size,sum_of_other_index_sizes from mysql.innodb_table_stats where database_name not in ('sys','mysql','information_schema','performance_schema');")["DATA"] #表统计信息
		inspection_info["DATA"]["MYSQL"]["innodb_index_stats"] = get_info("select database_name,table_name,index_name,last_update,stat_name,stat_value,sample_size,stat_description from mysql.innodb_index_stats where database_name not in ('sys','mysql','information_schema','performance_schema');")["DATA"] #索引统计信息
	

	#收集performance_schema库下的信息
	if inspection_info["DATA"]["PERFORMANCE_SCHEMA"]["HAVE_DATA"]:
		inspection_info["DATA"]["PERFORMANCE_SCHEMA"]["threads"] = get_info("select THREAD_ID,NAME,TYPE,PROCESSLIST_ID,PROCESSLIST_USER,PROCESSLIST_HOST,PROCESSLIST_DB,PROCESSLIST_COMMAND,PROCESSLIST_TIME,PROCESSLIST_STATE,PROCESSLIST_INFO,PARENT_THREAD_ID,ROLE,INSTRUMENTED,HISTORY,CONNECTION_TYPE,THREAD_OS_ID from performance_schema.threads;")["DATA"]
		inspection_info["DATA"]["PERFORMANCE_SCHEMA"]["accounts"] = get_info("select USER, HOST, CURRENT_CONNECTIONS, TOTAL_CONNECTIONS from performance_schema.accounts;")["DATA"]
		inspection_info["DATA"]["PERFORMANCE_SCHEMA"]["file_instances"] = get_info("select FILE_NAME,EVENT_NAME,OPEN_COUNT from performance_schema.file_instances;")["DATA"]
		#inspection_info["DATA"]["PERFORMANCE_SCHEMA"]["mutex_instances"] = get_info("select NAME,OBJECT_INSTANCE_BEGIN,LOCKED_BY_THREAD_ID from performance_schema.mutex_instances;")["DATA"] #没用
		#inspection_info["DATA"]["PERFORMANCE_SCHEMA"]["rwlock_instances"] = get_info("select NAME,OBJECT_INSTANCE_BEGIN,WRITE_LOCKED_BY_THREAD_ID,READ_LOCKED_BY_COUNT from performance_schema.rwlock_instances;")["DATA"] #没用
		inspection_info["DATA"]["PERFORMANCE_SCHEMA"]["socket_instances"] = get_info("select EVENT_NAME,OBJECT_INSTANCE_BEGIN,THREAD_ID,SOCKET_ID,IP,PORT,STATE from performance_schema.socket_instances;")["DATA"]
		inspection_info["DATA"]["PERFORMANCE_SCHEMA"]["events_statements_history"] = get_info("select THREAD_ID,EVENT_ID,END_EVENT_ID,EVENT_NAME,SOURCE,TIMER_START,TIMER_END,TIMER_WAIT,LOCK_TIME,SQL_TEXT,DIGEST,DIGEST_TEXT,CURRENT_SCHEMA,OBJECT_TYPE,OBJECT_SCHEMA,OBJECT_NAME,OBJECT_INSTANCE_BEGIN,MYSQL_ERRNO,RETURNED_SQLSTATE,MESSAGE_TEXT,ERRORS,WARNINGS,ROWS_AFFECTED,ROWS_SENT,ROWS_EXAMINED,CREATED_TMP_DISK_TABLES,CREATED_TMP_TABLES,SELECT_FULL_JOIN,SELECT_FULL_RANGE_JOIN,SELECT_RANGE,SELECT_RANGE_CHECK,SELECT_SCAN,SORT_MERGE_PASSES,SORT_RANGE,SORT_ROWS,SORT_SCAN,NO_INDEX_USED,NO_GOOD_INDEX_USED,NESTING_EVENT_ID,NESTING_EVENT_TYPE,NESTING_EVENT_LEVEL from performance_schema.events_statements_history order by LOCK_TIME desc limit 50;")["DATA"]
		inspection_info["DATA"]["PERFORMANCE_SCHEMA"]["metadata_locks"] = get_info("select OBJECT_TYPE,OBJECT_SCHEMA,OBJECT_NAME,OBJECT_INSTANCE_BEGIN,LOCK_TYPE,LOCK_DURATION,LOCK_STATUS,SOURCE,OWNER_THREAD_ID,OWNER_EVENT_ID from performance_schema.metadata_locks where OBJECT_TYPE='TABLE' order by OWNER_THREAD_ID asc limit 50;")["DATA"] #最新的元数据锁, 意义不大.....
		inspection_info["DATA"]["PERFORMANCE_SCHEMA"]["table_handles"] = get_info("select OBJECT_SCHEMA,OBJECT_NAME,count(*)  from performance_schema.table_handles where OBJECT_TYPE='TABLE' group by OBJECT_SCHEMA,OBJECT_NAME order  by 3 desc limit 50;")["DATA"] #打开次数前50的表

		inspection_info["DATA"]["PERFORMANCE_SCHEMA"]["events_waits_summary_by_account_by_event_name"] = get_info("select USER,HOST,EVENT_NAME,COUNT_STAR,SUM_TIMER_WAIT,MIN_TIMER_WAIT,AVG_TIMER_WAIT,MAX_TIMER_WAIT from performance_schema.events_waits_summary_by_account_by_event_name order by COUNT_STAR desc limit 50;")["DATA"] 
		inspection_info["DATA"]["PERFORMANCE_SCHEMA"]["events_waits_summary_by_thread_by_event_name"] = get_info("select THREAD_ID,EVENT_NAME,COUNT_STAR,SUM_TIMER_WAIT,MIN_TIMER_WAIT,AVG_TIMER_WAIT,MAX_TIMER_WAIT from performance_schema.events_waits_summary_by_thread_by_event_name order by COUNT_STAR desc limit 50;")["DATA"] #top50等待事事件
		inspection_info["DATA"]["PERFORMANCE_SCHEMA"]["events_waits_summary_global_by_event_name"] = get_info("select EVENT_NAME,COUNT_STAR,SUM_TIMER_WAIT,MIN_TIMER_WAIT,AVG_TIMER_WAIT,MAX_TIMER_WAIT from performance_schema.events_waits_summary_global_by_event_name lobal_by_event_name order by COUNT_STAR desc limit 50;")["DATA"] #top50 等待事件(event)
		inspection_info["DATA"]["PERFORMANCE_SCHEMA"]["events_statements_summary_by_account_by_event_name"] = get_info("select USER,HOST,EVENT_NAME,COUNT_STAR,SUM_TIMER_WAIT,MIN_TIMER_WAIT,AVG_TIMER_WAIT,MAX_TIMER_WAIT,SUM_LOCK_TIME,SUM_ERRORS,SUM_WARNINGS,SUM_ROWS_AFFECTED,SUM_ROWS_SENT,SUM_ROWS_EXAMINED,SUM_CREATED_TMP_DISK_TABLES,SUM_CREATED_TMP_TABLES,SUM_SELECT_FULL_JOIN,SUM_SELECT_FULL_RANGE_JOIN,SUM_SELECT_RANGE,SUM_SELECT_RANGE_CHECK,SUM_SELECT_SCAN,SUM_SORT_MERGE_PASSES,SUM_SORT_RANGE,SUM_SORT_ROWS,SUM_SORT_SCAN,SUM_NO_INDEX_USED,SUM_NO_GOOD_INDEX_USED from performance_schema.events_statements_summary_by_account_by_event_name order by COUNT_STAR desc  limit 50;")["DATA"]#top50 事件(event)
		inspection_info["DATA"]["PERFORMANCE_SCHEMA"]["objects_summary_global_by_type"] = get_info("select OBJECT_TYPE,OBJECT_SCHEMA,OBJECT_NAME,COUNT_STAR,SUM_TIMER_WAIT,MIN_TIMER_WAIT,AVG_TIMER_WAIT,MAX_TIMER_WAIT from performance_schema.objects_summary_global_by_type order by COUNT_STAR desc limit 50;")["DATA"] #top 50对象
		inspection_info["DATA"]["PERFORMANCE_SCHEMA"]["file_summary_by_event_name"] = get_info("select EVENT_NAME,COUNT_STAR,SUM_TIMER_WAIT,MIN_TIMER_WAIT,AVG_TIMER_WAIT,MAX_TIMER_WAIT,COUNT_READ,SUM_TIMER_READ,MIN_TIMER_READ,AVG_TIMER_READ,MAX_TIMER_READ,SUM_NUMBER_OF_BYTES_READ,COUNT_WRITE,SUM_TIMER_WRITE,MIN_TIMER_WRITE,AVG_TIMER_WRITE,MAX_TIMER_WRITE,SUM_NUMBER_OF_BYTES_WRITE,COUNT_MISC,SUM_TIMER_MISC,MIN_TIMER_MISC,AVG_TIMER_MISC,MAX_TIMER_MISC from performance_schema.file_summary_by_event_name order by COUNT_STAR desc limit 50;")["DATA"] #top50 file
		inspection_info["DATA"]["PERFORMANCE_SCHEMA"]["events_statements_summary_by_digest"] = get_info("select SCHEMA_NAME,DIGEST,DIGEST_TEXT,COUNT_STAR,SUM_TIMER_WAIT,MIN_TIMER_WAIT,AVG_TIMER_WAIT,MAX_TIMER_WAIT,SUM_LOCK_TIME,SUM_ERRORS,SUM_WARNINGS,SUM_ROWS_AFFECTED,SUM_ROWS_SENT,SUM_ROWS_EXAMINED,SUM_CREATED_TMP_DISK_TABLES,SUM_CREATED_TMP_TABLES,SUM_SELECT_FULL_JOIN,SUM_SELECT_FULL_RANGE_JOIN,SUM_SELECT_RANGE,SUM_SELECT_RANGE_CHECK,SUM_SELECT_SCAN,SUM_SORT_MERGE_PASSES,SUM_SORT_RANGE,SUM_SORT_ROWS,SUM_SORT_SCAN,SUM_NO_INDEX_USED,SUM_NO_GOOD_INDEX_USED,FIRST_SEEN,LAST_SEEN from performance_schema.events_statements_summary_by_digest order by COUNT_STAR desc limit 50;")["DATA"] #top50 sql
		
		


	#收集数据库信息 SYS 库下的信息
	if inspection_info["DATA"]["SYS"]["HAVE_DATA"]:
		inspection_info["DATA"]["SYS"]["innodb_locks"] = get_info("select wait_started,wait_age,wait_age_secs,locked_table,locked_index,locked_type,waiting_trx_id,waiting_trx_started,waiting_trx_age,waiting_trx_rows_locked,waiting_trx_rows_modified,waiting_pid,waiting_query,waiting_lock_id,waiting_lock_mode,blocking_trx_id,blocking_pid,blocking_query,blocking_lock_id,blocking_lock_mode,blocking_trx_started,blocking_trx_age,blocking_trx_rows_locked,blocking_trx_rows_modified,sql_kill_blocking_query,sql_kill_blocking_connection from sys.innodb_lock_waits;")["DATA"]
		inspection_info["DATA"]["SYS"]["statement_analysis"] = get_info("select query,db,full_scan,exec_count,total_latency,max_latency,avg_latency,lock_latency,rows_sent,rows_sent_avg,digest from sys.statement_analysis;")["DATA"]
	

	#其它数据库信息采集
	inspection_info["DATA"]["version"] = get_info("select @@version;")["DATA"]
	inspection_info["DATA"]["slave_status"] = get_info("show slave status;")["DATA"]
	inspection_info["DATA"]["status"] = get_info("show global status;")["DATA"]
	status_dict = {k:v for k,v in inspection_info["DATA"]["status"]}  #转化为字典
	inspection_info["DATA"]["variables"] = get_info("show global variables;")["DATA"]
	variables_dict = {k:v for k,v in inspection_info["DATA"]["variables"]}
	inspection_info["DATA"]["engine_innodb_status"] = get_info("SHOW ENGINE INNODB STATUS;")["DATA"]
	inspection_info["DATA"]["binlog"] = get_info("SHOW BINARY LOGS;")["DATA"]

	#TPS QPS
	TIME_INTERNAL = 1  #采样间隔
	qps_begin = get_info("show global status like 'Questions';")["DATA"]
	tps_begin_commit = get_info("show global status like 'Com_commit';")["DATA"]
	tps_begin_rollback = get_info("show global status like 'Com_rollback';")["DATA"]
	time.sleep(TIME_INTERNAL)
	qps_end = get_info("show global status like 'Questions';")["DATA"]
	tps_end_commit = get_info("show global status like 'Com_commit';")["DATA"]
	tps_end_rollback = get_info("show global status like 'Com_rollback';")["DATA"]
	QPS = (int(qps_end[0][1]) - int(qps_begin[0][1]))/TIME_INTERNAL
	TPS = ((int(tps_end_commit[0][1]) + int(tps_end_rollback[0][1])) - (int(tps_begin_commit[0][1]) - int(tps_begin_rollback[0][1]))) / TIME_INTERNAL
	inspection_info["DATA"]["QPS"] = QPS
	inspection_info["DATA"]["TPS"] = TPS
	

	#print(inspection_info["DATA"]["QPS"])


	#主机信息采集
	if inspection_info["HOST_INFO"]["HAVE_DATA"]:
		hostinfo = {}
		hostinfo["HAVE_DATA"] = True
		hostinfo["OS_TYPE"] = get_comm_info("cat /proc/sys/kernel/ostype")["DATA"]
		hostinfo["OS_LIKE"] = get_comm_info("""grep '^ID_LIKE=' /etc/os-release  | awk -F =  '{print $2}' | sed 's/\"//g' | awk '{print $1}'""")["DATA"]
		hostinfo["OS_NAME"] = get_comm_info("""grep "^NAME=" /etc/os-release  | awk -F = '{print $2}' | sed 's/\"//g'""")["DATA"]
		hostinfo["PLATFORM"] = get_comm_info("uname -m")["DATA"]
		hostinfo["KERNEL_VERSION"] = get_comm_info("uname -r")["DATA"]

		cpu_sock = int(get_comm_info("/usr/bin/lscpu  | /usr/bin/grep 'Socket(s)' | /usr/bin/awk '{print $NF}'")["DATA"])
		cpu_core = int(get_comm_info("/usr/bin/lscpu  | /usr/bin/grep 'Core(s)' | /usr/bin/awk '{print $NF}'")["DATA"])
		cpu_thread = int(get_comm_info("/usr/bin/lscpu  | /usr/bin/grep 'Thread(s)' | /usr/bin/awk '{print $NF}'")["DATA"])
		cpu_count = cpu_sock * cpu_core * cpu_thread
		hostinfo["CPU_SOCK"] = cpu_sock
		hostinfo["CPU_CORE"] = cpu_core
		hostinfo["CPU_THREAD"] = cpu_thread
		uptime_res = get_comm_info("/usr/bin/cat /proc/uptime")["DATA"]
		uptime = round(float(uptime_res.split()[0])/60/60/24,2) #开机时间 单位天
		cpu_b = get_comm_info("/usr/bin/head -1 /proc/stat | /usr/bin/awk '{print $2+$3+$4+$5+$6+$7+$8+$9+$(10),$5}'")["DATA"]
		time.sleep(0.1)
		cpu_e = get_comm_info("/usr/bin/head -1 /proc/stat | /usr/bin/awk '{print $2+$3+$4+$5+$6+$7+$8+$9+$(10),$5}'")["DATA"]
		cpu_total = int(cpu_e.split()[0]) - int(cpu_b.split()[0])
		cpu_idle = int(cpu_e.split()[1]) - int(cpu_b.split()[1])
		cpu_p = (cpu_total - cpu_idle ) / cpu_total #cpu当前使用率  总为1
		cpu_p100 = round((cpu_total - cpu_idle ) / cpu_total * 100,3)  #CPU当前使用百分比
		cpu_p_total = round((float(uptime_res.split()[0]) * cpu_count  - float(uptime_res.split()[1]))/float(uptime_res.split()[0])*100*cpu_count,3)#cpu开机到现在的使用百分比
		hostinfo["CPU_USAGE_100"] = cpu_p100 #CPU使用百分比
		hostinfo["CPU_USAGE_100_TOTAL"] = cpu_p_total  #cpu使用百分比(从开机到现在.)
		hostinfo["DF_HT"] = get_comm_info("df -PT | tail -n +2")["DATA"]
		hostinfo["MEM_TOTAL"] = get_comm_info("/usr/bin/grep MemTotal /proc/meminfo | /usr/bin/awk '{print $2}'")["DATA"]
		hostinfo["MEM_ALI"] = get_comm_info("/usr/bin/grep MemAvailable /proc/meminfo | /usr/bin/awk '{print $2}'")["DATA"]
		hostinfo["LOAD_AVG"] = get_comm_info("/usr/bin/awk '{print $1,$2,$3}' /proc/loadavg")["DATA"]
		hostinfo["TCP4_SOCKET"] = get_comm_info("/usr/bin/wc -l /proc/net/tcp | /usr/bin/awk '{print $1-1}'")["DATA"]
		hostinfo["HOSTNAME"] = get_comm_info("/usr/bin/cat /proc/sys/kernel/hostname")["DATA"]
		hostinfo["SWAP_TOTAL"] = get_comm_info("/usr/bin/grep SwapTotal /proc/meminfo | /usr/bin/awk '{print $2}'")["DATA"]
		hostinfo["SWAPPINESS"] = get_comm_info("/usr/bin/cat /proc/sys/vm/swappiness")["DATA"]
		hostinfo["TIME_ZONE"] = get_comm_info("ls -l /etc/localtime | awk -F /zoneinfo/ '{print $NF}'")["DATA"]
		hostinfo["DMESG"] = get_comm_info("tail -200 /var/log/dmesg")["DATA"]

		#磁盘类型
		hostinfo["DISK_TYPE"] = get_comm_info("lsblk -d -o NAME,rota | tail -n +2")["DATA"]

		#取数据库目录, 日志(error log之类的)
		hostinfo["DBINFO"] = {}
		hostinfo["DBINFO"]["tmpdir"] = get_comm_info("df -PT {dir} | tail -n +2".format(dir=variables_dict["tmpdir"]))["DATA"]
		hostinfo["DBINFO"]["datadir"] = get_comm_info("df -PT {dir} | tail -n +2".format(dir=variables_dict["datadir"]))["DATA"]
		hostinfo["DBINFO"]["innodb_data_home_dir"] = get_comm_info("df -PT {dir} | tail -n +2".format(dir=variables_dict["innodb_data_home_dir"]))["DATA"]
		hostinfo["DBINFO"]["innodb_log_group_home_dir"] = get_comm_info("df -PT {dir} | tail -n +2".format(dir=variables_dict["innodb_log_group_home_dir"]))["DATA"]
		hostinfo["DBINFO"]["log_bin_index"] = get_comm_info("df -PT {dir} | tail -n +2".format(dir=variables_dict["log_bin_index"]))["DATA"]
		hostinfo["DBINFO"]["relay_log_dir"] = get_comm_info("df -PT {dir} | tail -n +2".format(dir=variables_dict["relay_log_index"]))["DATA"]
		hostinfo["DBINFO"]["log_error"] =  get_comm_info("tail -100 {dir}".format(dir=variables_dict["log_error"]))["DATA"]

		#慢日志(如果有pt-query-digest, 就直接分析, 没得就tail200行, 交给分析脚本来整...)
		hostinfo["DBINFO"]["slow_log"] = {}
		hostinfo["DBINFO"]["slow_log"]["TYPE"] = ""
		if  get_comm_info("which pt-query-digest")["CODE"] == 0:
			hostinfo["DBINFO"]["slow_log"]["TYPE"] = "pt-query-digest"
			hostinfo["DBINFO"]["slow_log"]["DATA"] = get_comm_info("pt-query-digest {slow_log} --output json ".format(slow_log=variables_dict["slow_query_log_file"]))["DATA"]
		else:
			hostinfo["DBINFO"]["slow_log"]["TYPE"] = "text"
			hostinfo["DBINFO"]["slow_log"]["DATA"] =  get_comm_info("tail -{rows} {dir}".format(rows=SLOW_LOG_ROWS, dir=variables_dict["slow_query_log_file"]))["DATA"]
		

		inspection_info["HOST_INFO"] = hostinfo
		#print(inspection_info["HOST_INFO"]["DBINFO"])


	#数据采集完成后, 保存采集信息
	if NO_FILE:
		print("")
		if inspection_info["HOST_INFO"]["HAVE_DATA"]:
			print("数据库目录:",inspection_info["HOST_INFO"]["DBINFO"]["datadir"])
			print("tmp目录:",inspection_info["HOST_INFO"]["DBINFO"]["tmpdir"])
			print("innodb目录:",inspection_info["HOST_INFO"]["DBINFO"]["innodb_data_home_dir"])
		print("数据库数量: ",len(inspection_info["DATA"]["INFORMATION_SCHEMA"]["schemata"]))
		print("表数量: ",len(inspection_info["DATA"]["INFORMATION_SCHEMA"]["tables"]))
		data_length=0
		index_length=0
		for k in inspection_info["DATA"]["INFORMATION_SCHEMA"]["tables"]:
			data_length += k[9]
			index_length += k[11]
		print("数据大小: {datasize} MB    索引大小: {indexsize} MB".format(datasize=round(data_length/1024/1024,2), indexsize=round(index_length/1024/1024,2)))
		print("数据库版本:", inspection_info["DATA"]["version"][0][0])
		print("innodb_buffer_pool_size {innodb_buffer_pool_size} MB".format(innodb_buffer_pool_size=round(int(variables_dict["innodb_buffer_pool_size"])/1024/1024,2)))
		print("binlog格式:",variables_dict["binlog_format"])
		print("sync_binlog:",variables_dict["sync_binlog"])
		print("innodb_flush_log_at_trx_commit:",variables_dict["innodb_flush_log_at_trx_commit"])
		print("事务隔离级别:",variables_dict["transaction_isolation"])
		print("Slave_IO_Running:{Slave_IO_Running}  Slave_SQL_Running:{Slave_SQL_Running}  Master_Bind:{Master_Bind}".format(Slave_IO_Running=inspection_info["DATA"]["slave_status"][0][10], Slave_SQL_Running=inspection_info["DATA"]["slave_status"][0][11], Master_Bind=inspection_info["DATA"]["slave_status"][0][46]))
		print("")

	else:
		#把json数据类型全部转化为str
		class MyJsonEncoder(json.JSONEncoder):
			def default(self,obj):
				return str(obj)
		inspection_info = json.dumps(inspection_info, cls=MyJsonEncoder) 
		with open(SAVED_FILE,"w") as f:
			json.dump(inspection_info,f)
			print("数据基础信息已采集完成. 保存在 {SAVED_FILE} 可以执行如下命令,生成巡检报告\n xunjian_analyze {SAVED_FILE} ".format(SAVED_FILE=SAVED_FILE))


	#结束了 要关闭conn和ssh
	if CAN_SSH:
		ssh.close()
	cursor.close()
	conn.close()


def _argparse():
	#parser = argparse.ArgumentParser()
	#parser.add_argument('--help', '-h',  action='help',  help='显示帮助信息')
	parser = argparse.ArgumentParser(description='MYSQL 信息收集脚本. 最新版下载地址: visit https://github.com/ddcw/inspection ')
	parser.add_argument('--host', '-H',  action='store', dest='HOST', default="localhost", help='MYSQL服务器地址(默认localhost)')
	parser.add_argument('--port', '-P' ,  action='store', dest='PORT',type=int, default=3306, help='MYSQL服务器端口')
	parser.add_argument('--user', '-u' ,  action='store', dest='USER',  help='MYSQL用户')
	parser.add_argument('--password', '-p' ,  action='store', dest='PASSWORD',   help='MYSQL用户的密码')
	parser.add_argument('--socket', '-S' ,  action='store', dest='SOCKET',   help='mysql unix socket')
	parser.add_argument('--ssh-port', '-sP' ,  action='store', dest='SSH_PORT', default=22, type=int , help='MYSQL服务器主机的SSH端口(默认22)')
	parser.add_argument('--ssh-user', '-su' ,  action='store', dest='SSH_USER',  help='MYSQL服务器主机的SSH用户')
	parser.add_argument('--ssh-password', '-sp' ,  action='store', dest='SSH_PASSWORD',   help='MYSQL服务器主机的SSH用户的密码')
	parser.add_argument('--ssh-pkey', '-spk' ,  action='store', dest='SSH_PKEY',   help='MYSQL服务器主机的SSH用户的私钥(仅支持RSA)')
	parser.add_argument('--no-host', '-nh' ,  action='store_true', dest='NO_HOST',   help='不采集主机信息...')
	parser.add_argument('--file', '-f' ,  action='store', dest='SAVED_FILE',   help='信息采集之后保存的文件名字(仅支持JSON格式)')
	parser.add_argument('--no-file', '-n', '--print',  action='store_true', dest="NO_FILE",   help='不保存为文件, 只是print一些简单信息')
	parser.add_argument('--slow-log-rows', action='store', dest="SLOW_LOG_ROWS", default=500, type=int, help='采集慢日志的行数(当数据库服务器没得慢日志分析工具的时候), 默认500')
	parser.add_argument('--author',  action='store', dest="AUTHOR", default="ddcw",   help='记录这个脚本是谁执行的,不影响脚本使用(默认为ddcw)')
	parser.add_argument('--version', '-v', '-V', action='store_true', dest="version",  help='打印版本信息')
	return parser.parse_args()



if __name__ == '__main__':
	parser = _argparse()
	if parser.version :
		print("Version: {VERSION}".format(VERSION=VERSION))
	else:
		main(	HOST = parser.HOST,
			PORT = parser.PORT,
			USER = parser.USER,
			PASSWORD = parser.PASSWORD,
			SOCKET = parser.SOCKET,
			SSH_PORT = parser.SSH_PORT,
			SSH_USER = parser.SSH_USER,
			SSH_PASSWORD = parser.SSH_PASSWORD,
			SSH_PKEY = parser.SSH_PKEY,
			NO_HOST = parser.NO_HOST,
			SAVED_FILE = parser.SAVED_FILE,
			NO_FILE = parser.NO_FILE,
			AUTHOR = parser.AUTHOR,
			SLOW_LOG_ROWS = parser.SLOW_LOG_ROWS,
			)

