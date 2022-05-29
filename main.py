import time
from ddcw_py_tools import ddcw_mysql
#from ddcw_py_tools import get_dict_from_sql
from ddcw_py_tools import ddcw_ssh
from ddcw_py_tools import get_local_comm
from ddcw_inspection import data_collection
from ddcw_inspection import analyze_data
from ddcw_inspection import templates
from ddcw_inspection import collection_detail
from ddcw_inspection import web_html
import json
import argparse
import os,sys
from multiprocessing import Process, Queue

#from multiprocessing import Array,Value


class inspection:
	def __init__(self,*args,**kwargs):
		try:
			host = kwargs["host"]
		except:
			host = "0.0.0.0"
		try:
			port = kwargs["port"]
		except:
			port= None
		try:
			user = kwargs["user"]
		except:
			user = None
	
		try:
			password = kwargs["password"]
		except:
			password = None
	
		try:
			socket = kwargs["socket"]
		except:
			socket = None
	
	
		try:
			ssh_port = kwargs["ssh_port"]
			ssh_user = kwargs["ssh_user"]
			ssh_password = kwargs["ssh_password"]
		except:
			ssh_port = None
			ssh_user = None
			ssh_password = None
	
		try:
			ssh_key = kwargs["ssh_key"]
		except:
			ssh_key = None
	
	
		try:
			data = kwargs["data"]
		except:
			data = None
	
		try:
			mode = kwargs["mode"]
		except:
			mode = 0 # 0 采集数据,分析数据, 生成巡检报告,  1 根据所给的data(json格式)生成巡检报告,  2 只收集数据, 不做分析,不生成巡检报告, 只返回json


		try:
			self.status = kwargs["status"]
		except:
			self.status = None
			
	
		self.mysql = ddcw_mysql.set(host=host,user=user,port=port,password=password,socket=socket)
		self.ssh = ddcw_ssh.set(host=host,port=ssh_port,user=ssh_user,password=ssh_password,key=ssh_key)
		self.mode = mode
		self.data = data
		self.local_shell = get_local_comm.set()
		self.host = host
		self.port = port
		self.user = user

	#测试是否连接成功
	def test(self):
		if self.mysql.test():
			mysql = True
		#	self.mysql.set()
		else:
			mysql = False
	
		if self.ssh.test():
			ssh = True
		#	self.ssh.set()
		else:
			ssh = False
		return {"mysql":mysql, "ssh":ssh}

	def connect(self):
		if self.mysql.test():
			self.mysql.set()
		if self.ssh.test():
			self.ssh.set()


	def run(self,*args,**kwargs):
		mysql = self.mysql
		ssh = self.ssh
		mode = self.mode
		host = self.host
		port = self.port
		local_shell = self.local_shell
		local_ip = local_shell.get_result_dict("ifconfig | grep inet  | awk '{print $2}'")["stdout"]
		if host in local_ip or host == "0.0.0.0" or host == "localhost":
			shell = local_shell
		elif ssh.test():
			shell = ssh
		else:
			shell = None


		try:
			task_name = kwargs["task_name"]
		except:
			task_name = None

		table_list = collection_detail.db_table()
		db_comm = collection_detail.db_comm()


		#收集信息
		def run1(shell, mysql, table_list,db_comm,only_json):
			data_coll = data_collection.get_data(shell=shell, sql=mysql, table_list=table_list, db_comm=db_comm)
			data_coll.get_mysql()
			print("进度... 35%")
			data_coll.get_host() 
			print("进度... 54%")
			#data_coll.return_json_file("test20220419.json")
			if only_json:
				return data_coll.return_json_file("ddcw_{host}_{port}_{time}.json".format(host=host,port=port,time=str(time.time())))
			else:
				return data_coll.return_json()

		#分析信息
		def run2(jsondata):
			analyze = analyze_data.set(data=jsondata)
			analyze.analyze()
			return analyze.return_json()

		#生成巡检报告
		def run3(analyze_json,file_name):
			tmplate_file = templates.set(data=analyze_json, file_dir=RUN_DIR,file_name=file_name )
			return tmplate_file.return_html()

		def jindu(jindu):
			try:
				running[task_name]["status"] = jindu
			except:
				print("进度... {jindu}".format(jindu=jindu))
	

		if mode == 0:
			#print(run3(run2(run1(shell,mysql,table_list,db_comm))))
			jindu("15%")
			run1_result = run1(shell,mysql,table_list,db_comm,False)
			run1_result["INFO"]["HOST"] = self.host
			run1_result["INFO"]["PORT"] = self.port
			run1_result["INFO"]["USER"] = self.user
			jindu("70%")
			run2_result = run2(run1_result)
			jindu("80%")
			run3_result = run3(run2_result,"mysql_{host}_{port}_{time}".format(host=host,port=port,time=str(time.time())))
			jindu("95%")
			return run3_result
		elif mode == 1:
			#with open("test20220419.json",'r') as f :
			#	xunjian = json.load(f)
			#json_data = json.loads(xunjian)
			json_data = self.data
			run2_result = run2(json_data)
			run3_result = run3(run2_result, "mysql_{time}".format(time=str(time.time())))
			#print(run3_result)
			return run3_result

		elif mode == 2:
			run1_result = run1(shell,mysql,table_list,db_comm,True)
			try:
				run1_result["INFO"]["HOST"] = self.host
				run1_result["INFO"]["PORT"] = self.port
				run1_result["INFO"]["USER"] = self.user
			except:
				pass
			print(run1_result)
			return(run1_result)
		else:
			return {"istrue":False,"data":"不支持mode"}
			

	def close(self):
		try:
			self.mysql.close()
			self.ssh.close()
		except:
			pass



