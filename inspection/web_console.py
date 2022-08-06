import yaml
import sys,os
import time
from multiprocessing import Process, Manager, Queue
from . import ddcw_inspection
from threading import Thread 

class web_inspection:
	def __init__(self,parser):
		conf_file = parser.CONF_FILE
		try:
			inf = open(conf_file, 'r', encoding="utf-8")
			inf_data =  inf.read()
			inf.close()
			conf = yaml.load(inf_data,Loader=yaml.Loader)
		except Exception as e:
			print(e)
			sys.exit(1)

		self.host = conf['GLOBAL']['Web_host']
		self.port = int(conf['GLOBAL']['Web_port'])
		self.c = conf


	def init_history_task(self,tmp_dir):
		c = self.c
		task = {}
		task_detail = {}
		for x in os.listdir(tmp_dir):
			try:
				#注: 若主机名含_task_ 则解析失败
				hostport = x.split('_task_')[0]
				host = hostport.split('_')[0]
				port = hostport.split('_')[1]
				taskname = str(c['GLOBAL']['History_task_pre']) + str(x.split('_task_')[1].split('.')[0])
				taskdetailname = str(hostport) + '_' + taskname
				if taskname not in task:
					task[taskname] = {}
					task[taskname]['jindu'] = [0,0]
					task[taskname]['detail'] = []
				task[taskname]['detail'].append(taskdetailname)
				task_detail[taskdetailname] = {}
				task_detail[taskdetailname]['host'] = host
				task_detail[taskdetailname]['port'] = port
				task_detail[taskdetailname]['begin_time'] = ''
				task_detail[taskdetailname]['end_time'] = ''
				task_detail[taskdetailname]['score'] = 0
				task_detail[taskdetailname]['stat'] = 2
				task_detail[taskdetailname]['running'] = '已完成'
				task_detail[taskdetailname]['result'] = x
			except Exception as e:
				#print(e)
				continue
		#print(task)
		return task,task_detail



	def run(self,*args,**kwargs):
		c = self.c
		Tmp_dir = c['GLOBAL']['Tmp_dir']
		from flask import url_for,Flask,request,redirect,send_file, render_template
		import pandas as pd
		static_dir = str(os.getcwd()) + "/static"
		template_dir = str(os.getcwd()) + "/{Tmp_dir}".format(Tmp_dir=Tmp_dir)
		app = Flask(__name__, static_folder=static_dir, template_folder=template_dir )
		app.config['JSON_AS_ASCII'] = False #返回中文问题
		#app = Flask(__name__, )
		global task
		task = {}
		global task_detail
		task_detail = {}

		if c['GLOBAL']['History_task']:
			task,task_detail = self.init_history_task(c['GLOBAL']['Tmp_dir'])
		#print(task)
		#task_detail['test_task'] = {"running":"XXXXXXX"}
		@app.route('/')
		def index():
			print(os.getcwd())
			return app.send_static_file('index.html')


		@app.route('/inspection_web', methods=['POST'])
		def inspection_web():
			#global task,task_detail
			def display_state(d,):
				success_task_detail_list = [] #初始化巡检完成的队列
				task_detail_name = ''
				while True:
					try:
						task_detail_name = d['task_detail_name']
						task_name = d['task_name']
						task[task_name]['detail'].append(task_detail_name) #把这个task_detail注册到task中
						task_detail[task_detail_name] = {}
						task_detail[task_detail_name]['running'] = d['running'] #初始化task_detail
						break
					except Exception as e:
						time.sleep(0.01)
				while True:
					if d['stat'] == 99:
						#这个work线程完成了
						break 
					try:
						task_detail_name = d['task_detail_name']
						task_detail[task_detail_name]['running'] = d['running']
						task_detail[task_detail_name]['pid'] = d['pid']
						task_detail[task_detail_name]['host'] = d['host']
						task_detail[task_detail_name]['port'] = d['port']
						task_detail[task_detail_name]['begin_time'] = d['begin_time']
						task_detail[task_detail_name]['end_time'] = d['end_time']
						task_detail[task_detail_name]['stat'] = d['stat']
						#task_detail[task_detail_name]['result'] = d['result']
						task_detail[task_detail_name]['result'] = os.path.basename(d['result'])
						task_detail[task_detail_name]['task_name'] = d['task_name']
						task_detail[task_detail_name]['task_detail_name'] = d['task_detail_name']
						task_detail[task_detail_name]['score'] = d['score']
					except Exception as e:
						#产生异常就说明是新的一个task_name_detail了 也就是开始巡检另一个实例了
						task_detail[task_detail_name] = {}
						task_name = d['task_name']
						task[task_name]['detail'].append(task_detail_name)
						continue
						print(task_detail_name,task_detail,e)
					if d['stat'] == 2 or d['stat'] == 3:
						if task_detail_name not in success_task_detail_list:
							task[task_name]['jindu'][0] += 1 #stat=2 or 3
							success_task_detail_list.append(task_detail_name)

						#	#等待新的巡检任务开始
						#	while True:
						#		task_detail_name = d['task_detail_name']
						#		if d['stat'] == 99:
						#			#print("使命结束",d['pid'])
						#			break
						#		elif task_detail_name in success_task_detail_list:
						#			#print("还是旧任务",task_detail_name)
						#			continue
						#		else:
						#			#print("开始新任务了")
						#			task_name = d['task_name']
						#			task[task_name]['detail'].append(task_detail_name)
						#			task_detail[task_detail_name] = {}
						#			#print(task_detail_name)
						#			break
						#		time.sleep(0.01)
							
					time.sleep(0.01)
				
						
						
			try:
				#inspection_data = request.form['inspection_data']
				inspection_data = request.get_data()
				inspection_data = inspection_data.decode()
				#print(inspection_data,"AAAAAAA")
				inspection_data_old = eval(inspection_data)
				inspection_data = inspection_data_old['data']
				parallel = inspection_data_old['parallel']
				taskname = "task_{time}".format(time=time.strftime("%Y%m%d_%H%M%S", time.localtime())) #生成一个taskname
				task[taskname] = {} #格式化这个task
				task[taskname]['jindu'] = [0,len(inspection_data)]
				#task[taskname]['jindu'][0] = 0 #当前完成的实例数量
				#task[taskname]['jindu'][1] = len(inspection_data) #总的实例数量
				task[taskname]['detail'] = [] #每个实例的详情

				#print('inspection_data',inspection_data_old)
				
				PARALLEL = parallel if parallel < len(inspection_data) else len(inspection_data) #线程数太多没得意义

				#初始化日志
				logfile = c["GLOBAL"]["Log_file"]
				if (logfile is None) or logfile == "":
					logfile = "logs/task_{time}.log".format(time=time.strftime("%Y%m%d_%H%M%S", time.localtime()))
				logfile = os.path.abspath(logfile) #格式化为绝对路径
				logfile_dir = os.path.dirname(logfile)
				os.makedirs(logfile_dir, exist_ok = True) #创建日志目录


				with Manager() as manager:
					q = manager.Queue(len(inspection_data))
					for x in inspection_data:
						q.put(x)
					thread_list={}
					dthread_list={}
					d = {}
					for p in range(0,PARALLEL):
						d[p] = manager.dict()
						d[p]['stat'] = 0
						d[p]['running'] = "waiting"
						thread_list[p] = Process(target=ddcw_inspection.inspection, args=(q,c,logfile,d[p], taskname),)
						#dthread_list[p] = Process(target=display_state, args=(d[p],),)
						#修改为多线程, 因为多线程共享全局变量.....
						#thread_list[p] = Thread(target=ddcw_inspection.inspection, args=(q,c,logfile,d[p], taskname),)
						dthread_list[p] = Thread(target=display_state, args=(d[p],),)
					for p in range(0,PARALLEL):
						thread_list[p].start()
						dthread_list[p].start()
					for p in range(0,PARALLEL):
						thread_list[p].join()
						dthread_list[p].join()
			except Exception as e:
				print(e)
				return str(e)

			return "SUCCESS"
		
		@app.route('/inspection_status', methods=['POST'])
		def inspection_status():
			#global task,task_detail
			#detail = str(task)+str(task_detail)
			detail = {"task":task,"task_detail":task_detail}
			return detail

		@app.route('/inspection_item', methods=['POST'])
		def inspection_item():
			return {"data":c['INSPECTION']}

		
		@app.route('/inspection_global', methods=['POST'])
		def inspection_global():
			global_config = c['GLOBAL']
			global_config['Web_password'] = '不支持查看'
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
			file_name = "../" + c['GLOBAL']['Tmp_dir'] + "/" + str(file_name)
			if file_type == "html":
				return send_file(file_name,as_attachment=True)
			else:
				return "不支持这种文件类型{file_type}下载".format(file_type=file_type)
				pass
			return "不支持这种文件类型{file_type}下载".format(file_type=file_type)
		
		app.run(host=self.host,  port=self.port, debug=False, )
