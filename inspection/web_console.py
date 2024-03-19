import yaml
import sys,os
import time
from multiprocessing import Process, Manager, Queue
#from . import ddcw_inspection
from threading import Thread 
from gevent import pywsgi

from inspection import manager_inspection
from inspection import hashstr
from inspection import work_inspection
from inspection import work_relation



class web_inspection:
	def __init__(self,parser):
		conf_file = parser.CONF_FILE
		try:
			with open(conf_file, 'r', encoding="utf-8") as f:
				inf_data =  f.read()
			conf = yaml.load(inf_data,Loader=yaml.Loader)
		except Exception as e:
			print(e)
			sys.exit(1)


		#是否启动WEB. 如果可以连上manager就不启动web
		_INNER_ENABLE_WEB = True

		self.host = conf['WEB']['host']
		self.port = int(conf['WEB']['port'])
		self.c = conf

		manager_host = conf['MANAGER']['host']
		manager_port = int(conf['MANAGER']['port'])
		manager_authkey = hashstr.hash1(conf['MANAGER']['authkey'])

		#初始化task
		inspection_instance = manager_inspection.inspection()

		#初始化manager
		manager_instance = manager_inspection.task_manager()
		if manager_instance.test_conn(manager_host,manager_port,manager_authkey):
			_INNER_ENABLE_WEB = False
			print('已连接manager.... 不会启动web')
			#pass
		else:
			try:
				#manager_instance.start(manager_host,manager_port,manager_authkey,inspection_instance)
				manager_process = Process(target=manager_instance.start, args=(manager_host,manager_port,manager_authkey,inspection_instance),)
				manager_process.start()
			except Exception as e:
				print(e)
				sys.exit(1)

		self.manager_host = manager_host
		self.manager_port = manager_port
		self.manager_authkey = manager_authkey

		#启动work进程(非阻塞方式)
		PARALLEL = int(conf['OTHER']['parallel'])
		thread_list = {}
		for p in range(0,PARALLEL):
			thread_list[p] = Process(target=work_inspection.inspection, kwargs={'conf':self.c},)
		for p in range(0,PARALLEL):
			thread_list[p].start()
			#print(p,' start')
		
		#启动relation_work进程
		relation_work = Process(target=work_relation.relation, kwargs={'conf':self.c})
		relation_work.start()


		#本机连上manager
		manager_instance = manager_inspection.task_manager()
		m = manager_instance.conn(manager_host,manager_port,manager_authkey)
		q = m.task_queue() #将要巡检的队列
		queue_relation = m.queue_relation() #将要巡检的队列
		inspection_task = m.inspection() #task相关的信息
		self.q = q
		self.inspection_task = inspection_task
		self.queue_relation = queue_relation

		self._INNER_ENABLE_WEB = _INNER_ENABLE_WEB



	def relation_analyze(data):
		return {'status':True,'data':''}


	def run(self,*args,**kwargs):
		if not self._INNER_ENABLE_WEB:
			return True
		c = self.c
		Tmp_dir = c['OTHER']['report_dir']
		inspection_file = c['OTHER']['inspection']
		with open(inspection_file, 'r', encoding="utf-8") as f:
				inf_data =  f.read()
		inspection_conf = yaml.load(inf_data,Loader=yaml.Loader)
		from flask import url_for,Flask,request,redirect,send_file, render_template
		import pandas as pd
		static_dir = str(os.getcwd()) + "/static"
		template_dir = str(os.getcwd()) + "/{Tmp_dir}".format(Tmp_dir=Tmp_dir)
		app = Flask(__name__, static_folder=static_dir, template_folder=template_dir )
		app.config['JSON_AS_ASCII'] = False #返回中文问题
		#app = Flask(__name__, )
		@app.route('/')
		def index():
			print(os.getcwd())
			return app.send_static_file('index.html')


		@app.route('/inspection_web', methods=['POST'])
		def inspection_web():
			q = self.q
			inspection_task = self.inspection_task
			try:
				#inspection_data = request.form['inspection_data']
				inspection_data = request.get_data()
				inspection_data = inspection_data.decode()
				#print(inspection_data,"AAAAAAA")
				inspection_data_old = eval(inspection_data)
				inspection_data = inspection_data_old['data']
				#inspection_data去重 
				taskid = "task_{time}".format(time=time.strftime("%Y%m%d_%H%M%S", time.localtime())) #生成一个taskid
				#task[taskid] = len(inspection_data)

				#print(inspection_data)
				#PARALLEL = parallel if parallel < len(inspection_data) else len(inspection_data) #线程数太多没得意义

				#初始化日志
				#logfile = os.path.abspath(logfile) #格式化为绝对路径
				#logfile_dir = os.path.dirname(logfile)
				#os.makedirs(logfile_dir, exist_ok = True) #创建日志目录

			
				#初始化task信息
				inspection_task.init_task(taskid)
				inspection_task.set_task(taskid,'total',len(inspection_data))

				#初始化巡检队列
				for x in inspection_data:
					x['taskid'] = taskid
					x['data'] = {'havedata':False,'data':'xxx.xml'}
					#print(x,'AAAAAAAAAAAAAAAaa')
					q.put(x)

				#是否监控这个巡检完成? 看后面的需求吧. 目前设计的是 有绘制节点关系的需求就做 比较task[taskid]['total']和task[taskid]['complete']
				#还是启一个单独的进程去做吧, 这样不影响前端, 加个queue relation
				if self.c['OTHER']['node_relation']:
					self.queue_relation.put(taskid)
				#	while True:
				#		jindu = inspection_task.get_task_jindu(taskid)
				#		complete_n = jindu[0]
				#		total_n = jindu[1]
				#		if complete_n < total_n:
				#			time.sleep(3)
				#		else:
				#			relation_file = ana_relation.get_relation_csv(taskid,inspection_task,self.c['OTHER']['node_relation_file'])
				#			inspection_task.set_task(taskid,'relation',relation_file)
				#			break

			except Exception as e:
				print(e)
				return str(e)

			return "SUCCESS"
		
		@app.route('/inspection_status', methods=['POST'])
		def inspection_status():
			try:
				inspection_task = self.inspection_task
				task_list = inspection_task.get_task_all()
				task_detail_list = inspection_task.get_task_detail_all()
				return_task_detail = {}
				for x in task_detail_list:
					return_task_detail[x] = {}
					return_task_detail[x]['task_detail_id'] = task_detail_list[x]['task_detail_id']
					return_task_detail[x]['host'] = task_detail_list[x]['host']
					return_task_detail[x]['port'] = task_detail_list[x]['port']
					return_task_detail[x]['begin_time'] = task_detail_list[x]['begin_time']
					return_task_detail[x]['end_time'] = task_detail_list[x]['end_time']
					return_task_detail[x]['running'] = str(task_detail_list[x]['running'])
					return_task_detail[x]['stat'] = task_detail_list[x]['stat']
					return_task_detail[x]['score'] = task_detail_list[x]['score']
					return_task_detail[x]['result'] = task_detail_list[x]['result']
					return_task_detail[x]['task_detail_id'] = task_detail_list[x]['task_detail_id']
				detail = {'task':task_list,'task_detail':return_task_detail}
				return detail
			except:
				return False

		@app.route('/inspection_item', methods=['POST'])
		def inspection_item():
			return {"data":inspection_conf['INSPECTION']}

		
		@app.route('/inspection_global', methods=['POST'])
		def inspection_global():
			global_config = {}
			#global_config = {x:c['MYSQL'][x] for x in c['MYSQL']}
			global_config.update(c['MYSQL'])
			global_config.update(c['HOST'])
			global_config.update(c['OTHER'])
				
			return {"data":global_config}

		@app.route('/view/<html>')
		def web_view(html):
			try:
				#return app.send_static_file("127.0.0.1_3308_task_20220727_113139.html")
				return render_template(html) #虽然没有用到模板功能, 但是方便设置路径...
			except Exception as e :
				print(e,html,)
				return "{filename} 不存在".format(filename=html)

		@app.route('/download')
		def download():
			try:
				file_name = request.args.get('file_name')
			except:
				return "文件 {file_name} 不存在".format(file_name=file_name)
			try:
				file_type = request.args.get('file_type')
			except:
				file_type = "html"
			file_name = "../" + c['OTHER']['report_dir'] + "/" + str(file_name)
			if file_type == "html":
				return send_file(file_name,as_attachment=True)
			elif file_type == "docx":
				return send_file(file_name,as_attachment=True)
			elif file_type == "csv":
				return send_file(file_name,as_attachment=True)
			else:
				return "不支持这种文件类型{file_type}下载".format(file_type=file_type)
				pass
			return "不支持这种文件类型{file_type}下载".format(file_type=file_type)
		
		print('http://{host}:{port}'.format(host=self.host, port=self.port))
		#app.run(host=self.host,  port=self.port, debug=False, )
		server = pywsgi.WSGIServer((self.host, self.port), app)
		server.serve_forever()
