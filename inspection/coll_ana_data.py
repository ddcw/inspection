import pandas as pd
import datetime
#import numpy as np
class init_data:
	def __init__(self,conn):
		self.conn = conn

	def global_variables(self,):
		sql = "show global variables;"
		try:
			data = pd.read_sql_query(sql,self.conn,index_col='Variable_name').T
			return {"status":True,"data":data}
		except Exception as e:
			return {"status":False,"data":e}

	def setup_instruments(self):
		sql = "select * from performance_schema.setup_instruments;"
		try:
			data = pd.read_sql_query(sql,self.conn,)
			return {"status":True,"data":data}
		except Exception as e:
			return {"status":False,"data":e}

	def statement_analysis(self):
		sql = "select * from sys.statement_analysis;"
		try:
			data = pd.read_sql_query(sql,self.conn,)
			return {"status":True,"data":data}
		except Exception as e:
			return {"status":False,"data":e}


	def tables(self):
		sql = "select * from information_schema.tables where table_schema not in ('sys','information_schema','mysql','performance_schema');"
		try:
			data = pd.read_sql_query(sql,self.conn,)
			return {"status":True,"data":data}
		except Exception as e:
			return {"status":False,"data":e}

	def columns(self):
		sql = "select * from information_schema.columns where table_schema not in ('sys','information_schema','mysql','performance_schema');"
		try:
			data = pd.read_sql_query(sql,self.conn,)
			return {"status":True,"data":data}
		except Exception as e:
			return {"status":False,"data":e}

	def global_status(self):
		sql = "show global status"
		try:
			data = pd.read_sql_query(sql,self.conn,index_col='Variable_name').T
			return {"status":True,"data":data}
		except Exception as e:
			return {"status":False,"data":e}



class global_status:
	def __init__(self,*args,**kwargs):
		aa = "123"

	def t1():
		aa = 1


