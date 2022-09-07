
def get_relation_csv(taskid,inspection_task,csvdir):
	csvname = 'relation_{taskid}.csv'.format(taskid=taskid)
	taskdetail_list = inspection_task.get_task(taskid)['list']
	nodelist = [] #保存所有存在节点
	master_dict = {}
	slave_dict = {}
	mgr_dict = {}
	pxc_dic = {}
	for x in taskdetail_list:
		relation_data = inspection_task.get_task_detail(x)['relation_data']
		if 'master_info' in relation_data:
			print(relation_data['master_info'])

		if 'slave_info' in relation_data:
			print(relation_data['slave_info'])

		if 'mgr_info' in relation_data:
			print(relation_data['mgr_info'])

		if 'pxc_info' in relation_data:
			print(relation_data['pxc_info'])
	return csvname