class inspection_mf:
	def __init__(self, *args,**kwargs):
		try:
			mf = kwargs["mf"]
		except Exception as e:
			print(e)
			return
		try:
			test_only = kwargs["test_only"]
		except Exception as e:
			test_only = False

		if test_only:
			self.TEST_ONLY = test_only
		else:
			self.TEST_ONLY = mf["TEST_ONLY"]
		self.PARALLEL = mf["PARALLEL"]
		DEFAULT_HOST= mf["DEFAULT_HOST"]
		DEFAULT_PORT= mf["DEFAULT_PORT"]
		DEFAULT_USER= mf["DEFAULT_USER"]
		DEFAULT_PASSWORD= mf["DEFAULT_PASSWORD"]
		DEFAULT_SSH_PORT= mf["DEFAULT_SSH_PORT"]
		DEFAULT_SSH_USER= mf["DEFAULT_SSH_USER"]
		DEFAULT_SSH_PASSWORD= mf["DEFAULT_SSH_PASSWORD"]
		q = Queue(len(mf["DATA"])*2)
		self.q_running = Queue(len(mf["DATA"])*2)
		self.q_complete = Queue(len(mf["DATA"])*2)
		for x in mf["DATA"]:
			try:
				host = x["host"]
			except:
				host = DEFAULT_HOST

			try:
				port = x["port"]
			except:
				port = DEFAULT_PORT

			try:
				user = x["user"]
			except:
				user = DEFAULT_USER
			try:
				password = x["password"]
			except:
				password = DEFAULT_PASSWORD
			try:
				ssh_port = x["ssh_port"]
			except:
				ssh_port = DEFAULT_SSH_PORT
			try:
				ssh_user = x["ssh_user"]
			except:
				ssh_user = DEFAULT_SSH_USER
			try:
				ssh_password = x["ssh_password"]
			except:
				ssh_password = DEFAULT_SSH_PASSWORD

			q.put({"host":host,"port":port,"user":user,"password":password,"ssh_port":ssh_port,"ssh_user":ssh_user,"ssh_password":ssh_password})
		self.q = q
		

	def run(self,*args,**kwargs):
		q = self.q
		q_complete = self.q_complete
		TEST_ONLY = self.TEST_ONLY
		def inspection_inst():
			while True:
				try:
					ins_index = q.get(block=False,timeout=10)
				except:
					break
				#开始巡检
				ins = inspection(host=ins_index["host"],port=ins_index["port"],user=ins_index["user"],password=ins_index["password"],ssh_port=ins_index["ssh_port"],ssh_user=ins_index["ssh_user"],ssh_password=ins_index["ssh_password"])
				if TEST_ONLY == True:
					ins_test = ins.test()
					print("测试:",ins_test)
				else:
					ins.connect()
					ins_result = ins.run()
					q_complete.put(ins_result)
					if ins_result["istrue"]:
						print("{host}:{port} 巡检成功. {file}".format(host=ins_index["host"],port=ins_index["port"],file=ins_result["data"]))
					else:
						print("{host}:{port} 失败!!!!!!!!!!!!1. {file}".format(host=ins_index["host"],port=ins_index["port"],file=ins_result["data"]))

		thread_list={}
		for p in range(self.PARALLEL):
			thread_list[p] = Process(target=inspection_inst,args=(),daemon=True)	
		for p in range(self.PARALLEL):
			thread_list[p].start()
		for p in range(self.PARALLEL):
			thread_list[p].join()
		return_data = []
		while not q_complete.empty():
			try:
				result = q_complete.get(block=False,timeout=10)
				return_data.append(result)
			except Exception as e:
				print(e,"q_complete")
				break
		return return_data
	


