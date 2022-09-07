import time
class inspection:
	def __init__(self,):
		self.task = {}
		self.task_detail = {}
		self.task_detail_running = [] #定义一个运行中的task_detail, 每个巡检完了就来删, 开始巡检的时候就设置一下
		self.process_stat = {} #各进程的状态 0等待中 1运行中 2这个进程完成巡检后就得退出(其它进程设置)...

	def set_process(self,k,v):
		self.process_stat[k] = v
		return True
	def get_process(self,k):
		return self.process_stat[k]
	def get_process_all(self):
		return self.process_stat

	def init_task(self,taskid):
		#初始化task
		self.task[taskid] = {}
		self.task[taskid]['taskid'] = taskid
		self.task[taskid]['begin_time'] = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())
		self.task[taskid]['end_time'] = ''
		self.task[taskid]['total'] = 0
		self.task[taskid]['complete'] = 0
		self.task[taskid]['running'] = 0
		self.task[taskid]['fail'] = 0 #失败的数量
		self.task[taskid]['list'] = [] #task_detail_id
		self.task[taskid]['relation'] = '' #节点关系的csv文件路径

	def init_task_detail(self,taskid,task_detail_id):
		self.task_detail[task_detail_id] = {}
		self.task_detail[task_detail_id]['taskid'] = taskid
		self.task_detail[task_detail_id]['task_detail_id'] = task_detail_id
		self.task_detail[task_detail_id]['host'] = ''
		self.task_detail[task_detail_id]['port'] = ''
		self.task_detail[task_detail_id]['user'] = ''
		self.task_detail[task_detail_id]['begin_time'] = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())
		self.task_detail[task_detail_id]['end_time'] = ''
		self.task_detail[task_detail_id]['stat'] = 0
		self.task_detail[task_detail_id]['running'] = 'waiting'
		self.task_detail[task_detail_id]['result'] = []
		self.task_detail[task_detail_id]['score'] = -1
		self.task_detail[task_detail_id]['baseinfo'] = ''
		self.task_detail[task_detail_id]['relation_data'] = {}
		self.task_detail[task_detail_id]['role'] = []
		self.task_detail[task_detail_id]['inspection_detail'] = ''
		self.task_detail[task_detail_id]['suggestion'] = ''
		self.task_detail[task_detail_id]['mysqlstatus'] = False #显示mysql连接是否成功
		self.task_detail[task_detail_id]['sshstatus'] = False

	def get_task(self,*args):
		taskid = args[0]
		try:
			task_obj = args[1]
			return self.task[taskid][task_obj]
		except:
			return self.task[taskid]

	def get_task_all(self,):
		return self.task

	def get_task_jindu(self,taskid):
		return [self.task[taskid]['complete'],self.task[taskid]['total']]

	def set_task(self,taskid,task_obj,task_value):
		self.task[taskid][task_obj] = task_value
		return True

	def set_task_add(self,taskid,task_obj,task_value):
		self.task[taskid][task_obj] += int(task_value)
		return True

	def set_task_append(self,taskid,task_obj,task_value):
		self.task[taskid][task_obj].append(task_value)
		return True

	def get_task_detail(self,*args):
		#这里的taskid是taskdetailid 我只是懒得改了...
		taskid = args[0]
		try:
			task_obj = args[1]
			return self.task_detail[taskid][task_obj]
		except:
			return self.task_detail[taskid]

	def get_task_detail_all(self):
		return self.task_detail


	def set_task_detail(self,taskid,task_obj,task_value):
		self.task_detail[taskid][task_obj] = task_value
		return True

	def set_task_detail_add(self,taskid,task_obj,task_value):
		self.task_detail[taskid][task_obj] += task_value
		return True

	def set_task_detail_append(self,taskid,task_obj,task_value):
		self.task_detail[taskid][task_obj].append(task_value)
		return True

	def task_detail_running_append(self,task_detail_id):
		self.task_detail_running.append(task_detail_id)

	def task_detail_running_remove(self,task_detail_id):
		self.task_detail_running.remove(task_detail_id)


class task_manager:
	def __init__(self,):
		from multiprocessing.managers import BaseManager
		class InspectionManager(BaseManager): pass
		self.InspectionManager = InspectionManager

	def test_conn(self,host,port,authkey):
		InspectionManager = self.InspectionManager
		m = InspectionManager(address=(host, port), authkey=bytes(authkey,encoding = "utf8"))
		try:
			m.connect()
			#m.shutdown()
			return True
		except Exception as e:
			#print(e)
			return False

	def conn(self,host,port,authkey,):
		InspectionManager = self.InspectionManager
		InspectionManager.register('task_queue')
		InspectionManager.register('inspection')
		InspectionManager.register('queue_relation')
		m = InspectionManager(address=(host, port), authkey=bytes(authkey,encoding = "utf8"))
		m.connect()
		self.m = m
		return m

	def start(self,host,port,authkey,inspection_instance):
		from queue import Queue
		InspectionManager = self.InspectionManager
		queue = Queue()
		queue_relation = Queue()
		InspectionManager.register('task_queue', callable=lambda:queue)
		InspectionManager.register('queue_relation', callable=lambda:queue_relation)
		InspectionManager.register('inspection',callable=lambda:inspection_instance)
		m = InspectionManager(address=(host, port), authkey=bytes(authkey,encoding = "utf8"))
		s = m.get_server()
		s.serve_forever()
		return True

	def close(self):
		return self.m.shutdown()
