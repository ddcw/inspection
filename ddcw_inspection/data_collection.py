# -*- coding: utf-8 -*-

#from . import collection_detail
import time
import json

class get_data:
	def __init__(self,*args,**kwargs):
		try:
			self.shell = kwargs["shell"]
		except:
			self.shell = None
		try:
			self.sql = kwargs["sql"]
		except:
			self.sql = None
			return False
		try:
			self.table_list = kwargs["table_list"]
			self.db_comm = kwargs["db_comm"]
		except:
			self.table_list = None
			self.db_comm = None
			return False

		#设置基本数据
		data = {}
		data["HOSTINFO"] = {} #主机信息
		data["DBINFO"] = {} #数据库信息
		data["INFO"] = {}  #基本信息, 比如巡检版本之类的
		data["INFO"]["VERSION"] = "1.0" #定义版本
		data["INFO"]["DBTYPE"] = "Mysql" 
		data["INFO"]["START_TIME"] = time.strftime('%Y%m%d_%H%M%S', time.localtime())
		data["INFO"]["END_TIME"] = ""
		data["INFO"]["AUTHOR"] = "ddcw"
		self.data = data


	#先采集数据库信息, 再采集主机信息.  先采集主机信息的话, 部分数据库在主机上的信息就不会采集...:w
	def get_host(self):
		shell_execute = self.shell

		if shell_execute is None:
			self.data["HOSTINFO"] = {"HAVEDATA":False}
			return

		sql_execute = self.sql
		variables = self.data["DBINFO"]["comm"]["variables"]
		hostinfo = {}
		hostinfo["HAVEDATA"] = True
		hostinfo["ostype"] = shell_execute.get_result_dict("cat /proc/sys/kernel/ostype")
		hostinfo["oslike"] = shell_execute.get_result_dict("""grep '^ID_LIKE=' /etc/os-release  | awk -F =  '{print $2}' | sed 's/\"//g' | awk '{print $1}'""")
		hostinfo["osname"] = shell_execute.get_result_dict("""grep "^NAME=" /etc/os-release  | awk -F = '{print $2}' | sed 's/\"//g'""")
		hostinfo["hostname"] = shell_execute.get_result_dict("cat /proc/sys/kernel/hostname")
		hostinfo["platform"] = shell_execute.get_result_dict("uname -m")
		hostinfo["kernel"] = shell_execute.get_result_dict("uname -r")
		hostinfo["cpu_socket"] = shell_execute.get_result_dict("lscpu | grep 'Socket(s)' | awk '{print $NF}'")
		hostinfo["cpu_core"] = shell_execute.get_result_dict("lscpu | grep 'Core(s)' | awk '{print $NF}'")
		hostinfo["cpu_thread"] = shell_execute.get_result_dict("lscpu | grep 'Thread(s)' | awk '{print $NF}'")
		hostinfo["uptime"] = shell_execute.get_result_dict("cat /proc/uptime") # 开机总时间  总空闲时间(除以cpu线程数才是单个cpu的)
		hostinfo["interrupts"] = shell_execute.get_result_dict("cat /proc/interrupts") # 系统中断 详情:https://www.kernel.org/doc/html/latest/filesystems/proc.html
		hostinfo["meminfo"] = shell_execute.get_result_dict("cat /proc/meminfo")
		hostinfo["swappiness"] = shell_execute.get_result_dict("cat /proc/sys/vm/swappiness")
		hostinfo["df"] = shell_execute.get_result_dict("df -PT | tail -n +2")
		hostinfo["pvs"] = shell_execute.get_result_dict("pvs | tail -n +2")
		hostinfo["lsblk"] = shell_execute.get_result_dict("lsblk -d -o NAME,rota | tail -n +2")
		hostinfo["timezone"] = shell_execute.get_result_dict("ls -l /etc/localtime | awk -F /zoneinfo/ '{print $NF}'")
		hostinfo["tcp"] = shell_execute.get_result_dict("wc -l /proc/net/tcp | awk '{print $1-1}'")
		hostinfo["loadavg"] = shell_execute.get_result_dict("cat /proc/loadavg")
		hostinfo["dmesg"] = shell_execute.get_result_dict("dmesg -T | grep -iE ' error | kill | oom | out of memory '")

		mysqlinfo = {}

		#数据库目录 其实可以从self.data["DBINFO"]["comm"]["variables"]里面找信息的, 但是就必须得先使用get_db了. 于是就在获取一遍吧...
		def get_df_dir(test_dir):
			tmp_dict = sql_execute.get_result_dict("show variables like '{test_dir}'".format(test_dir=test_dir))
			if tmp_dict["istrue"]:
				test = tmp_dict["data"][0][1]
				test_comm = shell_execute.get_result_dict("df -PT {test} | tail -n +2".format(test=test, ))
				if test_comm["code"] == 0 and test_comm["stderr"] == "":
					return test_comm["stdout"]
			return ""
		mysqlinfo["datadir"] = get_df_dir("datadir")
		mysqlinfo["log_bin_index"] = get_df_dir("log_bin_index")
		#hostinfo["mysqlinfo"]["log_bin_index"] = get_df_dir("log_bin_index")

		#根据变量 返回一个对应的绝对路径
		def get_dir(var):
			var_dict = sql_execute.get_result_dict("show variables like '{var}'".format(var=var))
			if var_dict["istrue"]:
				var_dir = var_dict["data"][0][1]
				if var_dir[0] == "/":
					dir_exist = shell_execute.get_result_dict("ls {var_dir}".format(var_dir=var_dir))
					if dir_exist["code"] == 0 and dir_exist["stderr"] == "":
						return var_dir
					else:
						return ""
				else:
					datadir = sql_execute.get_result_dict("show variables like 'datadir'")["data"][0][1]
					var_dir = str(datadir) + str(var_dir)
					dir_exist = shell_execute.get_result_dict("ls {var_dir}".format(var_dir=var_dir))
					if dir_exist["code"] == 0 and dir_exist["stderr"] == "":
						return var_dir
					else:
						return ""
			return ""

		#日志采集: 慢日志 和 错误日志
		#获取慢日志路径和错误日志路径
		slow_log_dir = get_dir("slow_query_log_file")
		error_log_dir = get_dir("log_error")
		#判断是否有pt-query-digest工具
		HAVE_PT = False
		pt_test = shell_execute.get_result_dict("pt-query-digest --help")

		#慢日志
		if pt_test["code"] == 0 and pt_test["stderr"] == "":
			HAVE_PT = True
		if HAVE_PT and slow_log_dir != "":
			slow_log_dict = shell_execute.get_result_dict("pt-query-digest {slow_log} --output json".format(slow_log=slow_log_dir))
		else:
			slow_log_dict = shell_execute.get_result_dict("tail -500 {slow_log}".format(slow_log=slow_log_dir))
		if slow_log_dict["code"] == 0 and slow_log_dict["stderr"] == "":
			mysqlinfo["slow_log"] = {"have_pt":HAVE_PT, "data":slow_log_dict["stdout"], "status":True}
		else:
			mysqlinfo["slow_log"] = {"have_pt":HAVE_PT, "data":slow_log_dict["stdout"], "status":False}
			
		#错误日志
		error_log_dict = shell_execute.get_result_dict("tail -500 {error_log_dir}".format(error_log_dir=error_log_dir, ))
		if error_log_dict["code"] == 0 or error_log_dict["stderr"] == "": #这里有个BUG, subprocess 用tail取mysql8.0的错误日志的时候, 会超时..... 所以把and改为了or
			mysqlinfo["error_log"] = {"have_data":True, "data":error_log_dict["stdout"], "status":True}
		else:
			mysqlinfo["error_log"] = {"have_data":False, "data":error_log_dict["stderr"], "status":False}


		#BINLOG增长量判断
		binlog_index = sql_execute.get_result_dict("show variables like 'log_bin_index'")
		if binlog_index["istrue"]:
			binlog_stat_shell_comm = r'''for x in $(cat ''' + str(binlog_index["data"][0][1]) + r''');do aa=$(stat $x |  awk '{if ($1=="Modify:")print $2}'); bb=$(stat $x |  awk '{if ($1=="Size:")print $2}'); echo $aa $bb ;done;''' #注: 字符串太长了, 用format格式化会报错, 还是老老实实的字符串拼接吧....
			binlog_stat = shell_execute.get_result_dict(binlog_stat_shell_comm)
			mysqlinfo["binlog_stat"] = {"have_data":True, "data":binlog_stat["stdout"], "status":True}
		else:
			mysqlinfo["binlog_stat"] = {"have_data":False, "data":binlog_stat["stderr"], "status":False}
		

		hostinfo["mysqlinfo"] = {"code":0, "stdout":mysqlinfo, "stderr":""}
		
		self.data["HOSTINFO"] = hostinfo
		


	def get_mysql(self):
		data = {}
		data["table"] = {}
		data["comm"] = {}
		data["HAVEDATA"] = True
		sql_execute = self.sql
		table_list = self.table_list
		
		#表信息采集
		for x in table_list:
			try:
				table = x["table"]
			except:
				continue
			try:
				only_rows = x["only_rows"]
			except:
				only_rows = None
			try:
				exclude_rows = x["exclude_rows"]
			except:
				exclude_rows = ""
			try:
				where = x["where"]
			except:
				where = ""
			try:
				sql = x["sql"]
			except:
				sql = None
			#获取表结构,和查询sql
			table_name = table.split(".")[1]
			table_schema = table.split(".")[0]
			rows = ""
			sql_comm = ""
			if only_rows is not None:
				for col in only_rows:
					rows += ", "+str(col)
				rows = rows[1:]
			else:
				#table_cols_sql = "select column_name from information_schema.columns where table_schema='{table_schema}' and table_name='{table_name}'".format(table_name=table_name, table_schema=table_schema,) #BUG 01 information相关表的表名字需要大写.....(mysql8.0专属BUG  5.7没得)
				if table_schema.lower() == "information_schema":
					table_cols_sql = "select column_name from information_schema.columns where table_schema='{table_schema}' and table_name='{table_name}'".format(table_name=table_name.upper(), table_schema=table_schema,)
				else:
					table_cols_sql = "select column_name from information_schema.columns where table_schema='{table_schema}' and table_name='{table_name}'".format(table_name=table_name.lower(), table_schema=table_schema,)
				sql_result_1 = sql_execute.get_result_dict(table_cols_sql)
				if sql_result_1["istrue"]:
					for col in sql_result_1["data"]:
						if col[0] not in exclude_rows:
							rows += ", "+str(col[0])
					rows = rows[1:]
				
			if sql is None:
				sql_comm = "select {rows} from {table} {where}".format(rows=rows, table=table, where=where)
			
			else:
				sql_comm = str(sql) + " " + str(where)
				rows = sql.split("select ")[1].split(" from ")[0]
			#data["table"][table] = {"havedata":True, "rows":rows, "data":data}
			sql_result_2 = sql_execute.get_result_dict(sql_comm)
			if sql_result_2["istrue"]:
				data["table"][table] = {"havedata":True, "rows":rows, "data":sql_result_2["data"]}
			else:
				print(sql_comm)
				data["table"][table] = {"havedata":False, "rows":rows, "data":sql_result_2["data"]}

		#状态信息采集, 也就行执行的comm 比如show status之类的
		db_comm = self.db_comm
		for x in db_comm:
			sql_result = sql_execute.get_result_dict(x["comm"])
			if sql_result["istrue"]:
				data["comm"][x["name"]] = {"havedata":True, "rows":x["rows"], "data":sql_result["data"]}
			else:
				data["comm"][x["name"]] = {"havedata":False, "rows":x["rows"], "data":sql_result["data"]}

		#tps和qps采用计算平均, 也就是show status里面的 Questions/Uptime
		

		#数据库信息采集完成
		self.data["DBINFO"] = data


	def return_json(self):
		return self.data

	def return_json_file(self,file_dir):
		#把json数据类型全部转化为str
		class MyJsonEncoder(json.JSONEncoder):
			def default(self,obj):
				return str(obj)

		data = self.data
		data = json.dumps(data, cls=MyJsonEncoder)
		try:
			with open(file_dir,"w") as f:
				json.dump(data,f)
				return True
		except Exception as e:
			print(e)
			return False