class inspection_web:
	def __init__(self,*args,**kwargs):
		self.host = kwargs["host"]
		self.port = kwargs["port"]
		self.user = kwargs["user"]
		self.password = kwargs["password"]

	

	def run(self):
		#导入flask
		from flask import url_for,Flask,request,redirect,send_file
		global running 
		running = {}
		global complate
		complate = {}

		#初始化已完成的巡检文件
		for x in os.listdir(RUN_DIR):
			#加载.html结尾的文件 没想到还有这种办法^_^
			if len(x) == len(x.split(".html")[0])+5:
				complate[x] = {"host":"","port":"","user":"","mysql":"","ssh":"","status":x}
			
	
		app = Flask(__name__, static_folder=RUN_DIR, )
	
		@app.route('/')
		def index():
			return web_html.return_index()
	
		@app.route('/view/<html>')
		def web_view(html):
			try:
				#html = RUN_DIR + "/" + str(html)
				return app.send_static_file(html)
			except Exception as e :
				print(e,html,RUN_DIR)
				return "{filename} 不存在".format(filename=html)
	
		@app.route('/uploads',methods=['POST'])
		def web_upload():
			try:
				f = request.files['file']
				json_data = json.load(f)
				json_data = json.loads(json_data)
				ins_1 = inspection(data=json_data, mode=1)
				task_name = "task_" + str(time.time())
				
				ins_1_result = ins_1.run()
				running[task_name] =   {"host":"","port":"","user":"","mysql":"","ssh":"","status":"80%"}
				if ins_1_result["istrue"]:
						complate[task_name] = {"host":"","port":"","user":"","mysql":"","ssh":"","status":ins_1_result["data"]}
						ins_1.close()
						del running[task_name]
						#return {"type":"run","data":"[INFO] 分析完成..... {file_name}".format(file_name=ins_1_result["data"])}
						return  '''
<script type="text/javascript">
function returnIndex(){
//location.href="/index"
window.history.go(-1)
}
setTimeout("returnIndex()",5000)
</script>
<div align="center"><h2>请查看已完成''' + ins_1_result["data"] + '''</h2><p id="timereturn">5 秒后自动返回<a href="/view/{file_name}" target="_blank">(点此直接查看)</a></p></div>'''.format(file_name=ins_1_result["data"])
				else:
						return {"type":"run","data":"[ERROR] 分析完成..... {file_name}".format(file_name=ins_1_result["data"])}
			except Exception as e:
				print(e)
				return "服务器获取文件失败"


		@app.route('/download')
		def web_download():
			try:
				file_name = request.args.get('file_name')
			except:
				return "文件 {file_name} 不存在".format(file_name=file_name)
			try:
				file_type = request.args.get('file_type')
			except:
				file_type = "html"
			file_name = RUN_DIR + "/" + str(file_name)
			file_name_pdf = file_name +  ".pdf"
			if file_type == "html":
				return send_file(file_name,as_attachment=True)
			elif file_type == "pdf":
				return "暂不支持PDF下载, 请使用 浏览器打印-->另存为PDF 功能"
			return "不支持这种文件类型{file_type}下载".format(file_type=file_type)
			


		@app.route('/status', methods=['POST'])
		def web_status():
			try:
				running_status = request.form['running_status']
			except:
				running_status = False
			try:
				complate_status = request.form['complate_status']
			except:
				complate_status = False
			return_dict = {}
			if running_status:
				return_dict["running_status"] = {"havedata":"true","data":running}
			else:
				return_dict["running_status"] = {"havedata":"false","data":"none"}
			if complate_status:
				return_dict["complate_status"] = {"havedata":"true","data":complate}
			else:
				return_dict["complate_status"] = {"havedata":"false","data":"none"}
				
			return return_dict
	

		@app.route("/mf",methods=['POST'])
		def web_mf():
			try:
				f = request.files['file']
				f_str = f.read().decode("UTF-8")
				mf = eval(f_str)
				ins = inspection_mf(mf=mf,)
				ins_result = ins.run()
				for x in ins_result:
					if x["istrue"]:
						complate["MF_"+str(x["data"])] = {"host":"","port":"","user":"","mysql":"","ssh":"","status":x["data"]}
					else:
						print(x," 失败")
				return  '''
<script type="text/javascript">
function returnIndex(){
//location.href="/index"
window.history.go(-1)
}
setTimeout("returnIndex()",3000)
</script>
<div align="center"><h2>巡检完成...</h2><p id="timereturn">3 秒后自动返回<a href="#complete">(点此查看任务)</a></p></div>'''
			except Exception as e:
				return {"status":1,"data":e}
			

		@app.route('/inspection',methods=['POST'])
		def web_inspection():
			host = request.form['host']
			port = request.form['port']
			user = request.form['user']
			password = request.form['password']
			ssh_port = request.form['ssh_port']
			ssh_user = request.form['ssh_user']
			ssh_password = request.form['ssh_password']
			try:
				only_test = request.form['only_test']
			except Exception as e:
				only_test = False
			ins_1 = inspection(host=host,port=port,user=user,password=password,ssh_port=ssh_port,ssh_user=ssh_user,ssh_password=ssh_password)
			ins_1_test = ins_1.test()

			#print(request.form)
			if only_test == "True":
				print("only_test")
				return {"type":"test","data":ins_1_test}
			else:
				if ins_1_test["mysql"] :
					task_name = "task_" + str(time.time())
					running[task_name] =   {"host":host,"port":port,"user":user,"mysql":ins_1_test["mysql"],"ssh":ins_1_test["ssh"],"status":"0%"}
					ins_1.connect()
					running[task_name]["status"] = "10%"
					ins_1_result = ins_1.run(task_name=task_name)
					running[task_name]["status"] = "100%"
					if ins_1_result["istrue"]:
						complate[task_name] = {"host":host,"port":port,"user":user,"mysql":ins_1_test["mysql"],"ssh":ins_1_test["ssh"],"status":ins_1_result["data"]}
						del running[task_name]
						ins_1.close()
						return {"type":"true","data":"[INFO] 巡检完成..... {file_name}".format(file_name=ins_1_result["data"])}
					else:
						return {"type":"false","data":"[ERROR] 巡检失败..... {file_name}".format(file_name=ins_1_result["data"])}
				else:
					return {"type":"false","data":"[ERROR] mysql连接失败 (详情请查看日志...)" }

		app.run(host=self.host,  port=self.port, debug=False, )




