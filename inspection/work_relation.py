import sys,time,os
from inspection import hashstr
from . import manager_inspection
def relation(**kwargs):
	c = kwargs['conf']
	csvdir = os.path.abspath(c['OTHER']['node_relation_file'])
	manager_host = c['MANAGER']['host']
	manager_port = c['MANAGER']['port']
	manager_authkey = hashstr.hash1(c['MANAGER']['authkey'])
	manager_instance = manager_inspection.task_manager()
	if manager_instance.test_conn(manager_host,manager_port,manager_authkey):
		pass
	else:
		print('连接失败, 即将退出relation_work')
		sys.exit(1)

	m = manager_instance.conn(manager_host,manager_port,manager_authkey)
	queue_relation = m.queue_relation() #要生成节点关系的taskid队列
	inspection = m.inspection()


	while True:
		taskid = queue_relation.get()
		nodelist = {} #存在的节点信息 {"host:port":score}
		master_dict = {}
		slave_dict = {}
		mgr_dict = {}
		pxc_dict = {}
		csvname = 'relation_{taskid}.csv'.format(taskid=taskid)
		csvfullname = '{csvdir}/{csvname}'.format(csvdir=csvdir,csvname=csvname)
		print('即将开始分析节点关系....',taskid) 
		while inspection.get_task(taskid)['complete'] < inspection.get_task(taskid)['total']:
			time.sleep(1)
		task_instance = inspection.get_task(taskid)
		taskdetail_list = task_instance['list']
		print('开始分析节点关系',taskid)
		for x in taskdetail_list:
			instance = inspection.get_task_detail(x)
			relation_data = instance['relation_data']
			host = instance['host']
			port = instance['port']
			score = instance['score']
			hp = '{host}:{port}'.format(host=host,port=port)
			nodelist[hp] = score
			if 'master_info' in relation_data:
				if relation_data['master_info']['status']:
					if relation_data['master_info']['data']['status'] and relation_data['master_info']['data']['data'].shape[0] > 1:
						master_dict[hp] = []
						for y in relation_data['master_info']['data']['data'].values:
							try:
								master_dict[hp].append(y[2])
							except:
								pass
							
				#print(relation_data['master_info'])

			if 'slave_info' in relation_data:
				if relation_data['slave_info']['status']:
					if relation_data['slave_info']['data']['status']:
						for y in relation_data['slave_info']['data']['data'].values:
							slave_hp = '{host}:{port}'.format(host=y[1],port=y[2])
							if slave_hp not in master_dict:
								master_dict[slave_hp] = []
							try:
								master_dict[slave_hp].append(hp)
							except:
								pass
				#print(relation_data['slave_info'])

			if 'mgr_info' in relation_data:
				if relation_data['mgr_info']['status']:
					if relation_data['mgr_info']['data']['status']:
						for y in relation_data['mgr_info']['data']['data'].values:
							group_name = y[1]
							if group_name not in mgr_dict:
								mgr_dict[group_name] = []
							for z in y[0].split(','):
								try:
									mgr_dict[group_name].append(z)
								except:
									pass
				#print(relation_data['mgr_info'])

			if 'pxc_info' in relation_data:
				if relation_data['pxc_info']['status']:
					if relation_data['pxc_info']['data']['status']:
						wsrep_cluster_name = relation_data['pxc_info']['data']['data']['wsrep_cluster_name'].values[0]
						wsrep_cluster_address = relation_data['pxc_info']['data']['data']['wsrep_cluster_address'].values[0]
						if wsrep_cluster_name not in pxc_dict:
							pxc_dict[wsrep_cluster_name] = []
						for y in wsrep_cluster_address.split('//')[1].split(','):
							try:
								pxc_dict[wsrep_cluster_name].append(y)
							except:
								pass
				#print(relation_data['pxc_info'])


			#print("MGR_INFO:", mgr_dict)
			#print("PXC_INFO:", pxc_dict)
			#print("MASTER_INFO:", master_dict)

		#csvfullname
		with open(csvfullname,'a',encoding="utf-8") as f:
			for x in master_dict:
				try:
					fw1 = '主从,{hp}(主),{score}\n'.format(hp=x,score=nodelist[x])
				except:
					fw1 = '主从,{hp}(主),\n'.format(hp=x,)
				f.write(fw1)
				#先去重
				master_dict[x] = list(set(master_dict[x]))
				for y in master_dict[x]:
					try:
						wf = ',{hp}(从),{score}\n'.format(hp=y,score=nodelist[y])
					except:
						wf = ',{hp}(从),\n'.format(hp=y,)
					f.write(wf)
				f.write(',,\n')

			for x in mgr_dict:
				f.write('MGR集群({name})'.format(name=x))
				mgr_dict[x] = list(set(mgr_dict[x]))
				for y in mgr_dict[x]:
					try:
						f.write(',{y},{score}\n'.format(y=y,score=nodelist[y]))
					except:
						f.write(',{y},\n'.format(y=y,))
				f.write(',,\n')

			for x in pxc_dict:
				f.write('PXC集群({name})'.format(name=x))
				pxc_dict[x] = list(set(pxc_dict[x]))
				for y in pxc_dict[x]:
					try:
						f.write(',{y},{score}\n'.format(y=y,score=nodelist[y]))
					except:
						f.write(',{y},\n'.format(y=y,))
				f.write(',,\n')


		inspection.set_task(taskid,'relation',csvname)
