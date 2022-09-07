import pandas as pd
class anadata1:
	def __init__(self,*args,**kwargs):
		try:
			self.conn= kwargs['conn']
		except:
			pass
		try:
			self.global_conf= kwargs['global_conf']
		except:
			pass
		try:
			self.data2= kwargs['data2']
		except:
			pass

	def __inner_function_1(self,condition,data):
		if data['status']:
			data = data['data']
			c_flag = 1
			s_flag = 1
			if 'count' in condition:
				c_flag = 1 if data.shape[0]  >= condition['count'] else 0

			if 'size' in condition:
				s_flag = 1 if data[condition['size']['col']] >= condition['size']['data'] else 0
		
				
			if c_flag  == 1 and s_flag == 1:
				return True
			else:
				return False
		else:
			return False

	def __inner_function_2(self,condition,data):
		if data['status']:
			data = data['data']
			c_flag = 1
			if 'value' in condition:
				c_flag = 1 if str(data.values[0][0]) in condition['value'] else 0

				
			if c_flag  == 1 :
				return True
			else:
				return False
		else:
			return False

	def __inner_function_3(self,condition,data,name):
		if data['status']:
			data = data['data']
			c_flag = 1
			if 'value' in condition:
				for x in data[name].values:
					if x in condition['value']:
						return True
			return False
		else:
			return False

	def __inner_function_4(self,condition,data,):
		if data['status']:
			data = data['data']
			if 'min' in condition:
				if int(data.values[0][0]) < int(condition['min']):
					return False

			if 'max' in condition:
				if int(data.values[0][0]) > int(condition['max']):
					return False
			return True
		else:
			return False

	def __inner_score(self,l,c):
		#懒得写, 后面再写
		default_score = self.global_conf['OTHER']['default_score']
		score = c['score'] * (1 - default_score[l])
		des = c['des']
		suggestion = c['suggestion'] if 'suggestion' in c and l>0 else ''
		status = True
		for l1 in c['level']:
			if l == l1['level']:
				if 'des' in l1:
					des = l1['des']
				if 'suggestion' in l1:
					suggestion = l1['suggestion']
		return {'status':status,'object_name':c['object_name'],'type':c['type'],'level':l,'score':score,'old_score':c['score'],'level_des':des,'des':c['des'],'suggestion':suggestion}

	def no_primary_key(self,c,data):
		current_level = 1
		for l in c['level']:
			if self.__inner_function_1(l['condition'],data):
				current_level = l['level'] if l['level'] >= current_level else current_level
		return self.__inner_score(current_level,c)


	def redundant_indexes(self,c,data):
		current_level = 1
		for l in c['level']:
			if self.__inner_function_1(l['condition'],data):
				current_level = l['level'] if l['level'] >= current_level else current_level
		return self.__inner_score(current_level,c)


	def unused_indexes(self,c,data):
		current_level = 1
		for l in c['level']:
			if self.__inner_function_1(l['condition'],data):
				current_level = l['level'] if l['level'] >= current_level else current_level
		return self.__inner_score(current_level,c)


	def full_table_scans(self,c,data):
		current_level = 1
		for l in c['level']:
			if self.__inner_function_1(l['condition'],data):
				current_level = l['level'] if l['level'] >= current_level else current_level
		return self.__inner_score(current_level,c)

	def auto_increment_columns(self,c,data):
		current_level = 1
		for l in c['level']:
			if self.__inner_function_1(l['condition'],data):
				current_level = l['level'] if l['level'] >= current_level else current_level
		return self.__inner_score(current_level,c)

	def log_bin(self,c,data):
		current_level = 1
		for l in c['level']:
			if self.__inner_function_2(l['condition'],data):
				current_level = l['level'] if l['level'] >= current_level else current_level
		return self.__inner_score(current_level,c)

	def special_column(self,c,data):
		current_level = 1
		for l in c['level']:
			if self.__inner_function_1(l['condition'],data):
				current_level = l['level'] if l['level'] >= current_level else current_level
		return self.__inner_score(current_level,c)

	def big_table(self,c,data):
		current_level = 1
		for l in c['level']:
			if self.__inner_function_1(l['condition'],data):
				current_level = l['level'] if l['level'] >= current_level else current_level
		return self.__inner_score(current_level,c)

	def cold_table(self,c,data):
		current_level = 1
		for l in c['level']:
			if self.__inner_function_1(l['condition'],data):
				current_level = l['level'] if l['level'] >= current_level else current_level
		return self.__inner_score(current_level,c)

	def partition_table(self,c,data):
		current_level = 1
		for l in c['level']:
			if self.__inner_function_1(l['condition'],data):
				current_level = l['level'] if l['level'] >= current_level else current_level
		return self.__inner_score(current_level,c)

	def is_nullable(self,c,data):
		current_level = 1
		for l in c['level']:
			if self.__inner_function_1(l['condition'],data):
				current_level = l['level'] if l['level'] >= current_level else current_level
		return self.__inner_score(current_level,c)

	def no_innodb_table(self,c,data):
		current_level = 1
		for l in c['level']:
			if self.__inner_function_1(l['condition'],data):
				current_level = l['level'] if l['level'] >= current_level else current_level
		return self.__inner_score(current_level,c)

	def table_static_expired(self,c,data):
		current_level = 1
		for l in c['level']:
			if self.__inner_function_1(l['condition'],data):
				current_level = l['level'] if l['level'] >= current_level else current_level
		return self.__inner_score(current_level,c)

	def fragment_table(self,c,data):
		current_level = 1
		for l in c['level']:
			if self.__inner_function_1(l['condition'],data):
				current_level = l['level'] if l['level'] >= current_level else current_level
		return self.__inner_score(current_level,c)

	def same_user_password(self,c,data):
		current_level = 1
		for l in c['level']:
			if self.__inner_function_1(l['condition'],data):
				current_level = l['level'] if l['level'] >= current_level else current_level
		return self.__inner_score(current_level,c)

	def expired_password(self,c,data):
		current_level = 1
		for l in c['level']:
			if self.__inner_function_1(l['condition'],data):
				current_level = l['level'] if l['level'] >= current_level else current_level
		return self.__inner_score(current_level,c)

	def any_host(self,c,data):
		current_level = 1
		for l in c['level']:
			if self.__inner_function_1(l['condition'],data):
				current_level = l['level'] if l['level'] >= current_level else current_level
		return self.__inner_score(current_level,c)

	def simple_password(self,c,data):
		password_list = ""
		simple_password_list = []
		try:
			with open(self.global_conf['MYSQL']['dict_passowrd'],'r') as f:
				password_list = f.read().rstrip().split('\n')
			for x in password_list:
				sql = "SELECT CONCAT(user, '@', host) FROM mysql.user where authentication_string = CONCAT('*', UPPER(SHA1(UNHEX(SHA1('{password}')))))".format(password=x) #5.7.5之后不支持password函数
				rs = pd.read_sql_query(sql,self.conn,)
				for y in rs.values:
					simple_password_list.append(y[0])
			data = {'status':True,'data':pd.DataFrame(simple_password_list)}
		except Exception as e:
			print(e)
			pass
		current_level = 1
		for l in c['level']:
			if self.__inner_function_1(l['condition'],data):
				current_level = l['level'] if l['level'] >= current_level else current_level
		returndata = self.__inner_score(current_level,c)
		returndata['data'] = data['data']
		returndata['data_rows'] = data['data'].shape[0]
		return returndata

	def innodb_buffer_stats_by_schema(self,c,data):
		current_level = 0
		for l in c['level']:
			if self.__inner_function_2(l['condition'],data):
				current_level = l['level'] if l['level'] >= current_level else current_level
		return self.__inner_score(current_level,c)

	def schema_object_overview(self,c,data):
		current_level = 0
		for l in c['level']:
			if self.__inner_function_2(l['condition'],data):
				current_level = l['level'] if l['level'] >= current_level else current_level
		return self.__inner_score(current_level,c)

	def memory_global_by_current_bytes(self,c,data):
		current_level = 0
		for l in c['level']:
			if self.__inner_function_2(l['condition'],data):
				current_level = l['level'] if l['level'] >= current_level else current_level
		return self.__inner_score(current_level,c)

	def io_global_by_wait_by_latency(self,c,data):
		current_level = 0
		for l in c['level']:
			if self.__inner_function_2(l['condition'],data):
				current_level = l['level'] if l['level'] >= current_level else current_level
		return self.__inner_score(current_level,c)

	def waits_global_by_latency(self,c,data):
		current_level = 0
		for l in c['level']:
			if self.__inner_function_2(l['condition'],data):
				current_level = l['level'] if l['level'] >= current_level else current_level
		return self.__inner_score(current_level,c)

	def schema_table_lock_waits(self,c,data):
		current_level = 1
		for l in c['level']:
			if self.__inner_function_1(l['condition'],data):
				current_level = l['level'] if l['level'] >= current_level else current_level
		return self.__inner_score(current_level,c)

	def innodb_lock_waits(self,c,data):
		current_level = 1
		for l in c['level']:
			if self.__inner_function_1(l['condition'],data):
				current_level = l['level'] if l['level'] >= current_level else current_level
		return self.__inner_score(current_level,c)

	def master_info(self,c,data):
		current_level = 1
		for l in c['level']:
			if self.__inner_function_1(l['condition'],data):
				current_level = l['level'] if l['level'] >= current_level else current_level
		return self.__inner_score(current_level,c)

	def slave_info(self,c,data):
		data = self.data2['slave_status']
		current_level = 1
		for l in c['level']:
			if self.__inner_function_3(l['condition'],data,'Slave_IO_Running'):
				current_level = l['level'] if l['level'] >= current_level else current_level
			if self.__inner_function_3(l['condition'],data,'Slave_SQL_Running'):
				current_level = l['level'] if l['level'] >= current_level else current_level
		returndata = self.__inner_score(current_level,c)
		returndata['data'] = data['data'][['Slave_IO_State','Master_Host','Master_Port','Slave_IO_Running','Slave_SQL_Running','Last_IO_Error','Slave_SQL_Running_State','Retrieved_Gtid_Set','Executed_Gtid_Set','Master_Bind']]
		returndata['data_rows'] = data['data'].shape[0]
		return returndata

	def pxc_info(self,c,data):
		current_level = 1
		status = self.data2['global_status']['data']
		variables = self.data2['global_variables']['data']
		data = {}
		data['status'] = True
		try:
			data['data'] = pd.concat([status[['wsrep_cluster_status','wsrep_cluster_size','wsrep_connected','wsrep_ready','wsrep_replicated_bytes','wsrep_received_bytes']],variables[['wsrep_node_address','wsrep_cluster_name','wsrep_cluster_address']]],axis=1)
			for l in c['level']:
				if self.__inner_function_3(l['condition'],data,'wsrep_connected'):
					current_level = l['level'] if l['level'] >= current_level else current_level
				if self.__inner_function_3(l['condition'],data,'wsrep_ready'):
					current_level = l['level'] if l['level'] >= current_level else current_level
			returndata = self.__inner_score(current_level,c)
			returndata['data'] = data['data']
			returndata['data_rows'] = data['data'].shape[0]
			return returndata

		except Exception as e:
			#print(e)
			return {'status':False,'data':''}

	def mgr_info(self,c,data):
		data = self.data2['performance_schema.replication_group_members']
		variables = self.data2['global_variables']['data']
		try:
			data['data'].insert(0,'group_replication_group_name',variables['group_replication_group_name'].values[0])
			data['data'].insert(0,'group_replication_group_seeds',variables['group_replication_group_seeds'].values[0])
		except:
			pass
		current_level = 1
		for l in c['level']:
			if self.__inner_function_3(l['condition'],data,'MEMBER_STATE'):
				current_level = l['level'] if l['level'] >= current_level else current_level
		returndata = self.__inner_score(current_level,c)
		returndata['data'] = data['data']
		returndata['data_rows'] = data['data'].shape[0]
		return returndata

	def default_storage_engine(self,c,data):
		current_level = 3
		for l in c['level']:
			if self.__inner_function_2(l['condition'],data):
				current_level = l['level'] if l['level'] <= current_level else current_level
		return self.__inner_score(current_level,c)

	def innodb_flush_log_at_trx_commit(self,c,data):
		current_level = 3
		for l in c['level']:
			if self.__inner_function_2(l['condition'],data):
				current_level = l['level'] if l['level'] <= current_level else current_level
		return self.__inner_score(current_level,c)

	def sync_binlog(self,c,data):
		current_level = 3
		for l in c['level']:
			if self.__inner_function_2(l['condition'],data):
				current_level = l['level'] if l['level'] <= current_level else current_level
		return self.__inner_score(current_level,c)

	def general_log(self,c,data):
		current_level = 3
		for l in c['level']:
			if self.__inner_function_2(l['condition'],data):
				current_level = l['level'] if l['level'] <= current_level else current_level
		return self.__inner_score(current_level,c)

	def slow_query_log(self,c,data):
		current_level = 3
		for l in c['level']:
			if self.__inner_function_2(l['condition'],data):
				current_level = l['level'] if l['level'] <= current_level else current_level
		return self.__inner_score(current_level,c)

	def transaction_isolation(self,c,data):
		current_level = 3
		for l in c['level']:
			if self.__inner_function_2(l['condition'],data):
				current_level = l['level'] if l['level'] <= current_level else current_level
		return self.__inner_score(current_level,c)


	def innodb_buffer_pool_size(self,c,data):
		current_level = 3
		for l in c['level']:
			if self.__inner_function_4(l['condition'],data):
				current_level = l['level'] if l['level'] <= current_level else current_level
		return self.__inner_score(current_level,c)


	def server_id(self,c,data):
		current_level = 0
		for l in c['level']:
			if self.__inner_function_2(l['condition'],data):
				current_level = l['level'] if l['level'] >= current_level else current_level
		return self.__inner_score(current_level,c)

	def innodb_log_file_size(self,c,data):
		current_level = 2
		for l in c['level']:
			if self.__inner_function_4(l['condition'],data):
				current_level = l['level'] if l['level'] <= current_level else current_level
		return self.__inner_score(current_level,c)


	def innodb_log_files_in_group(self,c,data):
		current_level = 2
		for l in c['level']:
			if self.__inner_function_4(l['condition'],data):
				current_level = l['level'] if l['level'] <= current_level else current_level
		return self.__inner_score(current_level,c)


	def innodb_page_size(self,c,data):
		current_level = 4
		for l in c['level']:
			if self.__inner_function_2(l['condition'],data):
				current_level = l['level'] if l['level'] <= current_level else current_level
		return self.__inner_score(current_level,c)

	def innodb_doublewrite(self,c,data):
		current_level = 2
		for l in c['level']:
			if self.__inner_function_2(l['condition'],data):
				current_level = l['level'] if l['level'] <= current_level else current_level
		return self.__inner_score(current_level,c)

	def gtid_mode(self,c,data):
		current_level = 4
		for l in c['level']:
			if self.__inner_function_2(l['condition'],data):
				current_level = l['level'] if l['level'] <= current_level else current_level
		return self.__inner_score(current_level,c)

	def performance_schema(self,c,data):
		current_level = 3
		for l in c['level']:
			if self.__inner_function_2(l['condition'],data):
				current_level = l['level'] if l['level'] <= current_level else current_level
		return self.__inner_score(current_level,c)

	def binlog_format(self,c,data):
		current_level = 4
		for l in c['level']:
			if self.__inner_function_2(l['condition'],data):
				current_level = l['level'] if l['level'] <= current_level else current_level
		return self.__inner_score(current_level,c)

	def binlog_row_image(self,c,data):
		current_level = 3
		for l in c['level']:
			if self.__inner_function_2(l['condition'],data):
				current_level = l['level'] if l['level'] <= current_level else current_level
		return self.__inner_score(current_level,c)

	def max_connections(self,c,data):
		current_level = 2
		for l in c['level']:
			if self.__inner_function_4(l['condition'],data):
				current_level = l['level'] if l['level'] <= current_level else current_level
		return self.__inner_score(current_level,c)

	def innodb_io_capacity(self,c,data):
		current_level = 3
		for l in c['level']:
			if self.__inner_function_4(l['condition'],data):
				current_level = l['level'] if l['level'] <= current_level else current_level
		return self.__inner_score(current_level,c)

	def innodb_io_capacity_max(self,c,data):
		current_level = 3
		for l in c['level']:
			if self.__inner_function_4(l['condition'],data):
				current_level = l['level'] if l['level'] <= current_level else current_level
		return self.__inner_score(current_level,c)

	def innodb_log_buffer_size(self,c,data):
		current_level = 3
		for l in c['level']:
			if self.__inner_function_4(l['condition'],data):
				current_level = l['level'] if l['level'] <= current_level else current_level
		return self.__inner_score(current_level,c)