#定义参数
def _argparse():
	# argparse用法 https://docs.python.org/3/library/argparse.html
	parser = argparse.ArgumentParser(description='MYSQL巡检报告生成脚本. 最新下载地址: https://github.com/ddcw/inspection')
	parser.add_argument('--web',  action='store_true', dest='web', help='启动控制台')
	parser.add_argument('--web-host',  action='store', dest='web_host', default="0.0.0.0", help='web控制台的监听的地址, 默认 0.0.0.0')
	parser.add_argument('--web-port',  action='store', dest='web_port', type=int, default=6121, help='web控制台监听的端口')
	parser.add_argument('--web-user',  action='store', dest='web_user', default="ddcw", help='web控制台用户')
	parser.add_argument('--web-password',  action='store', dest='web_password', default="123456", help='web控制台密码')
	parser.add_argument('--version', '-v', '-V', action='store_true', dest="version",  help='VERSION')

	parser.add_argument('--host', '-H',  action='store', dest='HOST', default="localhost", help='MYSQL服务器地址(默认localhost)')
	parser.add_argument('--port', '-P' ,  action='store', dest='PORT',type=int, default=3306, help='MYSQL服务器端口')
	parser.add_argument('--user', '-u' ,  action='store', dest='USER',  help='MYSQL用户')
	parser.add_argument('--password', '-p' ,  action='store', dest='PASSWORD',   help='MYSQL用户的密码')
	parser.add_argument('--socket', '-S' ,  action='store', dest='SOCKET',   help='mysql unix socket')
	parser.add_argument('--ssh-port', '-sP' ,  action='store', dest='SSH_PORT', default=22, type=int , help='MYSQL服务器主机的SSH端口(默认22)')
	parser.add_argument('--ssh-user', '-su' ,  action='store', dest='SSH_USER',  help='MYSQL服务器主机的SSH用户')
	parser.add_argument('--ssh-password', '-sp' ,  action='store', dest='SSH_PASSWORD',   help='MYSQL服务器主机的SSH用户的密码')
	parser.add_argument('--ssh-pkey', '-spk' ,  action='store', dest='SSH_PKEY',   help='MYSQL服务器主机的SSH用户的私钥(支持RSA和DSA)')
	parser.add_argument('--file', '-f' ,  action='store', dest='SAVED_FILE',   help='巡检结果保存文件')
	parser.add_argument('--analyze-file', '-a' ,  action='store', dest='ANALYZE_FILE',   help='分析已采集的JSON文件')
	parser.add_argument('--only-test', '--test' ,  action='store_true', dest='TEST_ONLY',   help='只是测试下mysql或者ssh能不能用')

	parser.add_argument('--run-dir', '-r' ,  action='store', dest='RUN_DIR', default="tmp_html",   help='巡检结果保存目录(默认 tmp_html)')

	parser.add_argument('--mf', '-mf' ,  action='store', dest='MF',  help='批量巡检(使用这个参数时, 其它参数均无效, --only-test 除外..)')
	
	return parser.parse_args()


