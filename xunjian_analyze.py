import json
import argparse
import pandas as pd
import datetime
from jinja2 import FileSystemLoader,Environment
import matplotlib.pyplot as plt
import base64
import io
import os
import sys
import subprocess
import tempfile

#版本定义
analyze_version="0.3"


def get_local_command_result(comm):
	timeout = 30 #超过30秒没有执行完,就kill了
	with subprocess.Popen(comm, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as f:
		try:
			return {"CODE":f.wait(timeout),"DATA":str(f.stdout.read().rstrip(),encoding="utf-8")}
		except:
			f.kill()
			return {"CODE":256, "DATA":"TIMEOUT ({timeout})".format(timeout=timeout)}

def main(FILE, OUT_FILE, TEMPLATE_FILE):
	try:
		with open(FILE,'r') as f :
			xunjian = json.load(f)
		xunjian_result = json.loads(xunjian)
	except Exception as e:
		print("文件格式不对.... 仅支持JSON格式")
		sys.exit(1)
	try:
		DBTYPE = xunjian_result["DBTYPE"]
		HOST = xunjian_result["HOST"]
		PORT = xunjian_result["PORT"]
		AUTHOR = xunjian_result["AUTHOR"]
		START_TIME = xunjian_result["START_TIME"]
		DATA = xunjian_result["DATA"]
		HOST_INFO = xunjian_result["HOST_INFO"]
		mysql_inspection_version = xunjian_result["VERSION"]
	except Exception as e:
		print(e)
		print("获取信息失败, 请查看版本是否匹配")
		sys.exit(1)

	if DBTYPE == "MYSQL":
		#INFORMATION_SCHEMA 库
		if DATA["INFORMATION_SCHEMA"]["HAVE_DATA"]:
			schemata = pd.DataFrame(DATA["INFORMATION_SCHEMA"]["schemata"], columns=['CATALOG_NAME', 'SCHEMA_NAME', 'DEFAULT_CHARACTER_SET_NAME', 'DEFAULT_COLLATION_NAME'])
			tables = pd.DataFrame(DATA["INFORMATION_SCHEMA"]["tables"], columns=['ABLE_CATALOG', 'TABLE_SCHEMA', 'TABLE_NAME', 'TABLE_TYPE', 'ENGINE', 'VERSION', 'ROW_FORMAT', 'TABLE_ROWS', 'AVG_ROW_LENGTH', 'DATA_LENGTH', 'MAX_DATA_LENGTH', 'INDEX_LENGTH', 'DATA_FREE', 'AUTO_INCREMENT', 'CREATE_TIME', 'UPDATE_TIME', 'CHECK_TIME', 'TABLE_COLLATION', 'CHECKSUM', 'CREATE_OPTIONS', 'TABLE_COMMENT'])
			cols = pd.DataFrame(DATA["INFORMATION_SCHEMA"]["columns"], columns=['TABLE_CATALOG', 'TABLE_SCHEMA', 'TABLE_NAME', 'COLUMN_NAME', 'ORDINAL_POSITION', 'COLUMN_DEFAULT', 'IS_NULLABLE', 'DATA_TYPE', 'CHARACTER_MAXIMUM_LENGTH', 'CHARACTER_OCTET_LENGTH', 'NUMERIC_PRECISION', 'NUMERIC_SCALE', 'DATETIME_PRECISION', 'CHARACTER_SET_NAME', 'COLLATION_NAME', 'COLUMN_TYPE', 'COLUMN_KEY', 'EXTRA', 'PRIVILEGES', 'COLUMN_COMMENT', 'GENERATION_EXPRESSION'])
			statistics = pd.DataFrame(DATA["INFORMATION_SCHEMA"]["statistics"], columns=['TABLE_CATALOG', 'TABLE_SCHEMA', 'TABLE_NAME', 'NON_UNIQUE', 'INDEX_SCHEMA', 'INDEX_NAME', 'SEQ_IN_INDEX', 'COLUMN_NAME', 'COLLATION', 'CARDINALITY', 'SUB_PART', 'PACKED', 'NULLABLE', 'INDEX_TYPE', 'COMMENT', 'INDEX_COMMENT'])
			user_pri = pd.DataFrame(DATA["INFORMATION_SCHEMA"]["user_pri"], columns=['GRANTEE', 'TABLE_CATALOG', 'PRIVILEGE_TYPE', 'IS_GRANTABLE'])
			db_pri = pd.DataFrame(DATA["INFORMATION_SCHEMA"]["db_pri"], columns=['Host', 'Db', 'User', 'Select_priv', 'Insert_priv', 'Update_priv', 'Delete_priv', 'Create_priv', 'Drop_priv', 'Grant_priv', 'References_priv', 'Index_priv', 'Alter_priv', 'Create_tmp_table_priv', 'Lock_tables_priv', 'Create_view_priv', 'Show_view_priv', 'Create_routine_priv', 'Alter_routine_priv', 'Execute_priv', 'Event_priv', 'Trigger_priv'])
			innodb_trx = pd.DataFrame(DATA["INFORMATION_SCHEMA"]["innodb_trx"], columns=['trx_id', 'trx_state', 'trx_started', 'trx_requested_lock_id', 'trx_wait_started', 'trx_weight', 'trx_mysql_thread_id', 'trx_query', 'trx_operation_state', 'trx_tables_in_use', 'trx_tables_locked', 'trx_lock_structs', 'trx_lock_memory_bytes', 'trx_rows_locked', 'trx_rows_modified', 'trx_concurrency_tickets', 'trx_isolation_level', 'trx_unique_checks', 'trx_foreign_key_checks', 'trx_last_foreign_key_error', 'trx_adaptive_hash_latched', 'trx_adaptive_hash_timeout', 'trx_is_read_only', 'trx_autocommit_non_locking'])
			processlist = pd.DataFrame(DATA["INFORMATION_SCHEMA"]["processlist"], columns=['ID', 'USER', 'HOST', 'DB', 'COMMAND', 'TIME', 'STATE', 'INFO'])
			plugins = pd.DataFrame(DATA["INFORMATION_SCHEMA"]["plugins"], columns=['PLUGIN_NAME', 'PLUGIN_VERSION', 'PLUGIN_STATUS', 'PLUGIN_TYPE', 'PLUGIN_TYPE_VERSION', 'PLUGIN_LIBRARY', 'PLUGIN_LIBRARY_VERSION', 'PLUGIN_AUTHOR', 'PLUGIN_DESCRIPTION', 'PLUGIN_LICENSE', 'LOAD_OPTION'])


		#MYSQL 库
		if DATA["MYSQL"]["HAVE_DATA"]:
			users = pd.DataFrame(DATA["MYSQL"]["users"], columns=['Host', 'User', 'Select_priv', 'Insert_priv', 'Update_priv', 'Delete_priv', 'Create_priv', 'Drop_priv', 'Reload_priv', 'Shutdown_priv', 'Process_priv', 'File_priv', 'Grant_priv', 'References_priv', 'Index_priv', 'Alter_priv', 'Show_db_priv', 'Super_priv', 'Create_tmp_table_priv', 'Lock_tables_priv', 'Execute_priv', 'Repl_slave_priv', 'Repl_client_priv', 'Create_view_priv', 'Show_view_priv', 'Create_routine_priv', 'Alter_routine_priv', 'Create_user_priv', 'Event_priv', 'Trigger_priv', 'Create_tablespace_priv', 'ssl_type', 'ssl_cipher', 'x509_issuer', 'x509_subject', 'max_questions', 'max_updates', 'max_connections', 'max_user_connections', 'plugin', 'authentication_string', 'password_expired', 'password_last_changed', 'password_lifetime', 'account_locked'])
			slave_master_info = pd.DataFrame(DATA["MYSQL"]["slave_master_info"], columns=['Number_of_lines', 'Master_log_name', 'Master_log_pos', 'Host', 'User_name', 'Port', 'Connect_retry', 'Enabled_ssl', 'Heartbeat', 'Retry_count'])
			slave_relay_log_info = pd.DataFrame(DATA["MYSQL"]["slave_relay_log_info"], columns=['Number_of_lines', 'Relay_log_name', 'Relay_log_pos', 'Master_log_name', 'Master_log_pos', 'Sql_delay', 'Number_of_workers', 'Id', 'Channel_name'])
			slave_worker_info =  pd.DataFrame(DATA["MYSQL"]["slave_worker_info"], columns=['Id', 'Relay_log_name', 'Relay_log_pos', 'Master_log_name', 'Master_log_pos', 'Channel_name'])
			innodb_table_stats = pd.DataFrame(DATA["MYSQL"]["innodb_table_stats"], columns=['database_name', 'table_name', 'last_update', 'n_rows', 'clustered_index_size', 'sum_of_other_index_sizes'])
			innodb_index_stats = pd.DataFrame(DATA["MYSQL"]["innodb_index_stats"], columns=['database_name', 'table_name', 'index_name', 'last_update', 'stat_name', 'stat_value', 'sample_size', 'stat_description'])




		#PERFORMANCE_SCHEMA 库
		if DATA["PERFORMANCE_SCHEMA"]["HAVE_DATA"]:
			threads = pd.DataFrame(DATA["PERFORMANCE_SCHEMA"]["threads"], columns=['THREAD_ID', 'NAME', 'TYPE', 'PROCESSLIST_ID', 'PROCESSLIST_USER', 'PROCESSLIST_HOST', 'PROCESSLIST_DB', 'PROCESSLIST_COMMAND', 'PROCESSLIST_TIME', 'PROCESSLIST_STATE', 'PROCESSLIST_INFO', 'PARENT_THREAD_ID', 'ROLE', 'INSTRUMENTED', 'HISTORY', 'CONNECTION_TYPE', 'THREAD_OS_ID'])
			accounts = pd.DataFrame(DATA["PERFORMANCE_SCHEMA"]["accounts"], columns=['USER', 'HOST', 'CURRENT_CONNECTIONS', 'TOTAL_CONNECTIONS'])
			file_instances = pd.DataFrame(DATA["PERFORMANCE_SCHEMA"]["file_instances"], columns=['FILE_NAME', 'EVENT_NAME', 'OPEN_COUNT'])
			socket_instances = pd.DataFrame(DATA["PERFORMANCE_SCHEMA"]["socket_instances"], columns=['EVENT_NAME', 'OBJECT_INSTANCE_BEGIN', 'THREAD_ID', 'SOCKET_ID', 'IP', 'PORT', 'STATE'])
			events_statements_history = pd.DataFrame(DATA["PERFORMANCE_SCHEMA"]["events_statements_history"], columns=['THREAD_ID', 'EVENT_ID', 'END_EVENT_ID', 'EVENT_NAME', 'SOURCE', 'TIMER_START', 'TIMER_END', 'TIMER_WAIT', 'LOCK_TIME', 'SQL_TEXT', 'DIGEST', 'DIGEST_TEXT', 'CURRENT_SCHEMA', 'OBJECT_TYPE', 'OBJECT_SCHEMA', 'OBJECT_NAME', 'OBJECT_INSTANCE_BEGIN', 'MYSQL_ERRNO', 'RETURNED_SQLSTATE', 'MESSAGE_TEXT', 'ERRORS', 'WARNINGS', 'ROWS_AFFECTED', 'ROWS_SENT', 'ROWS_EXAMINED', 'CREATED_TMP_DISK_TABLES', 'CREATED_TMP_TABLES', 'SELECT_FULL_JOIN', 'SELECT_FULL_RANGE_JOIN', 'SELECT_RANGE', 'SELECT_RANGE_CHECK', 'SELECT_SCAN', 'SORT_MERGE_PASSES', 'SORT_RANGE', 'SORT_ROWS', 'SORT_SCAN', 'NO_INDEX_USED', 'NO_GOOD_INDEX_USED', 'NESTING_EVENT_ID', 'NESTING_EVENT_TYPE', 'NESTING_EVENT_LEVEL'])
			metadata_locks = pd.DataFrame(DATA["PERFORMANCE_SCHEMA"]["metadata_locks"], columns=['OBJECT_TYPE', 'OBJECT_SCHEMA', 'OBJECT_NAME', 'OBJECT_INSTANCE_BEGIN', 'LOCK_TYPE', 'LOCK_DURATION', 'LOCK_STATUS', 'SOURCE', 'OWNER_THREAD_ID', 'OWNER_EVENT_ID'])
			table_handles = pd.DataFrame(DATA["PERFORMANCE_SCHEMA"]["table_handles"], columns=['OBJECT_SCHEMA','OBJECT_NAME','COUNT'])
			events_waits_summary_by_account_by_event_name = pd.DataFrame(DATA["PERFORMANCE_SCHEMA"]["events_waits_summary_by_account_by_event_name"], columns=['USER', 'HOST', 'EVENT_NAME', 'COUNT_STAR', 'SUM_TIMER_WAIT', 'MIN_TIMER_WAIT', 'AVG_TIMER_WAIT', 'MAX_TIMER_WAIT'])
			
			events_waits_summary_by_thread_by_event_name = pd.DataFrame(DATA["PERFORMANCE_SCHEMA"]["events_waits_summary_by_thread_by_event_name"], columns=['THREAD_ID', 'EVENT_NAME', 'COUNT_STAR', 'SUM_TIMER_WAIT', 'MIN_TIMER_WAIT', 'AVG_TIMER_WAIT', 'MAX_TIMER_WAIT'])
			events_waits_summary_global_by_event_name = pd.DataFrame(DATA["PERFORMANCE_SCHEMA"]["events_waits_summary_global_by_event_name"], columns=['EVENT_NAME', 'COUNT_STAR', 'SUM_TIMER_WAIT', 'MIN_TIMER_WAIT', 'AVG_TIMER_WAIT', 'MAX_TIMER_WAIT'])
			events_statements_summary_by_account_by_event_name = pd.DataFrame(DATA["PERFORMANCE_SCHEMA"]["events_statements_summary_by_account_by_event_name"], columns=['USER', 'HOST', 'EVENT_NAME', 'COUNT_STAR', 'SUM_TIMER_WAIT', 'MIN_TIMER_WAIT', 'AVG_TIMER_WAIT', 'MAX_TIMER_WAIT', 'SUM_LOCK_TIME', 'SUM_ERRORS', 'SUM_WARNINGS', 'SUM_ROWS_AFFECTED', 'SUM_ROWS_SENT', 'SUM_ROWS_EXAMINED', 'SUM_CREATED_TMP_DISK_TABLES', 'SUM_CREATED_TMP_TABLES', 'SUM_SELECT_FULL_JOIN', 'SUM_SELECT_FULL_RANGE_JOIN', 'SUM_SELECT_RANGE', 'SUM_SELECT_RANGE_CHECK', 'SUM_SELECT_SCAN', 'SUM_SORT_MERGE_PASSES', 'SUM_SORT_RANGE', 'SUM_SORT_ROWS', 'SUM_SORT_SCAN', 'SUM_NO_INDEX_USED', 'SUM_NO_GOOD_INDEX_USED']) #top20 事件(event)
			objects_summary_global_by_type = pd.DataFrame(DATA["PERFORMANCE_SCHEMA"]["objects_summary_global_by_type"], columns=['OBJECT_TYPE', 'OBJECT_SCHEMA', 'OBJECT_NAME', 'COUNT_STAR', 'SUM_TIMER_WAIT', 'MIN_TIMER_WAIT', 'AVG_TIMER_WAIT', 'MAX_TIMER_WAIT']) #top 50对象
			file_summary_by_event_name = pd.DataFrame(DATA["PERFORMANCE_SCHEMA"]["file_summary_by_event_name"], columns=['EVENT_NAME', 'COUNT_STAR', 'SUM_TIMER_WAIT', 'MIN_TIMER_WAIT', 'AVG_TIMER_WAIT', 'MAX_TIMER_WAIT', 'COUNT_READ', 'SUM_TIMER_READ', 'MIN_TIMER_READ', 'AVG_TIMER_READ', 'MAX_TIMER_READ', 'SUM_NUMBER_OF_BYTES_READ', 'COUNT_WRITE', 'SUM_TIMER_WRITE', 'MIN_TIMER_WRITE', 'AVG_TIMER_WRITE', 'MAX_TIMER_WRITE', 'SUM_NUMBER_OF_BYTES_WRITE', 'COUNT_MISC', 'SUM_TIMER_MISC', 'MIN_TIMER_MISC', 'AVG_TIMER_MISC', 'MAX_TIMER_MISC'])  #top50 file
			events_statements_summary_by_digest = pd.DataFrame(DATA["PERFORMANCE_SCHEMA"]["events_statements_summary_by_digest"], columns=['SCHEMA_NAME', 'DIGEST', 'DIGEST_TEXT', 'COUNT_STAR', 'SUM_TIMER_WAIT', 'MIN_TIMER_WAIT', 'AVG_TIMER_WAIT', 'MAX_TIMER_WAIT', 'SUM_LOCK_TIME', 'SUM_ERRORS', 'SUM_WARNINGS', 'SUM_ROWS_AFFECTED', 'SUM_ROWS_SENT', 'SUM_ROWS_EXAMINED', 'SUM_CREATED_TMP_DISK_TABLES', 'SUM_CREATED_TMP_TABLES', 'SUM_SELECT_FULL_JOIN', 'SUM_SELECT_FULL_RANGE_JOIN', 'SUM_SELECT_RANGE', 'SUM_SELECT_RANGE_CHECK', 'SUM_SELECT_SCAN', 'SUM_SORT_MERGE_PASSES', 'SUM_SORT_RANGE', 'SUM_SORT_ROWS', 'SUM_SORT_SCAN', 'SUM_NO_INDEX_USED', 'SUM_NO_GOOD_INDEX_USED', 'FIRST_SEEN', 'LAST_SEEN']) #top50 sql



		#SYS 库
		if DATA["SYS"]["HAVE_DATA"]:
			innodb_locks = pd.DataFrame(DATA["SYS"]["innodb_locks"], columns=['wait_started', 'wait_age', 'wait_age_secs', 'locked_table',  'locked_index', 'locked_type', 'waiting_trx_id', 'waiting_trx_started', 'waiting_trx_age', 'waiting_trx_rows_locked', 'waiting_trx_rows_modified', 'waiting_pid', 'waiting_query', 'waiting_lock_id', 'waiting_lock_mode', 'blocking_trx_id', 'blocking_pid', 'blocking_query', 'blocking_lock_id', 'blocking_lock_mode', 'blocking_trx_started', 'blocking_trx_age', 'blocking_trx_rows_locked', 'blocking_trx_rows_modified', 'sql_kill_blocking_query', 'sql_kill_blocking_connection'])
			statement_analysis = pd.DataFrame(DATA["SYS"]["statement_analysis"], columns=['query', 'db', 'full_scan', 'exec_count', 'total_latency', 'max_latency', 'avg_latency', 'lock_latency', 'rows_sent', 'rows_sent_avg', 'digest'])



		#其它信息
		version = DATA["version"]
		if version[0][0][0:1] == 8:
			binlog = pd.DataFrame(DATA["binlog"], columns=['Log_name','File_size','Encrypted'])
		elif version[0][0][0:1] == 5:
			binlog = pd.DataFrame(DATA["binlog"], columns=['Log_name','File_size'])
		else:
			binlog = "not support"
		slave_status = DATA["slave_status"]
		tps = DATA["TPS"]
		qps = DATA["QPS"]
		engine_innodb_status = DATA["engine_innodb_status"]
		status = pd.DataFrame(DATA["status"], columns=['key','value']).set_index('key')
		variables = pd.DataFrame(DATA["variables"], columns=['key','value']).set_index('key')



		#主机信息采集
		#HAVE_DATA = HOST_INFO["HAVE_DATA"]
		if HOST_INFO["HAVE_DATA"]:
			OS_TYPE = HOST_INFO["OS_TYPE"]
			OS_LIKE = HOST_INFO["OS_LIKE"]
			OS_NAME = HOST_INFO["OS_NAME"]
			PLATFORM = HOST_INFO["PLATFORM"]
			KERNEL_VERSION = HOST_INFO["KERNEL_VERSION"]
			CPU_USAGE_100 = HOST_INFO["CPU_USAGE_100"]  #CPU当前使用百分比
			CPU_USAGE_100_TOTAL = HOST_INFO["CPU_USAGE_100_TOTAL"] #CPU总使用百分比
			DF_HT = HOST_INFO["DF_HT"].split("\n") #不准备显示这个数据, 就不做转换了... (当前是一维数组)
			MEM_TOTAL = int(HOST_INFO["MEM_TOTAL"])
			MEM_ALI = int(HOST_INFO["MEM_ALI"])
			LOAD_AVG = HOST_INFO["LOAD_AVG"]
			TCP4_SOCKET = HOST_INFO["TCP4_SOCKET"]
			HOSTNAME = HOST_INFO["HOSTNAME"]
			SWAP_TOTAL = HOST_INFO["SWAP_TOTAL"]
			SWAPPINESS = HOST_INFO["SWAPPINESS"]
			TIME_ZONE = HOST_INFO["TIME_ZONE"]
			TOP500_DMESG = HOST_INFO["DMESG"]

			DATA_DIR = HOST_INFO["DBINFO"]["datadir"].split()
			LOGBIN_DIR = HOST_INFO["DBINFO"]["log_bin_index"].split()
			RELAY_DIR = HOST_INFO["DBINFO"]["relay_log_dir"].split()

			SLOW_LOG = HOST_INFO["DBINFO"]["slow_log"]
			ERROR_LOG = HOST_INFO["DBINFO"]["log_error"]

			DISK_TYPE = [] 
			for x in HOST_INFO["DISK_TYPE"].split("\n"):
				if x.split()[0] != "sr0":
					DISK_TYPE.append([x.split()[0],x.split()[1]])
			#DISK_TYPE = pd.DataFrame(DISK_TYPE, columns=['DISK', 'TYPE',])
		else:
			OS_TYPE = ""
			OS_LIKE =""
			OS_NAME=""
			PLATFORM =""
			KERNEL_VERSION =""
			CPU_USAGE_100 =""
			CPU_USAGE_100_TOTAL =""
			DF_HT =""
			MEM_TOTAL =2
			MEM_ALI =1
			LOAD_AVG=""
			TCP4_SOCKET=""
			HOSTNAME =""
			SWAP_TOTAL =""
			SWAPPINESS =""
			TIME_ZONE =""
			TOP500_DMESG =""

			DATA_DIR =""
			LOGBIN_DIR=""
			RELAY_DIR =""

			SLOW_LOG =""
			ERROR_LOG =""

			DISK_TYPE = []


		#一些汇总信息
		total_db_count = schemata.shape[0] #总数据库数量
		total_table_count = tables.shape[0] #数表数量
		total_size = int(tables["DATA_LENGTH"].sum(axis=0)) #总数据大小(不含索引)
		total_conn_count = processlist.shape[0] #总Processlist数
		total_thread_count = threads.shape[0] #总线程数量
		
		#当前库的从库信息
		processlist_slave = processlist.where(processlist['COMMAND']=="Binlog Dump")[["HOST"]].dropna().values
		if processlist_slave.shape[0] > 0:
			have_processlist_slave = True
		else:
			have_processlist_slave = False
		

		#重复索引
		re_index = statistics[statistics.duplicated(subset=['TABLE_SCHEMA','TABLE_NAME','COLUMN_NAME'],keep=False)]#重复索引 subset根据什么字段判断为重复索引
		repeat_index=re_index[['TABLE_SCHEMA','TABLE_NAME','INDEX_NAME','COLUMN_NAME']].sort_values(by=['TABLE_SCHEMA','TABLE_NAME','COLUMN_NAME'],ascending=False)

		#无主键的表
		primary_key_unique_key_table = cols[cols.COLUMN_KEY.isin(['PRI','UNI'])][['TABLE_SCHEMA','TABLE_NAME']]  #相当于 select TABLE_SCHEMA,TABLE_NAME from cols where COLUMN_KEY in (PRI,UNI)
		no_primary_key = pd.concat([tables[['TABLE_SCHEMA','TABLE_NAME']],primary_key_unique_key_table,primary_key_unique_key_table]).drop_duplicates(keep=False) #取并集,然后删除重复的所有行

		#没得索引的表, 也就是排除 PRI UNI  MUL
		have_index_table = cols[cols.COLUMN_KEY.isin(['PRI','UNI','MUL'])][['TABLE_SCHEMA','TABLE_NAME']]
		no_index = pd.concat([tables[['TABLE_SCHEMA','TABLE_NAME']],have_index_table,have_index_table]).drop_duplicates(keep=False)

		#索引数量超过5个的表
		over_5_index = statistics[statistics.duplicated(subset=['TABLE_SCHEMA','TABLE_NAME','INDEX_NAME'],keep=False)]  #去重
		over_5_index = over_5_index.groupby(['TABLE_SCHEMA','TABLE_NAME'], as_index=False)["INDEX_NAME"].count() #group by count
		over_5_index = over_5_index.where(over_5_index["INDEX_NAME"]>5) #where

		#非innodb表
		#print(tables[~tables.ENGINE.isin(['InnoDB'])][['TABLE_SCHEMA','TABLE_NAME','ENGINE']])
		not_innodb = tables[~tables.ENGINE.isin(['InnoDB'])][['TABLE_SCHEMA','TABLE_NAME','ENGINE']]

		#显示插件信息
		all_plugins = plugins[['PLUGIN_NAME','PLUGIN_STATUS','PLUGIN_TYPE','PLUGIN_TYPE_VERSION','PLUGIN_AUTHOR','LOAD_OPTION']]

		#长时间未更新统计信息的表/索引 本次演示就是2天前
		over30days_table_static = innodb_table_stats.where(innodb_table_stats['last_update'] < str(datetime.datetime.now() - datetime.timedelta(days=30)), ).dropna().drop_duplicates(keep=False)
		over30days_index_static = innodb_index_stats.where(innodb_index_stats['last_update'] < str(datetime.datetime.now() - datetime.timedelta(days=30)), ).dropna().drop_duplicates(keep=False)

		#变量
		innodb_buffer_pool_size = int(variables.loc['innodb_buffer_pool_size','value'])
		default_storage_engine = variables.loc['default_storage_engine','value']
		sync_binlog = int(variables.loc['sync_binlog','value'])
		innodb_flush_log_at_trx_commit = int(variables.loc['innodb_flush_log_at_trx_commit','value'])
		read_only = variables.loc['read_only','value']
		max_connections = int(variables.loc['max_connections','value'])
		binlog_format = variables.loc['binlog_format','value']
		binlog_row_image = variables.loc['binlog_row_image','value']
		log_bin = variables.loc['log_bin','value']
		innodb_log_file_size = int(variables.loc['innodb_log_file_size','value'])
		server_uuid = variables.loc['server_uuid','value']
		innodb_page_size = variables.loc['innodb_page_size','value']

		#状态
		#print("部分状态信息")
		#print(status.loc['Uptime','value'])
		#print(status.loc['Connections','value'])

		#主从信息
		try:
			Master_Host=slave_status[0][1]
			Master_Port=slave_status[0][3]
			Slave_IO_Running=slave_status[0][10]
			Slave_SQL_Running=slave_status[0][11]
			Master_Bind=slave_status[0][46]
		except:
			Master_Host=""
			Master_Port=""
			Slave_IO_Running=""
			Slave_SQL_Running=""
			Master_Bind=""



		#碎片
		#print("碎片大于1M")
		over_100M_data_free = tables.where(tables["DATA_FREE"]>107374182400 )[['TABLE_SCHEMA','TABLE_NAME','DATA_FREE']].dropna()

		#用户和权限
		user_any = users.where(users["Host"]=="%")[['User','Host']].dropna()


		#锁
		#print("innodb锁")
		#print(innodb_locks)
		

		#各种TOP20
		#状态持续最长的前20个进程
		session_top20 = processlist[['USER', 'HOST', 'DB', 'COMMAND', 'TIME', 'STATE', 'INFO']].sort_values(by=["TIME"], ascending=False).head(20)


		#执行次数前10的SQL
		#sql_top10 = statement_analysis[['query', 'db', 'full_scan', 'exec_count', 'total_latency', 'max_latency', 'avg_latency', 'lock_latency', 'rows_sent', 'rows_sent_avg', 'digest']].sort_values(by=["exec_count","total_latency"],ascending=False).head(10)
		#top20 sql
		top20_sql = events_statements_summary_by_digest.head(20)
		

		#最大的前20张表
		table_top20 = tables[["TABLE_SCHEMA","TABLE_NAME","TABLE_ROWS","DATA_LENGTH","INDEX_LENGTH"]].sort_values(by=["DATA_LENGTH","INDEX_LENGTH"],ascending=False).head(20)

		#top20 lock
		lock_top20 = innodb_locks[[ "locked_table",'wait_age_secs','locked_index','locked_type', 'waiting_query','blocking_query','sql_kill_blocking_query' ]].sort_values(by=['wait_age_secs'],ascending=False).head(20)


		#top20 open tables
		top20_open_tables = table_handles.head(20)

		#top20 wait event
		top20_wait_events = events_waits_summary_global_by_event_name.head(20)

		#top20 metadata_locks
		top20_metadata_locks = metadata_locks.head(20)

		#top20 accounts
		top20_accounts = accounts.sort_values(by=['CURRENT_CONNECTIONS','TOTAL_CONNECTIONS'], ascending=False).head(20)
	
		#测试
		#print("####################################################################################")
		#print(tables.groupby(['TABLE_SCHEMA']).agg({'TABLE_NAME':'count','DATA_LENGTH':'sum','INDEX_LENGTH':'sum'}).sort_values(by=['DATA_LENGTH','INDEX_LENGTH'], ascending=False).reset_index(inplace=False))


		#print(SLOW_LOG)
		#print(any(SLOW_LOG))
		#exit(1)

		#开始分析slow log
		CAN_SLOW_LOG = True
		if any(SLOW_LOG):
			slow_query_tmp = []
			if SLOW_LOG["TYPE"] == "pt-query-digest":
				pt_classes = json.loads(SLOW_LOG["DATA"])["classes"]
				pt_global = json.loads(SLOW_LOG["DATA"])["global"]
			elif SLOW_LOG["TYPE"] == "text" and  get_local_command_result("pt-query-digest --help")["CODE"] == 0:
				with tempfile.TemporaryFile() as fp:
					fp.write(str(SLOW_LOG["DATA"]).encode('utf-8'))
					fp.seek(0)
					with subprocess.Popen("pt-query-digest --output json", shell=True,stdin=fp, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as f:
						try:
							slow_log_data = str(f.stdout.read().rstrip(),encoding="utf-8")
						except:
							f.kill()
							slow_log_data = str(f.stdout.read().rstrip(),encoding="utf-8")
				slow_log_data = json.loads(slow_log_data.split("\n")[2])
				pt_classes = slow_log_data["classes"]
				#pt_global = slow_log_data["pt_global"]
			else:
				print("无 pt-query-digest 分析慢日志, 将跳过慢日志分析....")
				have_slow_query_tmp_df_orderby = False
				slow_query_tmp_df_orderby = ""
				CAN_SLOW_LOG = False
			if CAN_SLOW_LOG:
				for x in pt_classes:
					tmp_result = {
						'checksum':x["checksum"],
						'query_count':x["query_count"],
						'Query_time_avg':x['metrics']['Query_time']['avg'],
						'Query_time_max':x['metrics']['Query_time']['max'],
						'Query_time_min':x['metrics']['Query_time']['min'],
						'Query_time_median':float(x['metrics']['Query_time']['median']),
						'Query_time_pct_95':x['metrics']['Query_time']['pct_95'],
						'db':x['metrics']['db']['value'],
						'sql':x['example']['query'],
					}
					slow_query_tmp.append(tmp_result)
	
				try:
					slow_query_tmp_df = pd.DataFrame(slow_query_tmp)
					slow_query_tmp_df_orderby = slow_query_tmp_df.sort_values(by=['Query_time_median'],ascending=False).head(20).values
					have_slow_query_tmp_df_orderby = True
				except Exception as e:
					slow_query_tmp_df_orderby = ""
					have_slow_query_tmp_df_orderby = False
		else:
			have_slow_query_tmp_df_orderby = False
			slow_query_tmp_df_orderby = ""
	

		#error log
		#print(ERROR_LOG)
		error_log_tmp = {}
		error_log_tmp["time"] = []
		error_log_tmp["n"] = []
		error_log_tmp["error"] = []
		error_log_tmp["info"] = []
		have_error_log_tmp_df_orderby = False
		for x in ERROR_LOG.split("\n"):
			try:
				if x.split()[2] == "[ERROR]" :
					error_log_tmp["time"].append(x.split()[0])
					error_log_tmp["n"].append(x.split()[1])
					error_log_tmp["error"].append(x.split()[2])
					error_log_tmp["info"].append(x.split("[ERROR]")[1])
					have_error_log_tmp_df_orderby = True
			except:
				continue
		try:
			error_log_tmp_df = pd.DataFrame(error_log_tmp)
			error_log_tmp_df_orderby = error_log_tmp_df.tail(20).values
		except:
			error_log_tmp_df_orderby=""
		


		#画图 数据库大小
		dbcount_df= tables.groupby(['TABLE_SCHEMA']).agg({'DATA_LENGTH':'sum','INDEX_LENGTH':'sum'}).sort_values(by=['DATA_LENGTH','INDEX_LENGTH'], ascending=False)
		tmps_ = io.BytesIO()
		dbcount_df.plot(kind="bar",yticks=[]).get_figure().savefig(tmps_,format='png', bbox_inches="tight")
		dbcount_img_base64 = base64.b64encode(tmps_.getvalue()).decode("utf-8").replace("\n", "")

		#渲染模板 比较坑, 得把文件拆分为文件路径和文件名字...  FileSystemLoader指定文件的路径
		(tmp_file_path,tmp_file_name) = os.path.split(TEMPLATE_FILE)
		if len(tmp_file_path) == 0:
			tmp_file_path = "./"
		env = Environment(loader=FileSystemLoader(tmp_file_path)) 
		template = env.get_template(tmp_file_name)
		tmp_file = template.render(
mysql_inspection_version=mysql_inspection_version,
xunjian_analyze_version=analyze_version,
author=AUTHOR,
host=HOST,
port=PORT,
dbtype=DBTYPE, 
version=version[0][0], 
server_id=variables.loc['server_id','value'],
isslave=any(Master_Host),
uptime=int(status.loc['Uptime','value']),
dbcount=tables.groupby(['TABLE_SCHEMA']).agg({'TABLE_NAME':'count','DATA_LENGTH':'sum','INDEX_LENGTH':'sum'}).sort_values(by=['DATA_LENGTH','INDEX_LENGTH'], ascending=False).reset_index(inplace=False).values,
dbcount_img_base64=dbcount_img_base64,
no_innodb=tables[~tables.ENGINE.isin(['InnoDB'])][['TABLE_SCHEMA','TABLE_NAME','ENGINE']].values,
no_primary=no_primary_key.values,
repeat_index=repeat_index.values,
no_index=no_index.values,
over30days_table_static=over30days_table_static.values,
over30days_index_static=over30days_index_static.values,
over_100M_data_free=over_100M_data_free.values,
user_any=user_any.values,
tps=tps,
qps=qps,
transaction_isolation=variables.loc['transaction_isolation','value'],
master_host=Master_Host,
master_port=Master_Port,
slave_io_running=Slave_IO_Running,
slave_sql_running=Slave_SQL_Running,
master_bind=Master_Bind,
session_top20=session_top20.values,
table_top20=table_top20.values,
have_host=HOST_INFO["HAVE_DATA"],
data_dir=DATA_DIR,
logbin_dir=LOGBIN_DIR,
relay_dir=RELAY_DIR,
all_plugins=all_plugins.values,
cpu_p=CPU_USAGE_100,
cpu_p_total=CPU_USAGE_100_TOTAL,
mem_p=round( (MEM_TOTAL - MEM_ALI ) / MEM_TOTAL * 100 ,2),
os_detail="{OS_NAME} {PLATFORM} {KERNEL_VERSION}".format(OS_NAME=OS_NAME, PLATFORM=PLATFORM, KERNEL_VERSION=KERNEL_VERSION),
loadavg=LOAD_AVG,
lock_top20=lock_top20.values,
innodb_buffer_pool_size=innodb_buffer_pool_size,
sys_total_mem=MEM_TOTAL,
default_storage_engine=default_storage_engine,
sync_binlog=sync_binlog,
innodb_flush_log_at_trx_commit=innodb_flush_log_at_trx_commit,
read_only=read_only,
slow_query_tmp_df_orderby=slow_query_tmp_df_orderby,
have_slow_query_tmp_df_orderby=have_slow_query_tmp_df_orderby,
max_connections=max_connections,
binlog_format=binlog_format,
log_bin=log_bin,
binlog_row_image=binlog_row_image,
innodb_log_file_size=innodb_log_file_size,
error_log_tmp_df_orderby=error_log_tmp_df_orderby,
have_error_log_tmp_df_orderby=have_error_log_tmp_df_orderby,
total_db_count=total_db_count,
total_table_count=total_table_count,
total_size=total_size,
total_conn_count=total_conn_count,
total_thread_count=total_thread_count,
have_processlist_slave=have_processlist_slave,
processlist_slave=processlist_slave,
server_uuid=server_uuid,
innodb_page_size=innodb_page_size,
top20_open_tables=top20_open_tables.values,
top20_wait_events=top20_wait_events.values,
top20_metadata_locks=top20_metadata_locks.values,
top20_accounts=top20_accounts.values,
top20_sql=top20_sql.values,
over_5_index=over_5_index.values,
disk_type=DISK_TYPE,
have_disk_type=any(DISK_TYPE),
)
		if OUT_FILE is None:
			FILE_HTML = '{FILE}.html'.format(FILE=FILE)
		else:
			FILE_HTML = OUT_FILE
		with open(FILE_HTML,'w') as fhtml :
			fhtml.write(tmp_file)
		print("分析完成, 结果保存在 {html}".format(html=FILE_HTML))


	elif DBTYPE == "PG":
		print('暂不支持 pg')
	else:
		print("不支持 {DBTYPE}".format(DBTYPE=DBTYPE))

def get_templates(file_name):
	print("暂不支持自动生成模板文件.... 后面再实现")
	sys.exit(1)
	with open(file_name,'w',1) as f:
		tmpfile_txt = '''
</html>
'''
		f.write(tmpfile_txt)
	return


def _argparse():
	# argparse用法 https://docs.python.org/3/library/argparse.html
	parser = argparse.ArgumentParser(description='MYSQL巡检报告生成脚本. 最新下载地址: https://github.com/ddcw/inspection')
	parser.add_argument('--file', '-f',  action='store', dest='file1',  help='mysql_inspection采集的json文件')
	parser.add_argument( action='store', dest='file2', nargs='?',  help='mysql_inspection采集的json文件')
	parser.add_argument('--out-file', '-o', action='store', dest='out_file', nargs='?', help='输出文件名(仅支持html). ')
	parser.add_argument('--template-file', '-t', action='store', dest='template_file', default="templates.html", help='巡检报告模板(0.3版本内置一个 优先级最低)')
	parser.add_argument('--version', '-v', '-V', action='store_true', dest="version",  help='VERSION')
	return parser.parse_args()

if __name__ == '__main__':
	parser = _argparse()
	if parser.version :
		print("Version: {analyze_version}".format(analyze_version=analyze_version))
	#json_file 需要分析的文件
	#template_file 模板文件
	json_file = ""
	template_file = "templates.html"	

	if parser.file1 is not None:
		json_file = parser.file1 if os.path.exists(parser.file1) else ""
	elif parser.file2 is not None:
		json_file = parser.file2 if os.path.exists(parser.file2) else ""
	else:
		print("请指定需要分析的JSON文件.")
		sys.exit(1)

	out_file = parser.out_file if parser.out_file is not None else "{json_file}.html".format(json_file=json_file)

	template_file = parser.template_file if parser.template_file is not None else "templates.html"
	if os.path.exists(template_file):
		print("即将开始分析 {json_file} (根据模板文件 {template_file} 生成报告)".format(json_file=json_file, template_file=template_file))
	else:
		print("未找到模板文件({template_file}), 将自动生成模板文件({template_file})".format(template_file=template_file))
		get_templates(template_file)
	main(json_file, out_file, template_file)
