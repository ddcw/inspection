import pandas as pd
import time
class init_data:
	def __init__(self,conn):
		self.conn = conn

	def global_status(self,data_collection_time,data_collection_interval):
		sql = "show global status;"
		try:
			time_col_0 = []
			data = pd.read_sql_query(sql,self.conn,index_col='Variable_name').T
			time_col_0.append(int(time.time()))
			time.sleep(data_collection_interval)
			runtime = data_collection_interval
			while runtime < data_collection_time:
				data = data.append(pd.read_sql_query(sql,self.conn,index_col='Variable_name').T)
				time_col_0.append(int(time.time()))
				time.sleep(data_collection_interval)
				runtime += data_collection_interval

			data.insert(0,'time_col_0',time_col_0)
			#不做计算, 为了兼容脚本采集的数据
			return {"status":True,"data":data}
		except Exception as e:
			return {"status":False,"data":e}

	def run_sql(self,sql):
		try:
			data = pd.read_sql_query(sql,self.conn,)
			return {"status":True,"data":data}
		except Exception as e:
			return {"status":False,"data":e}


	def run_sql2(self,sql):
		try:
			data = pd.read_sql_query(sql,self.conn,index_col='Variable_name').T
			return {"status":True,"data":data}
		except Exception as e:
			return {"status":False,"data":e}