if __name__ == '__main__':
	parser = _argparse()
	global RUN_DIR
	RUN_DIR = parser.RUN_DIR
	#创建目录 RUN_DIR
	test_local_comm = get_local_comm.set(timeout=3)
	test_local_comm.get_result_dict("mkdir -p {tmp_html}".format(tmp_html=RUN_DIR))

	#RUN_DIR = os.path.dirname(os.path.abspath(RUN_DIR))
	RUN_DIR = os.path.abspath(RUN_DIR)

	mode = 1 if parser.ANALYZE_FILE else 0

	
	if parser.version:
		print("Version: 1.1")
		sys.exit(0)

	if parser.MF:
		try:
			test_only = parser.TEST_ONLY
		except:
			test_only = False


		try:
			with open(parser.MF,'r') as f :
				mf_tmp = json.load(f)
			mf = mf_tmp
			print("开始批量巡检..")
			ins = inspection_mf(mf=mf, test_only=test_only)
			ins.run()
			sys.exit(0)
		except Exception as e:
			print("可能是格式错误",e)
			sys.exit(1)
		

	if parser.web:
		print("启动web, http://{host}:{port}".format(host=parser.web_host, port=parser.web_port))
		ins1 = inspection_web(
			host = parser.web_host,
			port = parser.web_port,
			user = parser.web_user,
			password = parser.web_password,
			)
		ins1.run()
	else:
		#ins1 = inspection(port=3332,password="123456",user="root",ssh_password=123456,mode=1)
		json_data=None
		if parser.ANALYZE_FILE:
			try:
				with open(parser.ANALYZE_FILE,'r') as f :
					xunjian = json.load(f)
				json_data = json.loads(xunjian)
			except Exception as e:
				print(e)
		ins1 = inspection(
			host=parser.HOST, 
			port=parser.PORT,
			user=parser.USER,
			password=parser.PASSWORD,
			socket=parser.SOCKET,
			ssh_port=parser.SSH_PORT,
			ssh_user=parser.SSH_USER,
			ssh_password=parser.SSH_PASSWORD,
			ssh_key=parser.SSH_PKEY,
			mode=mode, 
			data=json_data,
		)
		if parser.ANALYZE_FILE:
			print("开始分析json文件")
			ins1_result = ins1.run()
			if ins1_result["istrue"]:
				print("分析完成, 请查看巡检报告 {RUN_DIR}/{report}".format(RUN_DIR=RUN_DIR,report=ins1_result["data"]))
				sys.exit(0)
			else:
				print("分析失败")
				sys.exit(1)
		ins1_test = ins1.test()
		if parser.TEST_ONLY:
			print(ins1_test)
			sys.exit(0)
		if ins1_test["mysql"]:
			print("开始巡检: MYSQL",end='')
		else:
			print("请检查mysql连接信息")
			sys.exit(1)
		if ins1_test["ssh"] and not parser.ANALYZE_FILE:
			print(" 和 主机")
		else :
			print("")
		ins1.connect()
		ins1_result = ins1.run()
		print("进度... 100%")
		if ins1_result["istrue"]:
			print("巡检完成, 请查看巡检报告 {RUN_DIR}/{report}".format(RUN_DIR=RUN_DIR,report=ins1_result["data"]))
		else:
			print("巡检失败")
