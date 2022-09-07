from multiprocessing import Process, Manager, Queue
import yaml
import sys
import os
import time
from inspection import manager_inspection
from inspection import hashstr
from inspection import work_inspection
from . import parse_MF
from inspection import work_relation

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
		self.af = parser.af
		self.conf_file = parser.CONF_FILE
		#self.saved_file = parser.SAVED_FILE

		conf_file = parser.CONF_FILE
		try:
			with open(conf_file, 'r', encoding="utf-8") as f:
				inf_data =  f.read()
			conf = yaml.load(inf_data,Loader=yaml.Loader)
		except Exception as e:
			print(e)
			sys.exit(1)

		self.c = conf

		#是否启用命令行巡检
		_INNER_ENABLE_CONSOLE = True

		manager_host = conf['MANAGER']['host']
		manager_port = int(conf['MANAGER']['port'])
		manager_authkey = hashstr.hash1(conf['MANAGER']['authkey'])

		inspection_instance = manager_inspection.inspection()
		manager_instance = manager_inspection.task_manager()
		if manager_instance.test_conn(manager_host,manager_port,manager_authkey):
			print('已连接manager.... 将等待 {h} 下发任务'.format(h=manager_host))
			_INNER_ENABLE_CONSOLE = False

		else:
			try:
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

		self.relation_work = relation_work

		self.thread_list = thread_list
		self.PARALLEL = PARALLEL
		self.manager_process = manager_process
		#本机连上manager
		manager_instance = manager_inspection.task_manager()
		m = manager_instance.conn(manager_host,manager_port,manager_authkey)
		q = m.task_queue() #将要巡检的队列
		queue_relation = m.queue_relation()
		inspection_task = m.inspection() #task相关的信息
		self.q = q
		self.inspection_task = inspection_task
		self.queue_relation = queue_relation
		self._INNER_ENABLE_CONSOLE = _INNER_ENABLE_CONSOLE


	def run(self,*args,**kwargs):
		if not self._INNER_ENABLE_CONSOLE:
			time.sleep(10000000)
		c = self.c
		q = self.q
		queue_relation = self.queue_relation
		Tmp_dir = c['OTHER']['report_dir']
		inspection_file = c['OTHER']['inspection']
		with open(inspection_file, 'r', encoding="utf-8") as f:
			inf_data =  f.read()
		inspection_conf = yaml.load(inf_data,Loader=yaml.Loader)

		#初始化task
		inspection_task = self.inspection_task
		taskid = "task_{time}".format(time=time.strftime("%Y%m%d_%H%M%S", time.localtime())) #生成一个taskid
		inspection_task.init_task(taskid)

		#初始化巡检队列
		#多实例巡检
		if self.mf is not None:
			with open(self.mf, 'r', encoding="utf-8") as f:
				inf_data =  f.read()
			mfobj = yaml.load(inf_data,Loader=yaml.Loader)
			inspection_task.set_task(taskid,'total',len(mfobj['DATA']))
			for x in parse_MF.get_result(mfobj):
				x['taskid'] = taskid
				x['data'] = {'havedata':False,'data':'xxx.xml'}
				q.put(x)
			if self.c['OTHER']['node_relation']:
				self.queue_relation.put(taskid)
		elif self.af is None:
			inspection_task.set_task(taskid,'total',1)
			_tmp_q1 = {'host':self.host,'port':self.port,'user':self.user,'password':self.password,'socket':self.socket,'sshport':self.ssh_port,'sshuser':self.ssh_user,'sshpassword':self.ssh_password,'sshpkey':self.ssh_pkey,'sshenable':True,'sshforce':False,'taskid':taskid,'data':{'havedata':False,'data':'xxx.xml'}}
			q.put(_tmp_q1)

		elif self.af is not None:
			print('开始分析采集数据, 并生成巡检报告')
			_tmp_q2 = {'data':{'havedata':True,'data':self.af}, 'taskid':taskid}
			q.put(_tmp_q2)
			#time.sleep(1000)
		else:
			print('啥都没....')
			return False


		time.sleep(3)
		while True:
			jindu = inspection_task.get_task_jindu(taskid)
			complete_n = jindu[0]
			total_n = jindu[1]
			if complete_n < total_n:
				print('进度:{a}/{b}'.format(a=complete_n,b=total_n))
				time.sleep(3)
			else:
				break
		print('巡检完成. 巡检报告如下:')
		task_result = inspection_task.get_task(taskid)
		for x in task_result['list']:
			report_result = inspection_task.get_task_detail(x)['result']
			i_host = inspection_task.get_task_detail(x)['host']
			i_port = inspection_task.get_task_detail(x)['port']
			if len(report_result) == 0:
				print('{host}:{port} 巡检失败, 请查看日志'.format(host=i_host,port=i_port))
			for y in inspection_task.get_task_detail(x)['result']:
				print('{host}:{port} 巡检报告({report_type}):{report}'.format(host=i_host,port=i_port,report=y['data'],report_type=y['type']))


		#如果要分析节点关系, 就等一会
		if self.c['OTHER']['node_relation']:
			print('分析节点关系中, wait....')
			while inspection_task.get_task(taskid)['relation'] == '':
				time.sleep(1)
				print(inspection_task.get_task(taskid)['relation'])
			print('节点关系csv文件: {f}'.format(f=inspection_task.get_task(taskid)['relation']))

		for p in range(0,self.PARALLEL):
			self.thread_list[p].terminate()
		self.manager_process.terminate()
		self.relation_work.terminate()
		#sys.exit(0)
		return True