#具体的采集项 和 conf/conf.yaml 对应
#返回数据格式,{status:True,"data":"data","score":2}
#status 是否巡检成功
#data 巡检结果或者报错
#score 扣分
#type 巡检结果类型,  0 正常   1 达到warning  2 达到error
class collanadata:
	def __init__(self,*args,**kwargs):
		#self.conn = kwargs['conn']
		#self.global_variables = kwargs['global_variables']
		#self.setup_instruments = kwargs['setup_instruments']
		#self.tables = kwargs['tables']
		#self.columns = kwargs['columns']
		self.conn = kwargs['conn']
		self.global_variables = kwargs['result']['global_variables']
		self.tables = kwargs['result']['tables']
		self.setup_instruments = kwargs['result']['setup_instruments']
		self.columns = kwargs['result']['columns']
		self.global_status = kwargs['result']['global_status']
		self.conf = kwargs['conf']
		self.statement_analysis = kwargs['result']['statement_analysis']

	def list_int_to_date(self,strlist):
		return [datetime.datetime.utcfromtimestamp(i).strftime("%Y-%m-%d %H:%M:%S") for i in strlist]


	#内部函数, 计算分值的, 因为多数计算方法一样, 就搞了个函数来整
	def _inner_func1(self,pd1,c):
		t = 0
		score = c['Score']
		if pd1.shape[0] > c['Error']:
			t = 2
			score = 0 * c['Score']
		elif pd1.shape[0] > c['Warning']:
			t = 1
			score = 0.3 * c['Score']
		else:
			t = 0
			score = 1 * c['Score']
		return t,score

	def _inner_func2(self,pdWarning,pdError,c):
		t = 0
		score = c['Score']
		if pdError.shape[0] > 0:
			t = 2
			score = 0 * c['Score']
		elif pdWarning.shape[0] > 0:
			t = 1
			score = 0.3 * c['Score']
		else:
			t = 0
			score = 1 * c['Score']
		return t,score 

	def _inner_func3(self,k,c):
		t = 0
		score = c['Score']
		if k < c['Error']:
			t = 2
			score = 0 * c['Score']
		elif k < c['Warning']:
			t = 1
			score = 0.3 * c['Score']
		else:
			score = 1 * c['Score']
			t = 0
		return t,score

	def _inner_func4(self,k,c):
		t = 0
		score = c['Score']
		if k > c['Error']:
			t = 2
			score = 0 * c['Score']
		elif k > c['Warning']:
			t = 1
			score = 0.3 * c['Score']
		else:
			score = 1 * c['Score']
			t = 0
		return t,score

	def no_primary_key(self,c):
		sql = ""
		t = 0
		try:
			cols = self.columns['data']
			tables = self.tables['data']
			primary_key_unique_key_table = cols[cols.COLUMN_KEY.isin(['PRI','UNI'])][['TABLE_SCHEMA','TABLE_NAME']] #包含主键和唯一键的表
			no_primary_key = pd.concat([tables.where(tables['TABLE_TYPE'] == 'BASE TABLE' )[['TABLE_SCHEMA','TABLE_NAME']],primary_key_unique_key_table,primary_key_unique_key_table]).drop_duplicates(keep=False) #去掉包含主键和唯一键的表
			if no_primary_key.shape[0] > c['Error']:
				score = 0 * int(c['Score'])
				t = 2
			elif no_primary_key.shape[0] > c['Warning']:
				score = 0.3 * int(c['Score'])
				t = 1
			else:
				score = 1 * int(c['Score'])
			return {"status":True,"data":no_primary_key.values,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}
	
	def redundant_indexes(self,c):
		sql = "select * from sys.schema_redundant_indexes;"
		t = 0
		try:
			data = pd.read_sql_query(sql,self.conn,)
			if data.shape[0] > c['Error']:
				score = 0 * int(c['Score'])
				t = 2
			elif data.shape[0] > c['Warning']:
				score = 0.3 * int(c['Score'])
				t = 1
			else:
				score = 1 * int(c['Score'])
			return {"status":True,"data":data.values,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def unused_indexes(self,c):
		#sql = "select * from sys.schema_unused_indexes;"
		sql = "select * from sys.schema_unused_indexes where object_schema not in ('sys','information_schema','mysql','performance_schema');"
		t = 0
		try:
			data = pd.read_sql_query(sql,self.conn,)
			if data.shape[0] > c['Error']:
				score = 0 * int(c['Score'])
				t = 2
			elif data.shape[0] > c['Warning']:
				score = 0.3 * int(c['Score'])
				t = 1
			else:
				score = 1 * int(c['Score'])
			return {"status":True,"data":data.values,"score":score, "type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}


	def full_table_scans(self,c):
		sql = "select * from sys.schema_tables_with_full_table_scans;"
		t = 0
		try:
			data = pd.read_sql_query(sql,self.conn,)
			if data.shape[0] > c['Error']:
				score = 0 * int(c['Score'])
				t = 2
			elif data.shape[0] > c['Warning']:
				score = 0.3 * int(c['Score'])
				t = 1
			else:
				score = 1 * int(c['Score'])
			return {"status":True,"data":data.values,"score":score, "type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def partitions(self,c):
		sql = "select TABLE_SCHEMA,TABLE_NAME,count(PARTITION_NAME) as count from information_schema.PARTITIONS where table_schema not in ('sys','information_schema','mysql','performance_schema') group by TABLE_SCHEMA,TABLE_NAME;"
		t = 0
		try:
			data = pd.read_sql_query(sql,self.conn,)
			data = data.where(data['count']>0).dropna()
			if data.shape[0] > c['Error']:
				score = 0 * int(c['Score'])
				t = 2
			elif data.shape[0] > c['Warning']:
				score = 0.3 * int(c['Score'])
				t = 1
			else:
				score = 1 * int(c['Score'])
			return {"status":True,"data":data.values,"score":score, "type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def auto_increment_columns(self,c):
		#sql = "select table_schema,table_name,column_name,concat(used_per) as used_percent from (select table_schema,table_name,column_name, round((auto_increment/max_value)*100,2) as used_per from sys.schema_auto_increment_columns) as aa ;"
		sql = "select * from sys.schema_auto_increment_columns where auto_increment_ratio > {warning}".format(warning=c['Warning'])
		t = 0
		try:
			#data = pd.read_sql_query(sql,self.conn,dtypes={'auto_increment_ratio':np.float64})
			data = pd.read_sql_query(sql,self.conn,)
			data['auto_increment_ratio'] = data['auto_increment_ratio'].astype('float64')
			#print(data.dtypes)
			#print(data['used_percent'])
			#data = data.where(data['used_percent']>c['Warning']).dropna()
			dataerror = data.where(data['auto_increment_ratio']>c['Error']).dropna()
			if dataerror.shape[0] > 0:
				score = 0 * int(c['Score'])
				t = 2
			elif data.shape[0] > 0:
				score = 0.3 * int(c['Score'])
				t = 1
			else:
				score = 1 * int(c['Score'])
			return {"status":True,"data":data.values,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def special_column(self,c):
		return {"status":False,"data":"暂不支持","score":0}


	def table_info(self,c):
		try:
			return {"status":True,"data":self.tables['data'].values,"score":0,"type":0}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def big_table(self,c):
		t = 0
		try:
			tables = self.tables['data']
			big_table_warning = tables.where((tables["TABLE_ROWS"]>int(c['Warning']['rows'])) & (tables["DATA_LENGTH"] > int(c['Warning']['size'])) )[['TABLE_SCHEMA','TABLE_NAME','TABLE_ROWS','DATA_LENGTH']].dropna()
			big_table_error = tables.where((tables["TABLE_ROWS"]>int(c['Error']['rows'])) & (tables["DATA_LENGTH"] > int(c['Error']['size'])) )[['TABLE_SCHEMA','TABLE_NAME','TABLE_ROWS','DATA_LENGTH']].dropna()
			if big_table_error.shape[0] > 0:
				score = 0 * c['Score']
				t = 2
			elif big_table_warning.shape[0] > 0:
				score = 0.3 * c['Score']
				t = 1
			else:
				score = 1 * c['Score']
			return {"status":True,"data":big_table_warning.values,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}
			
	def cold_table(self,c):
		t = 0
		try:
			tables = self.tables['data']
			cold_table = tables.where(tables["UPDATE_TIME"]<str(datetime.datetime.now() - datetime.timedelta(days=c['Warning'])))[['TABLE_SCHEMA','TABLE_NAME',"UPDATE_TIME"]].dropna()
			cold_table_error = tables.where(tables["UPDATE_TIME"]<str(datetime.datetime.now() - datetime.timedelta(days=c['Error'])))[['TABLE_SCHEMA','TABLE_NAME',"UPDATE_TIME"]].dropna()
			if cold_table_error.shape[0] > 0:
				score = 0 * c['Score']
				t = 2
			elif cold_table.shape[0] > 0:
				score = 0.3 * c['Score']
				t = 1
			else:
				score = 1 * c['Score']
			return {"status":True,"data":cold_table.values,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def no_innodb(self,c):
		t = 0
		try:
			tables = self.tables['data']
			no_innodb = tables[~tables.ENGINE.isin(['InnoDB'])].where(tables['TABLE_TYPE'] == 'BASE TABLE' )[['TABLE_SCHEMA','TABLE_NAME','ENGINE']].dropna()
			t,score = self._inner_func1(no_innodb,c)
			return {"status":True,"data":no_innodb.values,"score":score,"type":t}
			
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def table_static_expired(self,c):
		t = 0
		try:
			#sql = "select * from mysql.innodb_table_stats where last_update < current_date() - {warningday}".format(warningday=c['Warning']) #使用函数来做时间计算 兼容8.0
			sql = "select * from mysql.innodb_table_stats where last_update < DATE_SUB(current_timestamp(), INTERVAL {warningday} DAY) ".format(warningday=c['Warning'])
			data = pd.read_sql_query(sql,self.conn,)
			data_Error = data.where(data["last_update"]<str(datetime.datetime.now() - datetime.timedelta(days=c['Error']))).dropna()
			if data_Error.shape[0] > 0:
				score = 0 * c['Score']
				t = 2
			elif data.shape[0] > 0:
				score = 0.3 * c['Score']
				t = 1
			else:
				score = 1 * c['Score']
			return {"status":True,"data":data.values,"score":score,"type":t}
			
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def table_fragment(self,c):
		t = 0
		try:
			tables = self.tables['data']
			tables["fragment_rate"] = round(tables["DATA_FREE"]/(tables["DATA_FREE"]+tables["DATA_LENGTH"])*100,2)
			tables_warning = tables.where(tables['fragment_rate']>c['Warning'])[['TABLE_SCHEMA','TABLE_NAME','DATA_LENGTH','DATA_FREE','fragment_rate']].dropna(how='all')
			tables_error = tables.where(tables['fragment_rate']>c['Error']).dropna(how='all')
			t,score = self._inner_func2(tables_warning,tables_error,c)
			#print(tables_warning)
			return {"status":True,"data":tables_warning.values,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def is_nullable(self,c):
		t = 0
		try:
			cols = self.columns['data']
			can_null_cols = cols[cols['IS_NULLABLE'] == "YES"][['TABLE_SCHEMA','TABLE_NAME','COLUMN_NAME']].dropna(how='all')
			#print(can_null_cols)
			t,score = self._inner_func1(can_null_cols,c)
			return {"status":True,"data":can_null_cols.values,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def same_user_password(self,c):
		t = 0
		try:
			#sql = "SELECT CONCAT(user, '@', host) FROM mysql.user WHERE authentication_string = PASSWORD(user) OR authentication_string = PASSWORD(UPPER(user)) OR authentication_string = PASSWORD(CONCAT(UPPER(LEFT(user, 1)), SUBSTRING(user, 2, LENGTH(user))));"
			sql = "SELECT CONCAT(user, '@', host) FROM mysql.user where authentication_string = CONCAT('*', UPPER(SHA1(UNHEX(SHA1(user)))))" #5.7.5之后不支持password函数
			data = pd.read_sql_query(sql,self.conn,)
			t,score = self._inner_func1(data,c)
			return {"status":True,"data":data.values,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def expired_password(self,c):
		t = 0
		try:
			sql = "SELECT CONCAT(user, '@', host) from mysql.user where password_expired='Y';"
			data = pd.read_sql_query(sql,self.conn,)
			t,score = self._inner_func1(data,c)
			return {"status":True,"data":data.values,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def anonymous_user(self,c):
		t = 0
		try:
			sql = "SELECT CONCAT(user, '@', host) FROM mysql.user where user = '';"
			data = pd.read_sql_query(sql,self.conn,)
			t,score = self._inner_func1(data,c)
			return {"status":True,"data":data.values,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}
		
	def any_host(self,c):
		t = 0
		try:
			sql = "SELECT CONCAT(user, '@', host) FROM mysql.user where host = '%';"
			data = pd.read_sql_query(sql,self.conn,)
			t,score = self._inner_func1(data,c)
			return {"status":True,"data":data.values,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}
		
	def simple_password(self,c):
		t = 0
		try:
			conf = self.conf
			password_list = ""
			simple_password_list = []
			with open(conf['GLOBAL']['Dict_passowrd'], 'r') as f:  
				password_list = f.read().rstrip().split('\n')
			for x in password_list:
				sql = "SELECT CONCAT(user, '@', host) FROM mysql.user where authentication_string = CONCAT('*', UPPER(SHA1(UNHEX(SHA1('{password}')))))".format(password=x) #5.7.5之后不支持password函数
				rs = pd.read_sql_query(sql,self.conn,)
				for y in rs.values:
					simple_password_list.append(y[0])
			data = pd.DataFrame(simple_password_list)
			t,score = self._inner_func1(data,c)
			return {"status":True,"data":data.values,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}
		
	def account_user(self,c):
		t = 0
		try:
			sql = "SELECT CONCAT(user, '@', host) FROM mysql.user where account_locked='Y' and user not in ('mysql.infoschema','mysql.session','mysql.sys');"
			data = pd.read_sql_query(sql,self.conn,)
			t,score = self._inner_func1(data,c)
			return {"status":True,"data":data.values,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}
		
	def innodb_buffer_stats_by_schema(self,c):
		t = 0
		score = 0
		try:
			sql = "select * from sys.innodb_buffer_stats_by_schema;"
			data = pd.read_sql_query(sql,self.conn,)
			#t,score = self._inner_func1(data,c)
			return {"status":True,"data":data.values,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def innodb_buffer_stats_by_table(self,c):
		t = 0
		score = 0
		try:
			sql = "select * from sys.innodb_buffer_stats_by_table;"
			data = pd.read_sql_query(sql,self.conn,)
			#t,score = self._inner_func1(data,c)
			return {"status":True,"data":data.values,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def memory_global_by_current_bytes(self,c):
		t = 0
		score = 0
		try:
			sql = "select * from sys.memory_global_by_current_bytes;"
			data = pd.read_sql_query(sql,self.conn,)
			#t,score = self._inner_func1(data,c)
			return {"status":True,"data":data.values,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def io_by_thread_by_latency(self,c):
		t = 0
		score = 0
		try:
			sql = "select * from sys.io_by_thread_by_latency;"
			data = pd.read_sql_query(sql,self.conn,)
			#t,score = self._inner_func1(data,c)
			return {"status":True,"data":data.values,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def io_global_by_wait_by_latency(self,c):
		t = 0
		score = 0
		try:
			sql = "select * from sys.io_global_by_wait_by_latency;"
			data = pd.read_sql_query(sql,self.conn,)
			#t,score = self._inner_func1(data,c)
			return {"status":True,"data":data.values,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def user_summary_by_file_io(self,c):
		t = 0
		score = 0
		try:
			sql = "select * from sys.user_summary_by_file_io;"
			data = pd.read_sql_query(sql,self.conn,)
			#t,score = self._inner_func1(data,c)
			return {"status":True,"data":data.values,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def io_global_by_file_by_bytes(self,c):
		t = 0
		score = 0
		try:
			sql = "select * from sys.io_global_by_file_by_bytes limit {limit};".format(limit=c['Other'])
			data = pd.read_sql_query(sql,self.conn,)
			#t,score = self._inner_func1(data,c)
			return {"status":True,"data":data.values,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def tmp_table(self,c):
		t = 0
		try:
			statement_analysis = self.statement_analysis['data']
			data = statement_analysis.where(statement_analysis['tmp_tables']>0).dropna(how='all')
			t,score = self._inner_func1(data,c)
			return {"status":True,"data":data.values,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def tmp_file(self,c):
		t = 0
		try:
			statement_analysis = self.statement_analysis['data']
			data = statement_analysis.where(statement_analysis['tmp_disk_tables']>0).dropna(how='all')
			t,score = self._inner_func1(data,c)
			return {"status":True,"data":data.values,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def schema_table_lock_waits(self,c):
		t = 0
		try:
			sql = "select * from sys.schema_table_lock_waits;"
			data = pd.read_sql_query(sql,self.conn,)
			t,score = self._inner_func1(data,c)
			return {"status":True,"data":data.values,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def wait_classes_global_by_latency(self,c):
		t = 0
		score = 0
		try:
			sql = "select * from sys.wait_classes_global_by_latency;"
			data = pd.read_sql_query(sql,self.conn,)
			#t,score = self._inner_func1(data,c)
			return {"status":True,"data":data.values,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def waits_global_by_latency(self,c):
		t = 0
		score = 0
		try:
			sql = "select * from sys.waits_global_by_latency;"
			data = pd.read_sql_query(sql,self.conn,)
			#t,score = self._inner_func1(data,c)
			return {"status":True,"data":data.values,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def innodb_lock_waits(self,c):
		t = 0
		score = 0
		try:
			sql = "select * from sys.innodb_lock_waits;"
			data = pd.read_sql_query(sql,self.conn,)
			t,score = self._inner_func1(data,c)
			return {"status":True,"data":data.values,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def key_buffer_read_hits(self,c):
		t = 0
		score = 0
		try:
			global_status = self.global_status['data'].tail(1)
			Key_read_requests = global_status['Key_read_requests'].values[0]
			Key_reads = global_status['Key_reads'].values[0]
			try:
				read_hits = round((1-Key_reads/Key_read_requests)*100,2)
				if read_hits < c['Error']:
					score = 0 * c['Score']
					t = 2
				elif read_hits < c['Warning']:
					score = 0.3 * c['Score']
					t = 1
				else:
					score = 1 * c['Score']
			except:
				read_hits = -1 #表示未使用MyIsam
				score = c['Score']
			#print('read_hits',read_hits)
			return {"status":True,"data":read_hits,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def key_buffer_write_hits(self,c):
		t = 0
		score = 0
		try:
			global_status = self.global_status['data'].tail(1)
			Key_write_requests = global_status['Key_write_requests'].values[0]
			Key_writes = global_status['Key_writes'].values[0]
			try:
				write_hits = round((1-Key_writes/Key_write_requests)*100,2)
				if write_hits < c['Error']:
					score = 0 * c['Score']
					t = 2
				elif write_hits < c['Warning']:
					score = 0.3 * c['Score']
					t = 1
				else:
					score = 1 * c['Score']
			except:
				write_hits = -1 #表示未使用MyIsam
				score = c['Score']
			return {"status":True,"data":write_hits,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def query_cache_hits(self,c):
		t = 0
		score = 0
		try:
			global_status = self.global_status['data'].tail(1)
			#global_variables = self.global_variables['data'].tail(1)
			try:
				Qcache_hits = global_status['Qcache_hits'].values[0]
				Qcache_inserts = global_status['Qcache_inserts'].values[0]
				q_hits = round(Qcache_hits / (Qcache_hits + Qcache_inserts)*100,2)
				if q_hits < c['Error']:
					score = 0 * c['Score']
					t = 2
				elif q_hits < c['Warning']:
					score = 0.3 * c['Score']
					t = 1
				else:
					score = 1 * c['Score']
			except:
				q_hits = -1
				score = 1 * c['Score']
			return {"status":True,"data":q_hits,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def innodb_buffer_read_hits(self,c):
		t = 0
		score = 0
		try:
			global_status = self.global_status['data'].tail(1)
			Innodb_buffer_pool_reads = int(global_status['Innodb_buffer_pool_reads'].values[0])
			Innodb_buffer_pool_read_requests = int(global_status['Innodb_buffer_pool_read_requests'].values[0])
			Innodb_buffer_pool_read_ahead = int(global_status['Innodb_buffer_pool_read_ahead'].values[0])
			#innodb_read_hits = round((1-Innodb_buffer_pool_reads/(Innodb_buffer_pool_reads+Innodb_buffer_pool_read_requests))*100,2)
			innodb_read_hits = round((1-Innodb_buffer_pool_reads/(Innodb_buffer_pool_reads+Innodb_buffer_pool_read_requests+Innodb_buffer_pool_read_ahead))*100,2)
			if innodb_read_hits < c['Error']:
				score = 0 * c['Score']
				t = 2
			elif innodb_read_hits < c['Warning']:
				score = 0.3 * c['Score']
				t = 1
			else:
				score = 1 * c['Score']
			#print(innodb_read_hits)
			return {"status":True,"data":innodb_read_hits,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def threads_hits(self,c):
		t = 0
		score = 0
		try:
			global_status = self.global_status['data'].tail(1)
			Threads_created = int(global_status['Threads_created'].values[0])
			Connections = int(global_status['Connections'].values[0])
			t_hits = round((1-Threads_created/Connections)*100,2)
			t,score = self._inner_func3(t_hits,c)
			#print(t_hits)
			return {"status":True,"data":t_hits,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def slow_query_ps(self,c):
		t = 0
		score = 0
		try:
			global_status = self.global_status['data'].tail(1)
			Slow_queries = int(global_status['Slow_queries'].values[0])
			Uptime = int(global_status['Uptime'].values[0])
			slow_ps = round(Slow_queries/Uptime,2)
			t,score = self._inner_func4(slow_ps,c)
			return {"status":True,"data":slow_ps,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def table_open_cache_hits(self,c):
		t = 0
		score = 0
		try:
			global_status = self.global_status['data'].tail(1)
			table_open_cache_hits= int(global_status['Table_open_cache_hits'].values[0])
			Table_open_cache_misses = int(global_status['Table_open_cache_misses'].values[0])
			table_hits = round(table_open_cache_hits/(table_open_cache_hits+Table_open_cache_misses)*100,2)
			t,score = self._inner_func3(table_hits,c)
			#print('table_hits',table_hits)
			return {"status":True,"data":table_hits,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def innodb_mem_used(self,c):
		t = 0
		score = 0
		try:
			global_status = self.global_status['data'].tail(1)
			Innodb_buffer_pool_pages_data = int(global_status['Innodb_buffer_pool_pages_data'].values[0])
			Innodb_buffer_pool_pages_total = int(global_status['Innodb_buffer_pool_pages_total'].values[0])
			innodb_mem_used_p = round(Innodb_buffer_pool_pages_data/Innodb_buffer_pool_pages_total*100,2)
			if innodb_mem_used_p > c['Error']:
				t = 2
				score = 0 * c['Score']
			elif innodb_mem_used_p < c['Warning']:
				t = 1
				score = 0.3 * c['Score']
			else:
				score = 1 * c['Score']
			#print(innodb_mem_used_p)
			return {"status":True,"data":innodb_mem_used_p,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def bytes_received_list(self,c):
		t = 0
		score = 0
		try:
			global_status = self.global_status['data']
			global_status['Bytes_received'] = global_status['Bytes_received'].astype('float64')
			t1 = global_status['time_col_0'].iloc[1:].values
			t1 = self.list_int_to_date(t1)
			data = global_status['Bytes_received'].diff(periods=1,).iloc[1:].values
			avg = round(sum(data)/len(data),2)
			return {"status":True,"data":{"time":t1,"data":data,"avg":avg},"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def bytes_sent_list(self,c):
		t = 0
		score = 0
		try:
			global_status = self.global_status['data']
			global_status['Bytes_sent'] = global_status['Bytes_sent'].astype('float64')
			t1 = global_status['time_col_0'].iloc[1:].values
			data = global_status['Bytes_sent'].diff(periods=1,).iloc[1:].values
			avg = round(sum(data)/len(data),2)
			return {"status":True,"data":{"time":t1,"data":data,"avg":avg},"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def conn_used_percent(self,c):
		t = 0
		score = 0
		try:
			global_status = self.global_status['data'].tail(1)
			global_variables = self.global_variables['data'].tail(1)
			Threads_connected = int(global_status['Threads_connected'].values[0])
			max_connections = int(global_variables['max_connections'].values[0])
			conn_p = round(Threads_connected/max_connections*100,2)
			t,score = self._inner_func4(conn_p,c)
			return {"status":True,"data":conn_p,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def innodb_read_write(self,c):
		t = 0
		score = 0
		try:
			global_status = self.global_status['data'].tail(1)
			Innodb_data_read = int(global_status['Innodb_data_read'].values[0])
			Innodb_data_written = int(global_status['Innodb_data_written'].values[0])
			return {"status":True,"data":[Innodb_data_read,Innodb_data_written],"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def innodb_read(self,c):
		t = 0
		score = 0
		try:
			global_status = self.global_status['data']
			global_status['Innodb_data_read'] = global_status['Innodb_data_read'].astype('float64')
			t1 = global_status['time_col_0'].iloc[1:].values
			t1 = self.list_int_to_date(t1)
			data = global_status['Innodb_data_read'].diff(periods=1,).iloc[1:].values
			avg = round(sum(data)/len(data),2)
			return {"status":True,"data":{"time":t1,"data":data,"avg":avg},"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}
		
	def innodb_write(self,c):
		t = 0
		score = 0
		try:
			global_status = self.global_status['data']
			global_status['Innodb_data_written'] = global_status['Innodb_data_written'].astype('float64')
			t1 = global_status['time_col_0'].iloc[1:].values
			t1 = self.list_int_to_date(t1)
			data = global_status['Innodb_data_written'].diff(periods=1,).iloc[1:].values
			avg = round(sum(data)/len(data),2)
			return {"status":True,"data":{"time":t1,"data":data,"avg":avg},"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def redo_log_write(self,c):
		t = 0
		score = 0
		try:
			global_status = self.global_status['data']
			global_status['Innodb_os_log_written'] = global_status['Innodb_os_log_written'].astype('float64')
			t1 = global_status['time_col_0'].iloc[1:].values
			t1 = self.list_int_to_date(t1)
			data = global_status['Innodb_os_log_written'].diff(periods=1,).iloc[1:].values
			avg = round(sum(data)/len(data),2)
			#print(data)
			return {"status":True,"data":{"time":t1,"data":data,"avg":avg},"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def double_write_rate(self,c):
		t = 0
		score = 0
		try:
			global_status = self.global_status['data']
			global_status['Innodb_dblwr_writes'] = global_status['Innodb_dblwr_writes'].astype('float64')
			t1 = global_status['time_col_0'].iloc[1:].values
			t1 = self.list_int_to_date(t1)
			data = global_status['Innodb_dblwr_writes'].diff(periods=1,).iloc[1:].values
			avg = round(sum(data)/len(data),2)
			#print(data)
			return {"status":True,"data":{"time":t1,"data":data,"avg":avg},"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def tps_qps(self,c):
		t = 0
		score = 0
		try:
			global_status = self.global_status['data']
			t1 = global_status['time_col_0'].iloc[1:].values
			t1 = self.list_int_to_date(t1)
			global_status['_commit_rollback'] = global_status['Com_commit'].astype('float64') + global_status['Com_rollback'].astype('float64')
			data1 = global_status['_commit_rollback'].diff(periods=1,).iloc[1:].values
			avg1 = round(sum(data1)/len(data1),2)
			data2 = global_status['Queries'].astype('float64').diff(periods=1,).iloc[1:].values
			avg2 = round(sum(data2)/len(data2),2)
			return {"status":True,"data":{"time":t1,"data1":data1,"data2":data2,"avg1":avg1,"avg2":avg2},"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def slave_info(self,c):
		t = 0
		score = 0
		try:
			sql = "show slave status;"
			data = pd.read_sql_query(sql,self.conn,)
			Slave_IO_Running = data['Slave_IO_Running'].values
			for x in Slave_IO_Running:
				if x == "NO":
					t = 2
					score = 0 * c['Score']
					break
				elif x == 'Connecting':
					t = 1
					score = 0.3 * c['Score']
				else:
					score = 1 * c['Score']
			if data.shape[0] > 0:
				return {"status":True,"data":data.to_dict(),"score":score,"type":t}
			else:
				return {"status":False,"data":"无从库信息","score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def pxc_info(self,c):
		t = 0
		score = 0
		try:
			global_status = self.global_status['data'].tail(1)
			global_variables = self.global_variables['data'].tail(1)

			wsrep_cluster_status = global_status['wsrep_cluster_status'].values[0]
			wsrep_cluster_size = global_status['wsrep_cluster_size'].values[0]
			wsrep_cluster_state_uuid = global_status['wsrep_cluster_state_uuid'].values[0]

			wsrep_connected = global_status['wsrep_connected'].values[0]
			wsrep_ready = global_status['wsrep_ready'].values[0]
			wsrep_local_state_comment = global_status['wsrep_local_state_comment'].values[0]
			wsrep_local_state_uuid = global_status['wsrep_local_state_uuid'].values[0]
			wsrep_provider_vendor = global_status['wsrep_provider_vendor'].values[0]

			if wsrep_connected != "ON" or wsrep_ready != "ON":
				score = 0 * c['Score']
				t = 2
			elif wsrep_local_state_comment != "Synced":
				score = 0.3 * c['Score']
				t = 1
			else:
				score = 1 * c['Score']
			return {"status":False,"data":{"status":global_status,"variables":global_variables},"score":score,"type":t}
		except Exception as e:
			data = "忽略 {obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def mgr_info(self,c):
		t = 0
		score = 0
		try:
			sql1 = "select * from performance_schema.replication_group_members;" #集群节点状态
			sql2 = "select * from performance_schema.replication_group_member_stats;" #自己状态
			data1 = pd.read_sql_query(sql1,self.conn,)
			data2 = pd.read_sql_query(sql2,self.conn,)
			MEMBER_STATE = data1['MEMBER_STATE'].values
			for x in MEMBER_STATE:
				if x == "ERROR":
					t = 2
					score = 0 * c['Score']
					break
				elif x == "ONLINE":
					t = 1
					score = 0.3 * c['Score']
				else:
					score = 1 * c['Score']
			if data2.shape[0] > 0:
				return {"status":True,"data":{"data1":data1.values,"data2":data2.values},"score":score,"type":t}
			else:
				return {"status":False,"data":"无MGR信息","score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def master_info(self,c):
		t = 0
		score = 0
		try:
			sql = "select * from information_schema.processlist where COMMAND = 'Binlog Dump';"
			#后续增加 show slave hosts; -- 5.7      SHOW REPLICAS -- 8.0
			data = pd.read_sql_query(sql,self.conn,)
			if data.shape[0] > 0:
				return {"status":True,"data":data.values,"score":score,"type":t}
			else:
				return {"status":False,"data":"本实例为主库(无从库连接信息)","score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def ndb_info(self,c):
		return {"status":False,"data":"暂不支持"}

	def triggers(self,c):
		t = 0
		score = 0
		try:
			sql = "select * from INFORMATION_SCHEMA.TRIGGERS where TRIGGER_SCHEMA not in ('sys','information_schema','mysql','performance_schema');"
			data = pd.read_sql_query(sql,self.conn,)
			t,score = self._inner_func1(data,c)
			return {"status":True,"data":data.values,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def views(self,c):
		t = 0
		score = 0
		try:
			sql = "select * from information_schema.views where TABLE_SCHEMA not in ('sys','information_schema','mysql','performance_schema');"
			data = pd.read_sql_query(sql,self.conn,)
			t,score = self._inner_func1(data,c)
			return {"status":True,"data":data.values,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def routines(self,c):
		t = 0
		score = 0
		try:
			sql = "select ROUTINE_SCHEMA,ROUTINE_NAME from information_schema.ROUTINES where ROUTINE_SCHEMA not in ('sys','information_schema','mysql','performance_schema');"
			data = pd.read_sql_query(sql,self.conn,)
			t,score = self._inner_func1(data,c)
			return {"status":True,"data":data.values,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def engine_innodb(self,c):
		t = 0
		score = 0
		try:
			sql = "show engine innodb status;"
			data = pd.read_sql_query(sql,self.conn,)
			return {"status":True,"data":data.values,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def engine_tokudb(self,c):
		t = 0
		score = 0
		try:
			sql = "show engine tokudb status;"
			data = pd.read_sql_query(sql,self.conn,)
			return {"status":True,"data":data.values,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def var_default_storage_engine(self,c):
		t = 0
		score = 0
		try:
			global_variables = self.global_variables['data'].tail(1)
			default_storage_engine = global_variables['default_storage_engine'].values[0]
			if default_storage_engine in c['Warning']:
				score = 1 * c['Score']
				return {"status":True,"data":default_storage_engine,"score":score,"type":t}
			else:
				t = 1
				score = 0.3 * c['Score']
				return {"status":True,"data":default_storage_engine,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def var_innodb_flush_log_at_trx_commit(self,c):
		t = 0
		score = 0
		try:
			global_variables = self.global_variables['data'].tail(1)
			var1 = global_variables['innodb_flush_log_at_trx_commit'].values[0]
			if int(var1) == int(c['Warning']):
				score = 1 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
			else:
				t = 1
				score = 0.3 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def var_sync_binlog(self,c):
		t = 0
		score = 0
		try:
			global_variables = self.global_variables['data'].tail(1)
			var1 = global_variables['sync_binlog'].values[0]
			if int(var1) == int(c['Warning']):
				score = 1 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
			else:
				t = 1
				score = 0.3 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def var_general_log(self,c):
		t = 0
		score = 0
		try:
			global_variables = self.global_variables['data'].tail(1)
			var1 = global_variables['general_log'].values[0]
			if str(var1) == str(c['Warning']):
				score = 1 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
			else:
				t = 1
				score = 0.3 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def var_slow_query_log(self,c):
		t = 0
		score = 0
		try:
			global_variables = self.global_variables['data'].tail(1)
			var1 = global_variables['slow_query_log'].values[0]
			if str(var1) == str(c['Warning']):
				score = 1 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
			else:
				t = 1
				score = 0.3 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def var_log_bin(self,c):
		t = 0
		score = 0
		try:
			global_variables = self.global_variables['data'].tail(1)
			var1 = global_variables['log_bin'].values[0]
			if str(var1) == str(c['Warning']):
				score = 1 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
			else:
				t = 1
				score = 0.3 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def var_qcache(self,c):
		t = 0
		score = 0
		try:
			global_status = self.global_status['data'].tail(1)
			var1 = global_status['Qcache_queries_in_cache'].values[0]
			if int(var1) == 0:
				score = 1 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
			else:
				t = 1
				score = 0.7 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def var_transaction_isolation(self,c):
		t = 0
		score = 0
		try:
			global_variables = self.global_variables['data'].tail(1)
			var1 = global_variables['transaction_isolation'].values[0]
			if var1 in c['Warning']:
				score = 1 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
			else:
				t = 1
				score = 0.3 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def var_innodb_buffer_pool_size(self,c):
		t = 0
		score = 0
		try:
			global_variables = self.global_variables['data'].tail(1)
			var1 = global_variables['innodb_buffer_pool_size'].values[0]
			if int(var1) > int(c['Warning']):
				score = 1 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
			else:
				t = 1
				score = 0.3 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def var_innodb_lru_scan_depth(self,c):
		t = 0
		score = 0
		try:
			global_variables = self.global_variables['data'].tail(1)
			var1 = global_variables['innodb_lru_scan_depth'].values[0]
			return {"status":True,"data":var1,"score":c['Score'],"type":t}
			if int(var1) > int(c['Warning']):
				score = 1 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
			else:
				t = 1
				score = 0.3 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def var_max_allowed_packet(self,c):
		t = 0
		score = 0
		try:
			global_variables = self.global_variables['data'].tail(1)
			var1 = global_variables['max_allowed_packet'].values[0]
			if int(var1) >= int(c['Warning']):
				score = 1 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
			else:
				t = 1
				score = 0.3 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def var_server_id(self,c):
		t = 0
		score = 0
		try:
			global_variables = self.global_variables['data'].tail(1)
			var1 = global_variables['server_id'].values[0]
			if int(var1) >= int(c['Warning']):
				score = 1 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
			else:
				t = 1
				score = 0.8 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def var_innodb_log_file_size(self,c):
		t = 0
		score = 0
		try:
			global_variables = self.global_variables['data'].tail(1)
			var1 = global_variables['innodb_log_file_size'].values[0]
			if int(var1) >= int(c['Warning']):
				score = 1 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
			else:
				t = 1
				score = 0.4 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def var_innodb_log_files_in_group(self,c):
		t = 0
		score = 0
		try:
			global_variables = self.global_variables['data'].tail(1)
			var1 = global_variables['innodb_log_files_in_group'].values[0]
			if int(var1) >= int(c['Warning']):
				score = 1 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
			else:
				t = 1
				score = 0.4 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def var_innodb_page_size(self,c):
		t = 0
		score = 0
		try:
			global_variables = self.global_variables['data'].tail(1)
			var1 = global_variables['innodb_page_size'].values[0]
			if int(var1) >= int(c['Warning']):
				score = 1 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
			else:
				t = 1
				score = 0.3 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def var_innodb_doublewrite(self,c):
		t = 0
		score = 0
		try:
			global_variables = self.global_variables['data'].tail(1)
			var1 = global_variables['innodb_doublewrite'].values[0]
			if str(var1) == str(c['Warning']):
				score = 1 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
			else:
				t = 1
				score = 0.3 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def var_gtid_mode(self,c):
		t = 0
		score = 0
		try:
			global_variables = self.global_variables['data'].tail(1)
			var1 = global_variables['gtid_mode'].values[0]
			if var1 in c['Warning']:
				score = 1 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
			else:
				t = 1
				score = 0.3 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def var_performance_schema(self,c):
		t = 0
		score = 0
		try:
			global_variables = self.global_variables['data'].tail(1)
			var1 = global_variables['performance_schema'].values[0]
			if str(var1) == str(c['Warning']):
				score = 1 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
			else:
				t = 1
				score = 0.3 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def var_character_set_database(self,c):
		t = 0
		score = 0
		try:
			global_variables = self.global_variables['data'].tail(1)
			var1 = global_variables['character_set_database'].values[0]
			if var1 in str(c['Warning']):
				score = 1 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
			else:
				t = 1
				score = 0.3 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def var_binlog_format(self,c):
		t = 0
		score = 0
		try:
			global_variables = self.global_variables['data'].tail(1)
			var1 = global_variables['binlog_format'].values[0]
			if str(var1) == str(c['Warning']):
				score = 1 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
			else:
				t = 1
				score = 0.3 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def var_binlog_row_image(self,c):
		t = 0
		score = 0
		try:
			global_variables = self.global_variables['data'].tail(1)
			var1 = global_variables['binlog_row_image'].values[0]
			if str(var1) == str(c['Warning']):
				score = 1 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
			else:
				t = 1
				score = 0.3 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def var_max_connections(self,c):
		t = 0
		score = 0
		try:
			global_variables = self.global_variables['data'].tail(1)
			var1 = global_variables['max_connections'].values[0]
			if int(var1) >= int(c['Warning']):
				score = 1 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
			else:
				t = 1
				score = 0.8 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def var_innodb_io_capacity(self,c):
		t = 0
		score = 0
		try:
			global_variables = self.global_variables['data'].tail(1)
			var1 = global_variables['innodb_io_capacity'].values[0]
			if int(var1) >= int(c['Warning']):
				score = 1 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
			else:
				t = 1
				score = 0.8 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def var_innodb_io_capacity_max(self,c):
		t = 0
		score = 0
		try:
			global_variables = self.global_variables['data'].tail(1)
			var1 = global_variables['innodb_io_capacity_max'].values[0]
			if int(var1) >= int(c['Warning']):
				score = 1 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
			else:
				t = 1
				score = 0.8 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def var_innodb_log_buffer_size(self,c):
		t = 0
		score = 0
		try:
			global_variables = self.global_variables['data'].tail(1)
			var1 = global_variables['innodb_log_buffer_size'].values[0]
			sql = "select event_name,avg_written from sys.x$io_global_by_wait_by_latency where event_name = 'innodb/innodb_log_file'"
			data = pd.read_sql_query(sql,self.conn,)
			if float(var1) >= float(c['Warning']) * float(data['avg_written'].values[0]):
				score = 1 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
			else:
				t = 1
				score = 0.4 * c['Score']
				return {"status":True,"data":var1,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def error_log(self,c):
		t = 0
		score = 0
		try:
			global_variables = self.global_variables['data'].tail(1)
			if global_variables['version'].values[0] > '8.0':
				sql = "select * from performance_schema.error_log where PRIO = 'Error' and LOGGED > DATE_SUB(current_timestamp(), INTERVAL {days} DAY);".format(days=c['Other'])
				data = pd.read_sql_query(sql,self.conn,)
				t,score = self._inner_func1(data,c)
				return {"status":True,"data":data.values,"score":score,"type":t}
			else:
				return {"status":False,"data":"{obj} 仅8.0才支持".format(obj=c['Object_name'],),"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def schema_object_overview(self,c):
		t = 0
		score = 0
		try:
			sql = "select * from sys.schema_object_overview where db not in ('information_schema','mysql','performance_schema','sys');"
			data = pd.read_sql_query(sql,self.conn,)
			return {"status":True,"data":data.values,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def memory_global_total(self,c):
		t = 0
		score = 0
		try:
			sql = "select * from sys.memory_global_total;"
			data = pd.read_sql_query(sql,self.conn,)
			return {"status":True,"data":data.values,"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}

	def com_sql(self,c):
		t = 0
		score = 0
		try:
			global_status = self.global_status['data']
			global_status['Com_select'] = global_status['Com_select'].astype('float64')
			global_status['Com_delete'] = global_status['Com_delete'].astype('float64')
			global_status['Com_update'] = global_status['Com_update'].astype('float64')
			global_status['Com_insert'] = global_status['Com_insert'].astype('float64')
			t1 = global_status['time_col_0'].iloc[1:].values
			t1=  self.list_int_to_date(t1)
			data1 = global_status['Com_select'].diff(periods=1,).iloc[1:].values
			data2 = global_status['Com_delete'].diff(periods=1,).iloc[1:].values
			data3 = global_status['Com_update'].diff(periods=1,).iloc[1:].values
			data4 = global_status['Com_insert'].diff(periods=1,).iloc[1:].values
			#avg = sum(data)/len(data)
			#print(data)
			return {"status":True,"data":{"time":t1,"data1":data1,"data2":data2,"data3":data3,"data4":data4,},"score":score,"type":t}
		except Exception as e:
			data = "{obj}: {e}".format(obj=c['Object_name'],e=str(e))
			return {"status":False,"data":data,"score":0}
