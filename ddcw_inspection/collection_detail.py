# -*- coding: utf-8 -*-

#定义巡检内容

def db_table():
	example = '''
{
"table":"mysql.user",
"only_rows":{"user","host"},
"exclude_rows":{"password","plugin",},
"where":"where user='1234' group by 1 order by 2 limit 1",
"sql":"select * from db1.t1;",
},''' #数据格式就这样, sql优先, only_rows其次, exclude_rows再其次, table最后 (where不为空的话就自动拼接上)
	sys_dbs = "'mysql', 'performance_schema', 'information_schema', 'sys'"
	where_schema_not_sys = "WHERE SCHEMA_NAME NOT IN ({sys_dbs})".format(sys_dbs=sys_dbs)
	where_database_not_sys = "WHERE database_name NOT IN ({sys_dbs})".format(sys_dbs=sys_dbs)
	where_table_schema_not_sys = "WHERE TABLE_SCHEMA NOT IN ({sys_dbs})".format(sys_dbs=sys_dbs)
	where_obj_schema_not_sys = "WHERE OBJECT_SCHEMA NOT IN ({sys_dbs})".format(sys_dbs=sys_dbs)
	return [
{
"table":"mysql.user",
"exclude_rows":{"password","authentication_string"},
},

{
"table":"mysql.slave_master_info",
"where":"",
"exclude_rows":{"User_password"},
},

{
"table":"mysql.slave_relay_log_info",
"where":"",
},

{
"table":"mysql.slave_worker_info",
"where":"",
},

{
"table":"mysql.innodb_table_stats",
"where":where_database_not_sys,
},

{
"table":"mysql.innodb_index_stats",
"where":where_database_not_sys,
},

{
"table":"information_schema.schemata",
"where":where_schema_not_sys,
},

{
"table":"information_schema.tables",
"where":where_table_schema_not_sys,
},

{
"table":"information_schema.columns",
"where":where_table_schema_not_sys,
},

{
"table":"information_schema.statistics",
"where":where_table_schema_not_sys,
},

{
"table":"information_schema.user_privileges",
"where":"",
},

{
"table":"mysql.db",
"where":"",
},

{
"table":"information_schema.innodb_trx",
"where":"",
},

{
"table":"information_schema.processlist",
"sql":"select ID,USER,HOST,DB,COMMAND,TIME,STATE,INFO from information_schema.PROCESSLIST",
},

{
"table":"information_schema.plugins",
"where":"",
},

{
"table":"performance_schema.events_statements_summary_by_digest",
"where":"where DIGEST_TEXT is not null",
},

{
"table":"performance_schema.threads",
"where":"",
},

{
"table":"performance_schema.accounts",
"where":"",
},

{
"table":"performance_schema.socket_instances",
"where":"",
},

{
"table":"performance_schema.events_statements_history",
"where":"order by LOCK_TIME desc limit 50;",
},

{
"table":"performance_schema.metadata_locks",
"where":"where OBJECT_TYPE='TABLE' order by OWNER_THREAD_ID asc limit 50",
},

{
"table":"performance_schema.table_handles",
"where":"",
"sql":"select OBJECT_SCHEMA,OBJECT_NAME,count(*)  from performance_schema.table_handles where OBJECT_TYPE='TABLE' group by OBJECT_SCHEMA,OBJECT_NAME order  by 3 desc limit 50",
},

{
"table":"performance_schema.events_waits_summary_by_account_by_event_name",
"where":"order by COUNT_STAR desc limit 50",
},

{
"table":"performance_schema.events_waits_summary_by_thread_by_event_name",
"where":"order by COUNT_STAR desc limit 50",
},

{
"table":"performance_schema.events_waits_summary_global_by_event_name",
"where":"order by COUNT_STAR desc limit 50",
},

{
"table":"performance_schema.events_statements_summary_by_account_by_event_name",
"where":"order by COUNT_STAR desc limit 50",
},

{
"table":"performance_schema.objects_summary_global_by_type",
"where":"order by COUNT_STAR desc limit 50",
},

{
"table":"performance_schema.file_summary_by_event_name",
"where":"order by COUNT_STAR desc limit 50",
},

{
"table":"performance_schema.events_statements_summary_by_digest",
"where":"",
"sql":"select SCHEMA_NAME,DIGEST,DIGEST_TEXT,COUNT_STAR,SUM_TIMER_WAIT,MIN_TIMER_WAIT,AVG_TIMER_WAIT,MAX_TIMER_WAIT,SUM_LOCK_TIME,SUM_ERRORS,SUM_WARNINGS,SUM_ROWS_AFFECTED,SUM_ROWS_SENT,SUM_ROWS_EXAMINED,SUM_CREATED_TMP_DISK_TABLES,SUM_CREATED_TMP_TABLES,SUM_SELECT_FULL_JOIN,SUM_SELECT_FULL_RANGE_JOIN,SUM_SELECT_RANGE,SUM_SELECT_RANGE_CHECK,SUM_SELECT_SCAN,SUM_SORT_MERGE_PASSES,SUM_SORT_RANGE,SUM_SORT_ROWS,SUM_SORT_SCAN,SUM_NO_INDEX_USED,SUM_NO_GOOD_INDEX_USED,FIRST_SEEN,LAST_SEEN from performance_schema.events_statements_summary_by_digest where DIGEST_TEXT is not null order by COUNT_STAR desc limit 50"
},

{
"table":"performance_schema.table_io_waits_summary_by_index_usage",
"where":where_obj_schema_not_sys + " and INDEX_NAME is null",
},

{
"table":"performance_schema.replication_connection_status",
"where":"",
},

{
"table":"performance_schema.replication_group_members",
"where":"",
},

{
"table":"performance_schema.replication_group_member_stats",
"where":"",
},

{
"table":"performance_schema.replication_connection_configuration",
"where":"",
},

{
"table":"sys.innodb_lock_waits",
"where":"",
},

{
"table":"sys.statement_analysis",
"where":"",
},

{
"table":"sys.innodb_buffer_stats_by_table",
"where":"",
},

{
"table":"sys.io_global_by_wait_by_bytes",
"where":"",
},

{
"table":"sys.memory_by_host_by_current_bytes",
"where":"",
},

{
"table":"sys.memory_by_user_by_current_bytes",
"where":"",
},


]

def db_comm():
	example = '''
{
"name":"variables",
"rows":{"key","value"},
"comm":"show variables",
}
'''#数据格式 返回数据均为二位数组, 所以要指定rows   注: variables 不能删, 因为采集主机信息的时候要用到
	return [
{
"name":"variables",
"rows":["key","value"],
"comm":"show global variables",
},

{
"name":"status",
"rows":["key","value"],
"comm":"show global status",
},

{
"name":"innodb_status",
"rows":["a", "b", "c"],
"comm":"show engine innodb status",
},

{
"name":"slave_status",
"rows":["key","value"],
"comm":"show slave status",
},

]

def host_comm():
	#主机信息不好写啊..... 脚本里面写吧...
	example = '''
{
"name":"meminfo",
"comm":"cat /proc/meminfo",
"rows":{"obj","value"}
}
'''
	return [
{
"name":"meminfo",
"comm":"cat /proc/meminfo",
"rows":{"obj","value"}
},

]
