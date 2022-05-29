# -*- coding: utf-8 -*-
import pandas as pd
import datetime
import json
import tempfile
import subprocess

class set:
	def __init__(self,*args,**kwargs):
		try:
			self.data = kwargs["data"]
		except Exception as e:
			print(e)
			return False

		self.result = {}
		self.VERSION = "1.0"
		self.result["VERSION"] = self.VERSION

	def analyze(self):
		data = self.data
		result = {}

		#判断有没得数据
		try:
			if data["DBINFO"]["HAVEDATA"]:
				pass
			else:
				print("无数据库信息")
				return False
		except Exception as e:
			print(e, "格式不对, 可能是版本有问题")
			return False


		def to_pandas(rows_str,datas):
			try:
				rows = []
				for x in rows_str.split(","):
					rows.append(x.strip())
				return {"istrue":True, "data":pd.DataFrame(datas,columns=rows)}
			except Exception as e:
				return {"istrue":False, "data":e}
		def to_pandas_key(rows_str,datas):
			try:
				rows = rows_str
				return {"istrue":True, "data":pd.DataFrame(datas,columns=rows).set_index(rows[0])}
			except Exception as e:
				return {"istrue":False, "data":e}
		#把表之类的信息转换为pandas
		table_list = {}
		for table in data["DBINFO"]["table"]:
			tmp_data = data["DBINFO"]["table"][table]
			if tmp_data["havedata"]:
				to_pandas_tmp = to_pandas(tmp_data["rows"],tmp_data["data"])
				if to_pandas_tmp["istrue"] :
					table_list[table] = to_pandas_tmp["data"] 

		table_comm_list = {}
		#把show variables之类的也转化为pandas
		for comm in data["DBINFO"]["comm"]:
			if comm == "slave_status":
				continue #slave_status不同版本有不同行,  就当作二位数组就行 #其实innodb status也没必要的....
			tmp_data = data["DBINFO"]["comm"][comm]
			if tmp_data["havedata"]:
				to_pandas_tmp = to_pandas_key(tmp_data["rows"],tmp_data["data"])
				if to_pandas_tmp["istrue"] :
					table_comm_list[comm] = to_pandas_tmp["data"] 


	#		table_comm_list["status"] = pd.DataFrame(data["DBINFO"]["comm"]["status"]["data"], columns=['key','value']).set_index('key')
	#		print(table_comm_list["status"]["Queries"])
	#	except Exception as e:
	#		print(e)
	#		table_comm_list["status"] = None

		try:
			table_comm_list["slave_status"] = data["DBINFO"]["comm"]["slave_status"]["data"]
		except:
			pass
		#print(table_comm_list["slave_status"][0][11])



		#主机信息获取
		HAVE_HOSTINFO = False
		try:
			if data["HOSTINFO"]["HAVEDATA"]:
				HAVE_HOSTINFO = True
		except:
			pass





		#开始分析: 并生成result
		#result["no_innodb_table"] = {"istrue":True,"data":data, "describe":"非innodb表"} 格式就这样, 全部传递给jinja2 jinja2再生成具体的数据


		#基础信息
		try:
			result["AUTHOR"] = data["INFO"]["AUTHOR"]
			result["DBTYPE"] = data["INFO"]["DBTYPE"]
		except:
			result["DBTYPE"] = "MYSQL"

		result["time"] = data["INFO"]["START_TIME"]

		#非innodb表
		try:
			tables = table_list["information_schema.tables"]
			not_innodb = table_list["information_schema.tables"][~table_list["information_schema.tables"].ENGINE.isin(['InnoDB'])].where(tables['TABLE_TYPE'] == 'BASE TABLE' )[['TABLE_SCHEMA','TABLE_NAME','ENGINE']].dropna().values #相当于sql: select TABLE_SCHEMA,TABLE_NAME,ENGINE from information_schema.tables where ENGINE not in ('InnoDB')  #系统表在采集数据的时候就已经过滤了...
			result["no_innodb_table"] = {"istrue":True, "data":not_innodb, "describe":"非innodb表"}
		except Exception as e:
			print("no_innodb_table",e)
			result["no_innodb_table"] = {"istrue":False, "data":"", "describe":"非innodb表"}


		#各种引擎的表
		try:
			all_engine_table = tables.groupby(['ENGINE'])["TABLE_NAME"].count().reset_index(drop=False,inplace=False)
			all_engine_table_T = all_engine_table.T
			result["all_engine_table"] = {"istrue":True,"data":{"all_engine_table":all_engine_table.values,"all_engine_table_T":all_engine_table_T.values}}
		except Exception as e:
			print("all_engine_table",e)
			result["all_engine_table"] = {"istrue":True,"data":""}


		#无主键的表
		try:
			cols = table_list["information_schema.columns"]
			primary_key_unique_key_table = cols[cols.COLUMN_KEY.isin(['PRI','UNI'])][['TABLE_SCHEMA','TABLE_NAME']]
			no_primary_key = pd.concat([tables.where(tables['TABLE_TYPE'] == 'BASE TABLE' )[['TABLE_SCHEMA','TABLE_NAME']],primary_key_unique_key_table,primary_key_unique_key_table]).drop_duplicates(keep=False).values
			result["no_primary_key"] = {"istrue":True, "data":no_primary_key, "describe":"无主键的表"}
		except Exception as e:
			print("no_primary_key",e)
			result["no_primary_key"] = {"istrue":False, "data":"", "describe":"无主键的表"}


		#重复索引的表
		try:
			statistics = table_list["information_schema.statistics"]
			re_index = statistics[statistics.duplicated(subset=['TABLE_SCHEMA','TABLE_NAME','COLUMN_NAME'],keep=False)]
			repeat_index=re_index[['TABLE_SCHEMA','TABLE_NAME','INDEX_NAME','COLUMN_NAME']].sort_values(by=['TABLE_SCHEMA','TABLE_NAME','COLUMN_NAME'],ascending=False).values
			result["repeat_index"] = {"istrue":True, "data":repeat_index, "describe":"有重复索引的表"}
		except Exception as e:
			print("repeat_index",e)
			result["repeat_index"] = {"istrue":False, "data":"", "describe":"有重复索引的表"}
			


		#没得索引的表
		try:
			have_index_table = cols[cols.COLUMN_KEY.isin(['PRI','UNI','MUL'])][['TABLE_SCHEMA','TABLE_NAME']]
			no_index = pd.concat([tables[['TABLE_SCHEMA','TABLE_NAME']],have_index_table,have_index_table]).drop_duplicates(keep=False).values
			result["no_index"] = {"istrue":True, "data":no_index, "describe":"没得索引的表"}
		except Exception as e:
			print("no_index",e)
			result["no_index"] = {"istrue":False, "data":"", "describe":"没得索引的表"}


		#索引数量超过5的表
		try:
			#print(statistics[statistics.duplicated(subset=['TABLE_SCHEMA','TABLE_NAME','INDEX_NAME'],keep=False)])
			#print(statistics[statistics.duplicated(subset=['TABLE_SCHEMA','TABLE_NAME','INDEX_NAME'],keep=False)])
			over_5_index = statistics[statistics.duplicated(subset=['TABLE_SCHEMA','TABLE_NAME','INDEX_NAME'],keep=False)]  #去重
			over_5_index = over_5_index.groupby(['TABLE_SCHEMA','TABLE_NAME'], as_index=False)["INDEX_NAME"].count() #group by count
			over_5_index = over_5_index.where(over_5_index["INDEX_NAME"]>5).dropna().values
			result["over_5_index"] = {"istrue":True, "data":over_5_index, "describe":"索引数量超过5的表"}
		except Exception as e:
			print("over_5_index",e)
			result["over_5_index"] = {"istrue":False, "data":"", "describe":"索引数量超过5的表"}
			
		

		#数据库信息, 数据库大小, 索引大小之类的
		try:
			databases_0 = tables.groupby(['TABLE_SCHEMA']).agg({'TABLE_NAME':'count','DATA_LENGTH':'sum','INDEX_LENGTH':'sum'}).sort_values(by=['DATA_LENGTH','INDEX_LENGTH'], ascending=False).reset_index(inplace=False)
			databases = databases_0.values
			databases_T = databases_0.T.values
			result["databases"] = {"istrue":True, "data":{"databases":databases, "databases_T":databases_T}, "describe":"数据库信息, 含数据库数据大小,索引大小,表数量"}
		except Exception as e:
			print("databases",e)
			result["databases"] = {"istrue":False, "data":"", "describe":"数据库信息, 含数据库数据大小,索引大小,表数量"}
			

		
		#统计信息过期的表
		try:
			innodb_table_stats = table_list["mysql.innodb_table_stats"]
			over30days_table_static = innodb_table_stats.where(innodb_table_stats['last_update'] < str(datetime.datetime.now() - datetime.timedelta(days=30)), ).dropna().drop_duplicates(keep=False)

			result["over30days_table_static"] = {"istrue":True,"data":over30days_table_static.values}
		except Exception as e:
			print("over30days_table_static",e)
			result["over30days_table_static"] = {"istrue":False,"data":""}

		try:
			innodb_index_stats = table_list["mysql.innodb_index_stats"]
			over30days_index_static = innodb_index_stats.where(innodb_index_stats['last_update'] < str(datetime.datetime.now() - datetime.timedelta(days=30)), ).dropna().drop_duplicates(keep=False)
			result["over30days_index_static"] = {"istrue":True,"data":over30days_index_static.values}
		except Exception as e:
			print("over30days_index_static",e)
			result["over30days_index_static"] = {"istrue":False,"data":""}
			

		#碎片率超过30%的表 (去掉小表, data_free < 40MB的)
		try:
			tables["fragment_rate"] = round(tables["DATA_FREE"]/(tables["DATA_FREE"]+tables["DATA_LENGTH"]),2)
			fragment_table = tables.where((tables["fragment_rate"]>0.3) & (tables["DATA_FREE"] > 41943040))[['TABLE_SCHEMA','TABLE_NAME','DATA_FREE','fragment_rate']].dropna().values
			result["fragment_table"] = {"istrue":True,"data":fragment_table}
		except Exception as e:
			print("fragment_table",e)
			result["fragment_table"] = {"istrue":False,"data":""}


		#大表  大于1000W行 且大于30GB
		try:
			big_table = tables.where((tables["TABLE_ROWS"]>10000000) & (tables["DATA_LENGTH"] > 32212254720) )[['TABLE_SCHEMA','TABLE_NAME','TABLE_ROWS','DATA_LENGTH']].dropna().values
			result["big_table"] = {"istrue":True,"data":big_table}
		except Exception as e:
			print("big_table",e)
			result["big_table"] = {"istrue":False,"data":""}
			
			
		#冷表
		try:
			cold_table = tables.where(tables["UPDATE_TIME"]<str(datetime.datetime.now() - datetime.timedelta(days=60)))[['TABLE_SCHEMA','TABLE_NAME',"UPDATE_TIME"]].dropna().values
			result["cold_table"] = {"istrue":True,"data":cold_table}
		except Exception as e:
			print("cold_table",e)
			result["cold_table"] = {"istrue":False,"data":""}




		#innodb status分析 参考资料: https://dev.mysql.com/doc/refman/5.7/en/innodb-standard-monitor.html
		#Total large memory allocated 4397727744 总内存(字节) 控制页+数据页 1:38.6
		#Dictionary memory allocated 771853 数据字典
		#Buffer pool size   262112  缓冲池总大小(page)
		#Free buffers       260969 剩余的缓冲池大小(page) 也就是free_list
		#Database pages     1140  LRU的大小(不够了就去找free_list)
		#Old database pages 0
		#Modified db pages  0
		#Pending reads      0

		try:
			innodb_status = table_comm_list["innodb_status"]
			engine_innodb_status_detail = innodb_status["c"][0]

			buffer_pool_and_memory = engine_innodb_status_detail.split("----------------------\nBUFFER POOL AND MEMORY\n----------------------")[1].split("--------------\nROW OPERATIONS\n--------------")[0]
			total_buffer_pool_and_memory = buffer_pool_and_memory.split("----------------------\nINDIVIDUAL BUFFER POOL INFO\n----------------------")[0]
			result["BUFFER POOL AND MEMORY"] = {"istrue":True,"data":total_buffer_pool_and_memory}
		except Exception as e:
			print(e,"BUFFER POOL AND MEMORY")
			result["BUFFER POOL AND MEMORY"] = {"istrue":False,"data":""}

		try:
			result["TRANSACTIONS"] = {"istrue":True,"data":engine_innodb_status_detail.split("------------\nTRANSACTIONS\n------------")[1].split("--------\nFILE I/O\n--------")[0]}
		except Exception as e:
			print(e,"TRANSACTIONS")
			result["TRANSACTIONS"] = {"istrue":True,"data":""}

			






		#sql执行情况
		try:
			status = table_comm_list["status"]
			Com_df = status.filter(like='Com_', axis=0)
		#	for index,row in Com_df.iterrows():
		#		try:
		#			Com_df.loc[index]["value"] = int(row["value"])
		#		except:
		#			Com_df.loc[index]["value"] = 0
			Com_df = Com_df[Com_df.value != "0"] #把为0的去掉, 不然太多了影响观看...
			try:
				Com_df = Com_df.drop(['Com_begin','Com_commit','Com_rollback']) #去掉Com_begin和Com_commit和Com_rollback  猜猜为啥要try
			except:
				pass
			Com_df.reset_index(drop=False,inplace=True) #drop=False把索引变成列, inplace=True替换, 不然原来的值是不变的, 只能用来复制..
			sql_comm = Com_df.values
			sql_comm_T = Com_df.T.values
			result["sql_comm"] = {"istrue":True,"data":{"sql_comm":sql_comm,"sql_comm_T":sql_comm_T},"describe":"sql执行情况"}
		except Exception as e:
			print("sql_comm",e)
			result["sql_comm"] = {"istrue":False,"data":"","describe":"sql执行情况"}



		#数据库参数
		try:
			variables = table_comm_list["variables"].to_dict()  #pandas转字典, 这样jinja2就能直接用了
			result["variables"] = {"istrue":True,"data":variables}
		except Exception as e:
			result["variables"] = {"istrue":False,"data":""}


		#top20 table
		try:
			top20_table = table_list["information_schema.tables"][["TABLE_SCHEMA","TABLE_NAME","ENGINE","TABLE_ROWS","DATA_LENGTH","INDEX_LENGTH"]].sort_values(by=["DATA_LENGTH","INDEX_LENGTH"],ascending=False).head(20).values
			result["top20_table"] = {"istrue":True,"data":top20_table}
		except Exception as e:
			result["top20_table"] = {"istrue":False,"data":""}


		#full_table  使用全表扫描的表
		try:
			table_io_waits_summary_by_index_usage = table_list["performance_schema.table_io_waits_summary_by_index_usage"]
			full_table = table_io_waits_summary_by_index_usage[["OBJECT_SCHEMA","OBJECT_NAME","COUNT_STAR","SUM_TIMER_WAIT","AVG_TIMER_WAIT","COUNT_READ","SUM_TIMER_READ","AVG_TIMER_READ"]]
			full_table = full_table.where(full_table["COUNT_READ"]>0).dropna()
			result["full_table"] = {"istrue":True,"data":full_table.values}
		except Exception as e:
			result["full_table"] = {"istrue":False,"data":""}


		#使用临时表sql
		try:
			tmp_table_file_table = table_list["performance_schema.events_statements_summary_by_digest"]
			tmp_table_file = tmp_table_file_table[["SCHEMA_NAME","COUNT_STAR","SUM_CREATED_TMP_DISK_TABLES","SUM_CREATED_TMP_TABLES","SUM_ROWS_AFFECTED","DIGEST_TEXT"]].where((tmp_table_file_table["SUM_CREATED_TMP_DISK_TABLES"]>0) | (tmp_table_file_table["SUM_CREATED_TMP_TABLES"]>0)).dropna()
			result["tmp_table_file"] = {"istrue":True,"data":tmp_table_file.values}
			
		except Exception as e:
			result["tmp_table_file"] = {"istrue":False,"data":""}
			

		#top20 sql
		try:
			events_statements_summary_by_digest = table_list["performance_schema.events_statements_summary_by_digest"]
			top20_sql = events_statements_summary_by_digest[["SCHEMA_NAME","COUNT_STAR","FIRST_SEEN","LAST_SEEN","SUM_ROWS_AFFECTED","DIGEST_TEXT"]].sort_values(by=['COUNT_STAR'],ascending=False).head(20)
			result["top20_sql"] = {"istrue":True,"data":top20_sql.values}
		except Exception as e:
			print("top20_sql",e)
			result["top20_sql"] = {"istrue":False,"data":""}


		#数据库状态分析 show status
		#参考  https://dev.mysql.com/doc/refman/5.7/en/server-status-variables.html
		try:
			status = table_comm_list["status"]
			result["status"] = {"istrue":True,"data":status.to_dict()}
		except Exception as e:
			print(e,"status")
			result["status"] = {"istrue":False,"data":""}
			
			
		#基础汇总信息
		try:
			table_sum_size_gb = round(tables["DATA_LENGTH"].sum() / 1024 / 1024 /1024, 2)
			result["table_sum_size_gb"] = {"istrue":True,"data":table_sum_size_gb}
		except:
			result["table_sum_size_gb"] = {"istrue":False,"data":"0"}

		try:
			index_sum_size_gb = round(tables["INDEX_LENGTH"].sum() / 1024 / 1024 /1024, 2)
			result["index_sum_size_gb"] = {"istrue":True,"data":index_sum_size_gb}
		except:
			result["index_sum_size_gb"] = {"istrue":False,"data":"0"}

			
		#用户表
		try:
			user = table_list["mysql.user"][["Host","User","plugin","password_expired","password_lifetime","Super_priv","Grant_priv","account_locked"]]
			result["user"] = {"istrue":True,"data":user.values}
		except Exception as e:
			result["user"] = {"istrue":False,"data":""}

		#超级用户
		try:
			user_table = table_list["mysql.user"]
			super_user = user_table["Super_priv"].where(user_table["Super_priv"]=="Y").dropna()
			result["super_user"] = {"istrue":True,"data":super_user.values}
		except Exception as e:
			print(e,"super_user")
			result["super_user"] = {"istrue":False,"data":""}

		#密码过期的用户
		try:
			user_table = table_list["mysql.user"]
			password_expired_user = user_table["password_expired"].where(user_table["password_expired"]=="Y").dropna()
			result["password_expired_user"] = {"istrue":True,"data":password_expired_user.values}
		except:
			result["password_expired_user"] = {"istrue":False,"data":""}
			


		#使用内存最多的表
		try:
			innodb_buffer_stats_by_table_table = table_list["sys.innodb_buffer_stats_by_table"]
			innodb_buffer_stats_by_table =  innodb_buffer_stats_by_table_table.sort_values(by=['rows_cached'],ascending=False).head(20).values
			result["innodb_buffer_stats_by_table"] = {"istrue":True,"data":innodb_buffer_stats_by_table}
		except Exception as e:
			print(e,"innodb_buffer_stats_by_table")
			result["innodb_buffer_stats_by_table"] = {"istrue":False,"data":""}


		#IO等待
		try:
			io_global_by_wait_by_bytes = table_list["sys.io_global_by_wait_by_bytes"].values
			result["io_global_by_wait_by_bytes"] = {"istrue":True,"data":io_global_by_wait_by_bytes}
		except Exception as e:
			print(e,"io_global_by_wait_by_bytes")
			result["io_global_by_wait_by_bytes"] = {"istrue":False,"data":""}


		#使用内存最多的前20台主机
		try:
			memory_by_host_by_current_bytes = table_list["sys.memory_by_host_by_current_bytes"][["host","current_count_used","current_allocated","current_avg_alloc","current_max_alloc","total_allocated"]].head(20)
			result["memory_by_host_by_current_bytes"] = {"istrue":True,"data":memory_by_host_by_current_bytes.values}
		except Exception as e:
			print(e,"memory_by_host_by_current_bytes")
			result["memory_by_host_by_current_bytes"] = {"istrue":False,"data":""}
		
		#使用内存最多的用户  TOP20
		try:
			memory_by_user_by_current_bytes = table_list["sys.memory_by_user_by_current_bytes"][["user","current_count_used","current_allocated","current_avg_alloc","current_max_alloc","total_allocated"]].head(20)
			result["memory_by_user_by_current_bytes"] = {"istrue":True,"data":memory_by_user_by_current_bytes.values}
		except Exception as e:
			print(e,"memory_by_user_by_current_bytes")
			result["memory_by_user_by_current_bytes"] = {"istrue":False,"data":""}


		#锁
		try:
			innodb_lock_waits_table = table_list["sys.innodb_lock_waits"]
			innodb_lock_waits = innodb_lock_waits_table[[ "locked_table",'wait_age_secs','locked_index','locked_type', 'waiting_query','blocking_query','sql_kill_blocking_query' ]].sort_values(by=['wait_age_secs'],ascending=False)
			result["innodb_lock_waits"] = {"istrue":True,"data":innodb_lock_waits.values}
		except Exception as e:
			print(e,"innodb_lock_waits")
			result["innodb_lock_waits"] = {"istrue":False,"data":""}
		
			
		#插件
		try:
			plugins = table_list["information_schema.plugins"][['PLUGIN_NAME','PLUGIN_STATUS','PLUGIN_TYPE','PLUGIN_TYPE_VERSION','PLUGIN_AUTHOR','LOAD_OPTION']]
			result["plugins"] = {"istrue":True,"data":plugins.values}
		except Exception as e:
			print(e,"plugins")
			result["plugins"] = {"istrue":False,"data":""}
			
			
			


		#processlist
		try:
			processlist = table_list["information_schema.processlist"]
			result["processlist"] = {"istrue":True,"data":processlist.values}
		except Exception as e:
			print("processlist",e)
			result["processlist"] = {"istrue":False,"data":""}

		#threads
		try:
			threads = table_list["performance_schema.threads"]
			result["threads"] = {"istrue":True,"data":threads.values}
		except Exception as e:
			print("threads",e)
			result["threads"] = {"istrue":False,"data":""}
		
		

		#集群高可用信息
		try:
			slave_status = table_comm_list["slave_status"]
			#print(slave_status,len(slave_status[0]))
			#slave_host = slave_status[1]
			#slave_port = slave_status[3]
			result["slave_status"] = {"istrue":True,"data":slave_status}
		except Exception as e:
			print("no slave status")
			result["slave_status"] = {"istrue":False,"data":""}

		#group replication
		try:
			replication_group_members = table_list["performance_schema.replication_group_members"][["CHANNEL_NAME","MEMBER_ID","MEMBER_HOST","MEMBER_PORT","MEMBER_STATE",]] #8.0会多几个参数
			result["replication_group_members"] = {"istrue":True,"data":replication_group_members.values}
		except Exception as e:
			print("replication_group_members",e)
			result["replication_group_members"] = {"istrue":False,"data":""}

		try:
			replication_group_member_stats = table_list["performance_schema.replication_group_member_stats"][["CHANNEL_NAME","VIEW_ID","MEMBER_ID","COUNT_TRANSACTIONS_IN_QUEUE","COUNT_TRANSACTIONS_CHECKED","COUNT_CONFLICTS_DETECTED","COUNT_TRANSACTIONS_ROWS_VALIDATING","TRANSACTIONS_COMMITTED_ALL_MEMBERS","LAST_CONFLICT_FREE_TRANSACTION"]]
			result["replication_group_member_stats"] = {"istrue":True,"data":replication_group_member_stats.values}
		except Exception as e:
			print("replication_group_member_stats",e)
			result["replication_group_member_stats"] = {"istrue":True,"data":""}
	
			


		#当前服务器角色(主/从/GR主/GR从)
		try:
			try:
				if result["status"]["data"]["value"]["group_replication_primary_member"] == result["variables"]["data"]["value"]["server_uuid"]:
					current_role = "MGR主节点"
				elif (result["status"]["data"]["value"]["group_replication_primary_member"] != result["variables"]["data"]["value"]["server_uuid"]) and any(result["status"]["data"]["value"]["group_replication_primary_member"]):
					current_role = "MGR从节点"
				else:
					current_role = None
			except:
				current_role = None
			
			if current_role is None:
				current_role = ""
				try:
					if result["slave_status"]["istrue"] and len(result["slave_status"]["data"]) > 0:
						current_role += " 从库 "
				except:
					pass
				if processlist.where(processlist['COMMAND']=="Binlog Dump")[["HOST"]].dropna().values.shape[0] > 0:
					current_role += " 主库(有{n}个从库) ".format(n=processlist.where(processlist['COMMAND']=="Binlog Dump")[["HOST"]].dropna().values.shape[0])
			if current_role == "":
				current_role = "非主非从" 
			
			result["current_role"] = {"istrue":True,"data":current_role}
		except Exception as e:
			print("current_role",e)
			result["current_role"] = {"istrue":False,"data":""}



		#主机信息分析
		if HAVE_HOSTINFO:
			result["havehostdata"] = True
			hostdata = data["HOSTINFO"]

			#binlog
			#binlog增长变化
			try:
				binlog_stat_data = []
				for x in hostdata["mysqlinfo"]["stdout"]["binlog_stat"]["data"].split("\n"):
					binlog_stat_data.append(x.split())
				binlog_stat_df = pd.DataFrame(binlog_stat_data,columns=["time","size"])
				#把size部分换成整型  有必要的话, 还能进行单位换算, 比如换成MB
				for index,row in binlog_stat_df.iterrows():
					try:
						binlog_stat_df.loc[index]["size"] = int(row["size"])
					except:
						binlog_stat_df.loc[index]["size"] = 0
				binlog_stat_df_group_by = binlog_stat_df.groupby(['time']).agg({'size':['sum','count']})
				binlog_stat_df_group_by.reset_index(drop=False,inplace=True)
				binlog_stat_df_group_by_T = binlog_stat_df_group_by.T
				result["binlog_grows"] = {"istrue":True,"data":{"binlog_stat_df_group_by_T":binlog_stat_df_group_by_T.values,"binlog_stat_df_group_by":binlog_stat_df_group_by.values},}
			except Exception as e:
				print("binlog_grows",e)
				result["binlog_grows"] = {"istrue":False,"data":""}

			#慢sql分析
			try:
				slow_log_format_is_pt =  hostdata["mysqlinfo"]["stdout"]["slow_log"]["have_pt"]
				slow_log = hostdata["mysqlinfo"]["stdout"]["slow_log"]["data"]
				if hostdata["mysqlinfo"]["stdout"]["slow_log"]["status"]:
					if slow_log_format_is_pt:
						pt_classes = json.loads(slow_log)["classes"]
						pt_global = json.loads(slow_log)["global"]
					else:
						#使用本机的pt分析
						with tempfile.TemporaryFile() as fp:
							fp.write(str(slow_log).encode('utf-8'))
							fp.seek(0)
							with subprocess.Popen("pt-query-digest --output json | tail -n +2", shell=True,stdin=fp, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as f:
								slow_log_data = str(f.stdout.read().rstrip(),encoding="utf-8")
						slow_log = json.loads(slow_log_data)
						pt_classes = slow_log["classes"]
					#转换格式
					slow_query_tmp = []
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
					#转换成dataframe
					slow_query_tmp_df = pd.DataFrame(slow_query_tmp)
					slow_query_tmp_df_orderby = slow_query_tmp_df.sort_values(by=['Query_time_median'],ascending=False).head(20).values
					result["slow_sql"] = {"istrue":True,"data":slow_query_tmp_df_orderby}
				else:
					#TODO PY ANALYZE SLOW LOG
					result["slow_sql"] = {"istrue":False,"data":""}
			except Exception as e:
					print("no slow sql",e)
					result["slow_sql"] = {"istrue":False,"data":""}


			#错误日志分析
			try:
				error_log =  hostdata["mysqlinfo"]["stdout"]["error_log"]["data"]
				if hostdata["mysqlinfo"]["stdout"]["error_log"]["status"] :
					error_log_tmp = {}
					error_log_tmp["time"] = []
					error_log_tmp["n"] = []
					error_log_tmp["error"] = []
					error_log_tmp["info"] = []
					have_error_log_tmp_df_orderby = False
					for x in error_log.split("\n"):
						try:
							if x.split()[2] == "[ERROR]" :
								error_log_tmp["time"].append(x.split()[0])
								error_log_tmp["n"].append(x.split()[1])
								error_log_tmp["error"].append(x.split()[2])
								error_log_tmp["info"].append(x.split("[ERROR]")[1])
								have_error_log_tmp_df_orderby = True
						except:
							continue
					error_log_tmp_df = pd.DataFrame(error_log_tmp)
					error_log_tmp_df_orderby = error_log_tmp_df.tail(20).values
					result["error_log"] = {"istrue":True,"data":error_log_tmp_df_orderby}
				else:
					result["error_log"] = {"istrue":False,"data":""}
			except Exception as e:
				print("error_log",e)
				result["error_log"] = {"istrue":False,"data":""}



			#数据目录
			try:
				data_log_dir = hostdata["mysqlinfo"]["stdout"]["datadir"]
				result["data_log_dir"] = {"istrue":True,"data":data_log_dir.split()}
			except Exception as e:
				print(e,"data_log_dir")
				result["data_log_dir"] = {"istrue":False,"data":""}
			
				
			#日志目录
			try:
				log_bin_index = hostdata["mysqlinfo"]["stdout"]["log_bin_index"]
				result["log_bin_index"] = {"istrue":True,"data":log_bin_index.split()}
			except Exception as e:
				print(e,"log_bin_index")
				result["log_bin_index"] = {"istrue":False,"data":""}


			#CPU使用率等
			try:
				uptime = hostdata["uptime"]["stdout"]
				cpu_socket = hostdata["cpu_socket"]["stdout"]
				cpu_core = hostdata["cpu_core"]["stdout"]
				cpu_thread = hostdata["cpu_thread"]["stdout"]
				timezone = hostdata["timezone"]["stdout"]
				meminfo = hostdata["meminfo"]["stdout"]
				osname = hostdata["osname"]["stdout"]
				kernel = hostdata["kernel"]["stdout"]
				loadavg = hostdata["loadavg"]["stdout"]
				swappiness = hostdata["swappiness"]["stdout"]
				hostname = hostdata["hostname"]["stdout"]
				platform = hostdata["platform"]["stdout"]

				#cpu使用率计算  uptime或者cpu数量 有为0的情况(虽然不可能, 但是确实有这个异常..), 所以这这计算使用率
				try:
					uptime_0 = uptime.split()[0]
					uptime_1 = uptime.split()[1]
					cpu_use = float(uptime_1)/(float(uptime_0)*float(cpu_socket)*float(cpu_core)*float(cpu_thread))
					cpu_p = round( (1 - cpu_use)*100 ,2)
					cpu_p = str(cpu_p) + '%'
				except Exception as e:
					print(e,' uptime: ',uptime.split()[0], uptime.split()[1], ' cpu: ',cpu_socket,cpu_core,cpu_thread)
					cpu_p = ''

				mem = {}
				for x in meminfo.split("\n"):
					mem_kv = x.split(":")
					mem[mem_kv[0]] = int(mem_kv[1].strip().split()[0])
				result["cpu_mem"] = {"istrue":True,"cpu_socket":cpu_socket,"cpu_core":cpu_core,"cpu_thread":cpu_thread,"timezone":timezone,"mem":mem,"uptime":uptime.split(),"osname":osname, "kernel":kernel, "loadavg":loadavg.split(), "swappiness":swappiness,"hostname":hostname,"platform":platform,'cpu_p':cpu_p}
			except Exception as e:
				result["cpu_mem"] = {"istrue":False}
				print(e,"cpu_mem")

		else:
			result["havehostdata"] = False
			print("无主机信息可供分析..")
			

		

		self.result = result


	def test(self):
		data = self.data
		#简单的测试下数据获取正常不...
		for x in data["DBINFO"]["table"]:
			print(data["DBINFO"]["table"][x]["havedata"], x, )

		for x in data["DBINFO"]["comm"]:
			print(data["DBINFO"]["comm"][x]["havedata"],x)

		for x in data["HOSTINFO"]:
			print(data["HOSTINFO"][x]["code"],x)
		


	def return_json(self):
		return self.result


	def return_json_file(self, file_name):
		return "xx"
		
			

