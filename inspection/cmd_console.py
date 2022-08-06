from . import ddcw_inspection
from . import log
from multiprocessing import Process, Manager, Queue
import yaml
import sys
import os
import time
from . import format_mf

class inspection():
	def __init__(self,parser):
		self.host = parser.HOST
		self.port = parser.PORT
		self.user = parser.USER
		self.password = parser.PASSWORD
		self.socket = parser.SOCKET
		self.ssh_port = parser.SSH_PORT
		self.ssh_user = parser.SSH_USER
		self.ssh_password = parser.SSH_PASSWORD
		self.ssh_pkey = parser.SSH_PKEY

		self.mf = parser.MF
		self.conf_file = parser.CONF_FILE
		self.saved_file = parser.SAVED_FILE

	def run(self,*args,**kwargs):

		try:
			inf = open(self.conf_file, 'r', encoding="utf-8")
			inf_data =  inf.read()
			inf.close()
			conf = yaml.load(inf_data,Loader=yaml.Loader)
		except Exception as e:
			print(e)
			sys.exit(1)
			

		#初始化日志文件
		logfile = conf["GLOBAL"]["Log_file"]
		if (logfile is None) or logfile == "":
			logfile = "logs/task_{time}.log".format(time=time.strftime("%Y%m%d_%H%M%S", time.localtime()))
		logfile = os.path.abspath(logfile) #格式化为绝对路径
		logfile_dir = os.path.dirname(logfile)
		os.makedirs(logfile_dir, exist_ok = True) #创建日志目录
		#logs = log.log(logfile=logfile) #每个进程自己创建, 这样记录的信息格式才不会相互覆盖


		global inspection_result
		inspection_result = {}

		def display_state(d,):
			fail_list = []
			lastmsg = "" #和上次输出一样的话, 就不输出了.
			while True:
				if d['stat'] == 1:
					msg = "[{pid}] {host}:{port} 运行中... 当前进度:{running} ".format(pid=d['pid'],host=d['host'],port=d['port'],running=d['running'])
					if msg != lastmsg:
						print(msg)
						lastmsg = msg
				elif d['stat'] == 0:
					continue
				elif d['stat'] == 2:
					msg = "[{pid}] {host}:{port} 巡检完成, 巡检报告:{result}".format(pid=d['pid'],host=d['host'],port=d['port'],result=d['result'])
					inspection_result['{host}_{port}'.format(host=d['host'],port=d['port'])] = msg
					if msg != lastmsg:
						print(msg)
						lastmsg = msg
				elif d['stat'] == 3:
					fail_list_name = "{host}_{port}".format(host=d['host'],port=d['port'])
					if fail_list_name in fail_list:
						continue
					else:
						msg = "[{pid}] {host}:{port} 巡检失败,请查看日志 {logfile}".format(pid=d['pid'],host=d['host'],port=d['port'],logfile=logfile)
						inspection_result['{host}_{port}'.format(host=d['host'],port=d['port'])] = msg
						if msg != lastmsg:
							print(msg)
							lastmsg = msg
						fail_list.append(fail_list_name)
				elif d['stat'] == 99:
					break
				else:
					continue
				time.sleep(0.5)
			return True

		taskname = "task_{time}".format(time=time.strftime("%Y%m%d_%H%M%S", time.localtime()))
		#多实例巡检
		if self.mf is not None:
			mf = open(self.mf, 'r', encoding="utf-8")
			mf_data = mf.read()
			mf.close()
			mfconf = yaml.load(mf_data,Loader=yaml.Loader)
			
			with Manager() as manager:
				#d = manager.dict() #貌似不支持二维数组, 但是每个值都支持dict, 所以也能实现二维数组... 但又不能修改值了, 还是拆开吧...
				q = manager.Queue(len(mfconf['DATA']))
				#l = logs
				c = conf

				#初始化队列和字典
				#mf_list 要巡检的实例列表
				mf_list = mfconf['DATA'] #后续考虑格式化 TODO
				for x in mf_list:
					q.put(x)
	
				thread_list={}
				dthread_list={}
				d = {}
				for p in range(0,mfconf['GLOBAL']['PARALLEL']):
					d[p] = manager.dict()
					d[p]['stat'] = 0
					d[p]['running'] = "waiting"
					thread_list[p] = Process(target=ddcw_inspection.inspection, args=(q,c,logfile,d[p], taskname),)
					dthread_list[p] = Process(target=display_state, args=(d[p],),)
				for p in range(0,mfconf['GLOBAL']['PARALLEL']):
					thread_list[p].start()
					dthread_list[p].start()
				for p in range(0,mfconf['GLOBAL']['PARALLEL']):
					thread_list[p].join()
					dthread_list[p].join()

		else:
			with Manager() as manager:
				inspection_one = {
					'host':self.host,
					'port':self.port,
					'password':self.password,
					'user':self.user,
					'socket':self.socket,
					'ssh_port':self.ssh_port,
					'ssh_user':self.ssh_user,
					'ssh_password':self.ssh_password,
					'ssh_pkey':self.ssh_pkey,
				}
				inspection_one = format_mf.formatc(inspection_one)
				q = manager.Queue(1)
				q.put(inspection_one)
				#l = logs
				c = conf
				d = manager.dict()
				d['stat'] = 0
				d['running'] = 'waiting'
				p = Process(target=ddcw_inspection.inspection, args=(q,c,logfile,d, taskname),)
				pd = Process(target=display_state, args=(d,),)
				p.start()
				pd.start()
				p.join()
				pd.join()
			#print("单机巡检")

			

		#print(inspection_result)
			
		return True


