from . import manager_inspection
import sys,time,os
from . import log
from inspection import hashstr
import uuid
from . import mysql_shell_conn,format_mf,coll_data
import yaml
import datetime
from . import anadata
from . import report_docx,report_html
from . import host_inspection
from . import role_format
from . import parseXML
def inspection(**kwargs):
	c = kwargs['conf']
	pid = os.getpid()
	manager_host = c['MANAGER']['host']
	manager_port = c['MANAGER']['port']
	manager_authkey = hashstr.hash1(c['MANAGER']['authkey'])

	#打开日志文件
	logfile = c['OTHER']['logfile']
	if (logfile is None) or logfile == "":
		logfile = "logs/work_{pid}_{time}.log".format(pid=pid, time=time.strftime("%Y%m%d_%H%M%S", time.localtime()))
	logfile = os.path.abspath(logfile) #格式化为绝对路径
	logfile_dir = os.path.dirname(logfile)
	os.makedirs(logfile_dir, exist_ok = True) #创建日志目录
	l = log.log(logfile=logfile, format_log="[{osid}]".format(osid=pid,))
	l.info('WORK {pid} BEGIN'.format(pid=pid,))

	#连接manager
	manager_instance = manager_inspection.task_manager()
	if manager_instance.test_conn(manager_host,manager_port,manager_authkey):
		l.info('manager连接成功')
	else:
		l.error('manager连接失败, 即将退出..')
		sys.exit(1)

	m = manager_instance.conn(manager_host,manager_port,manager_authkey)
	q = m.task_queue() #将要巡检的队列
	inspection = m.inspection() #task相关的信息
	

	#初始化进程相关信息
	process_id = '{hostname}_{pid}'.format(hostname=os.uname().nodename, pid=pid)
	inspection.set_process(process_id,0)
	

	#使用全局的巡检项配置(TODO), 现在就读取本机的配置文件...
	with open(c['OTHER']['inspection'], 'r', encoding="utf-8") as f:
		inf_data =  f.read()
	inspection_item = yaml.load(inf_data,Loader=yaml.Loader)['INSPECTION']

	#等待巡检队列
	while True:
		#instance = q.get(block=False,timeout=10)
		instance = q.get() #获取要巡检的信息

		if inspection.get_process(process_id) == 2:
			#inspection.set_process(pid,2)
			inspection.set_process(process_id,2)
			#q.put(instance) #又放回去了..... 好像放不回去了...
			#print('放回去了?',instance)
			#break
		else:
			#inspection.set_process(pid,1)
			inspection.set_process(process_id,1)
	
		

		taskid = instance['taskid']
		req = instance['data'] #是否要采集数据的标示
		try:
			host = instance['host']
			port = instance['port']
			user = instance['user']
			password = instance['password']
			sshport = instance['sshport']
			sshuser = instance['sshuser']
			sshpassword = instance['sshpassword']
			sshenable = instance['sshenable'] #是否启用SSH, 也就是是否巡检主机信息
			sshforce = instance['sshforce'] #是否强制要求SSH
		except:
			host = 'None'
			port = 0
			user = 'None'
			pass
		task_detail_id = uuid.uuid1().hex   #初始化task_detail_id  uuid1含MAC地址

		#初始化task_detail (巡检实例)
		inspection.init_task_detail(taskid,task_detail_id)
		inspection.set_task_detail(task_detail_id,'host',host)
		inspection.set_task_detail(task_detail_id,'port',port)
		inspection.set_task_detail(task_detail_id,'user',user)

		inspection.set_task_add(taskid,'running',1)
		#inspection.set_process(pid,1)
		inspection.task_detail_running_append(task_detail_id)
		inspection.set_task_append(taskid,'list',task_detail_id)

		#判断是否有数据, 没得就连接mysql读取数据, 有就把对应的数据传递给分解脚本(计算得分,建议之类的)

		begin_time = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())
		def msg1(msg):
			l.info(msg)
			inspection.set_task_detail(task_detail_id,'running',msg)

		#校验MSYQL和SSH连接 (没得数据的时候才会用到mysql和ssh连接)
		instancef = format_mf.formatc(instance) #格式化连接信息
		if not req['havedata']:
			msg1('开始测试MYSQL连接信息.')
			cmysql = mysql_shell_conn.mysql(instancef)
			if cmysql.status():
				conn = cmysql.conn()
				mysql_com = coll_data.init_data(conn) #
				inspection.set_task_detail(task_detail_id,'mysqlstatus',True)
			else:
				msg = '{host}:{port} MYSQL连接失败: {e} 请查看日志({logfile})'.format(e=cmysql.error, logfile=logfile,host=host,port=port)
				l.error(msg)
				inspection.set_task_detail(task_detail_id,'running',msg)
				inspection.set_task_detail(task_detail_id,'stat',3)
				inspection.set_task_detail(task_detail_id,'mysqlstatus',False)
				#更新task信息
				inspection.set_task_add(taskid,'complete',1)
				inspection.set_task_add(taskid,'running',-1)
				inspection.set_task_add(taskid,'fail',1)
				continue

			if sshenable == 'True':
				cshell = mysql_shell_conn.shell(instancef)
				if cshell.status():
					shell = cshell.conn()
					inspection.set_task_detail(task_detail_id,'sshstatus',True)
				elif sshforce == 'True':
					msg = 'SSH连接失败, 因为sshforce=True, 所以即将退出巡检'
					l.error(msg)
					inspection.set_task_detail(task_detail_id,'running',msg)
					inspection.set_task_detail(task_detail_id,'stat',3)
					inspection.set_task_detail(task_detail_id,'sshstatus',False)
					sshenable = False
					#更新task信息
					inspection.set_task_add(taskid,'complete',1)
					inspection.set_task_add(taskid,'running',-1)
					inspection.set_task_add(taskid,'fail',1)
					continue
				else:
					msg = 'SSH连接失败, 忽略主机巡检'
					l.error(msg)
					inspection.set_task_detail(task_detail_id,'sshstatus',False)
					sshenable = False

		else:
			#从主节点获取采集的数据(http传输)
			inspection_from_shell_data_filename = req['data']
			#然后传递到本地(TODO)
			inspection_from_shell_data_local_filename = inspection_from_shell_data_filename
			inspection_from_shell_data = parseXML.return_obj(inspection_from_shell_data_local_filename)
			#初始化实例信息
			inspection.set_task_detail(task_detail_id,'host',inspection_from_shell_data['baseinfo']['host'])
			inspection.set_task_detail(task_detail_id,'port',inspection_from_shell_data['baseinfo']['port'])
			host = inspection_from_shell_data['baseinfo']['host']
			port = inspection_from_shell_data['baseinfo']['port']
		
		inspection.set_task_detail(task_detail_id,'stat',1)
		#持续巡检项
		if req['havedata']:
			#根据rep['data']的文件解析 data1 (持续采集数据)
			msg1('开始读取持续巡检项')
			data1 = inspection_from_shell_data['data1']
			#print('TO BE CONTINED')
		else:
			msg1('开始采集固定巡检项 (预计{s}秒)'.format(s=c['MYSQL']['data_collection_time']))
			data1 = mysql_com.global_status(c['MYSQL']['data_collection_time'],c['MYSQL']['data_collection_interval'])
			#print(data1)

		#持续巡检项的分析(其实就是生成一些画图需要的数据)
		msg1('分析持续巡检项')
		data1_result = {}
		data1_result['data'] = {}
		if data1['status']:
			data1_result['status'] = True
			data1['data']['_commit_rollback'] = data1['data']['Com_commit'].astype('float64') + data1['data']['Com_rollback'].astype('float64')
			time_seq = data1['data']['time_col_0'].iloc[1:].values #时间序列
			data1_result['data']['time_seq'] = [datetime.datetime.utcfromtimestamp(i).strftime("%Y-%m-%d %H:%M:%S") for i in time_seq]
			list_data1 = ['Bytes_received', 'Bytes_sent', 'Innodb_dblwr_writes', 'Innodb_data_read', 'Innodb_data_written', 'Innodb_os_log_written', 'Queries','_commit_rollback', 'Com_select', 'Com_delete', 'Com_update', 'Com_insert',]
			for x in list_data1:
				data1['data'][x] = data1['data'][x].astype('float64')
				data1_result['data'][x] = data1['data'][x].diff(periods=1,).iloc[1:].values
			#data1_result['data']['Innodb_dblwr_writes'] = data1['data']['Innodb_dblwr_writes'].diff(periods=1,).iloc[1:].values
		else:
			data1_result['status'] = False

		#print(data1_result)

		#固定巡检项 (集群相关信息也得在这里采集了, 因为它不止一条SQL...)
		if req['havedata']:
			msg1('开始读取固定采集项')
			data2 = inspection_from_shell_data['data2']
			#print('TO BE CONTINED')
		else:
			msg1('开始采集固定采集项')
			data2 = {}
			data2['global_variables'] = mysql_com.run_sql2('show global variables;')
			data2['global_status'] = mysql_com.run_sql2('show global status;')
			data2['sys.metrics'] = mysql_com.run_sql('select * from metrics;')
			data2['sys.memory_global_total'] = mysql_com.run_sql('select * from sys.memory_global_total;')
			data2['slave_status'] = mysql_com.run_sql('show slave status;')
			data2['performance_schema.replication_group_members'] = mysql_com.run_sql('select * from performance_schema.replication_group_members;') #MGR集群节点状态
			data2['performance_schema.replication_group_member_stats'] = mysql_com.run_sql('select * from performance_schema.replication_group_member_stats;') #MGR自己状态
			data2['master_info'] = mysql_com.run_sql("select * from information_schema.processlist where COMMAND = 'Binlog Dump';") #查看主库又多少从库, show slave host 可能不行
			data2['db_table_info'] = mysql_com.run_sql("select bb.*,aa.DEFAULT_CHARACTER_SET_NAME from information_schema.SCHEMATA as aa left join (select table_schema, sum(data_length) as data_length, sum(index_length) as index_length from information_schema.tables where TABLE_SCHEMA not in ('sys','mysql','information_schema','performance_schema') group by table_schema) as bb on aa.SCHEMA_NAME=bb.table_schema where bb.table_schema is not null;")

		#固定巡检项分析
		#分析个P, 后面再考虑...
		data2_result = {'status':True,'data':data2}

		#巡检项
		if req['havedata']:
			#colldata = anadata.anadata1(global_conf=c,data2=data2)
			#colldata = inspection_from_shell_data['data3']
			colldata = anadata.anadata1(global_conf=c, data2=data2,)  #没必要把mysql_com传递过去,反正数据是在这里读取的
		else:
			#colldata = anadata.anadata1(global_conf=c, mysql_com=mysql_com,data2=data2)
			colldata = anadata.anadata1(global_conf=c, data2=data2, conn=conn) #没必要把mysql_com传递过去,反正数据是在这里读取的
		msg1('开始巡检')
		inspection_data_result = {}
		inspection_total = 0 #总的巡检数(含未启用的)
		inspection_enable = 0 #启用的巡检数
		inspection_success = 0 #巡检成功的数
		inspection_fail = 0 #巡检失败的
		inspection_level_1 = 0 #巡检告警为 1 的 (正常)
		inspection_level_2 = 0 #巡检告警为 2 的 
		inspection_level_3 = 0 #巡检告警为 3 的
		inspection_level_4 = 0 #巡检告警为 4 的
		inspection_level_5 = 0 #巡检告警为 5 的
		inspection_suggestion = [] #巡检建议,是个列表
		inspection_score_total = 0 #巡检成功的总分
		inspection_score_get = 0 #巡检成功的得分
		inspection_score_percent = 0 #得分(百分比, inspection_score_get/inspection_score_total)
		for x in inspection_item:
			inspection_total += 1
			x['enabled'] = True if 'enabled' not in x else x['enabled'] #默认启用巡检项
			if x['enabled']:
				inspection_enable += 1
				msg1('巡检{xj} ({des})'.format(xj=x['object_name'],des=x['des']))

				if req['havedata']:
					#print('读取xml文件, 获取当前的信息, 其实只有第一次读取了的, 后面都是直接取 ,但后面在写吧')
					if x['object_name'] == 'simple_password':
						continue
					data = {'status':True,'data':inspection_from_shell_data['data3'][x['object_name']]}
				elif x['sql'] is not None:
					data = mysql_com.run_sql(x['sql'])
				else:
					data = {'status':True,'data':''}

				if not data['status']:
					msg = '{xob} 数据为空, 将跳过. {err}'.format(xob=x['object_name'], err=data['data'])
					msg1(msg)
					inspection_data_result[x['object_name']] = {}
					inspection_data_result[x['object_name']]['status'] = False
					continue
				execcmd = 'inspection_data_result["{f}"] = colldata.{f}(x,data)'.format(f=x['object_name'])
				exec(execcmd)
				#print(inspection_data_result[x['object_name']])
				if inspection_data_result[x['object_name']]['status']:
					inspection_success += 1
					if 'data' not in inspection_data_result[x['object_name']]:
						inspection_data_result[x['object_name']]['data'] = data['data']
						inspection_data_result[x['object_name']]['data_rows'] = data['data'].shape[0]
					if inspection_data_result[x['object_name']]['suggestion'] != '' and inspection_data_result[x['object_name']]['level'] > 1:
						inspection_suggestion.append(inspection_data_result[x['object_name']]['suggestion'])
					inspection_score_total += x['score']
					inspection_score_get += inspection_data_result[x['object_name']]['score']
					if inspection_data_result[x['object_name']]['level'] == 1:
						inspection_level_1 += 1
					elif inspection_data_result[x['object_name']]['level'] == 2:
						inspection_level_2 += 1
					elif inspection_data_result[x['object_name']]['level'] == 3:
						inspection_level_3 += 1
					elif inspection_data_result[x['object_name']]['level'] == 4:
						inspection_level_4 += 1
					elif inspection_data_result[x['object_name']]['level'] == 5:
						inspection_level_5 += 1
				else:
					inspection_fail += 1
				#inspection_data_result[x['object_name']]['status'] = 1

		#关闭MYSQL连接
		if not req['havedata']:
			conn.close()

		#节点关系信息剥离
		relation_data = {}
		for x in ['master_info','slave_info','pxc_info','mgr_info']:
			try:
				relation_data[x] = {'status':True,'data':inspection_data_result[x]}
			except:
				relation_data[x] = {'status':False,'data':''}
		role = role_format.get_role(relation_data,data2['global_variables'],data2['global_status'],) 
		role = ['普通库'] if len(role) == 0 else role

		#主机巡检相关信息 
		#print(inspection_data_result)
		if req['havedata']:
			hostdata = inspection_from_shell_data['hostdata']
		else:
			if sshenable == 'True':
				hostinstance_1 = host_inspection.inspection(shell,{'global_variables':data2['global_variables']},c['HOST'])
				hostdata = hostinstance_1.run()
				hostdata['data']['dirstatus'] = True
			else:
				hostdata = {'status':False,'data':''}
	
		end_time = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())
		try:
			inspection_score_percent = round(inspection_score_get/inspection_score_total*100,0)
		except:
			inspection_score_percent = 0
		#生成 mysqldata  baseinfo(同task_detail['xx']['baseinfo']) 
		baseinfo = {}
		baseinfo['taskid'] = taskid
		baseinfo['task_detail_id'] = task_detail_id
		baseinfo['begin_time'] = begin_time
		baseinfo['end_time'] = end_time
		baseinfo['score'] = inspection_score_percent
		baseinfo['host'] = host
		baseinfo['port'] = port
		baseinfo['version'] = data2['global_variables']['data']['version'].values[0]
		baseinfo['uptime'] = round(int(data2['global_status']['data']['Uptime'].values[0])/60/60/24,2)
		baseinfo['mem_total'] = data2['sys.memory_global_total']['data'].values[0][0]
		baseinfo['inspection_level_1'] = inspection_level_1
		baseinfo['inspection_level_2'] = inspection_level_2
		baseinfo['inspection_level_3'] = inspection_level_3
		baseinfo['inspection_level_4'] = inspection_level_4
		baseinfo['inspection_level_5'] = inspection_level_5
		baseinfo['inspection_success'] = inspection_success
		baseinfo['inspection_fail'] = inspection_fail
		baseinfo['role'] = role
		baseinfo['report_dir'] = c['OTHER']['report_dir'] #巡检报告保存的目录.
		baseinfo['online'] = c['OTHER']['online'] #仅HTML模板要...
		#一些命中率.... (x100 不带百分号)
		try:
			baseinfo['key_buffer_read_hits'] = round((1-int(data2['global_status']['data']['Key_reads'].values[0])/int(data2['global_status']['data']['Key_read_requests'].values[0]))*100,2)
		except Exception as e:
			msg1(e)
			baseinfo['key_buffer_read_hits'] = -1
		try:
			baseinfo['key_buffer_write_hits'] = round((1-int(data2['global_status']['data']['Key_writes'].values[0])/int(data2['global_status']['data']['Key_write_requests'].values[0]))*100,2)
		except Exception as e:
			msg1(e)
			baseinfo['key_buffer_write_hits'] = -1
		try:
			baseinfo['query_cache_hits'] = round(int(data2['global_status']['data']['Qcache_hits'].values[0])/(int(data2['global_status']['data']['Qcache_hits'].values[0])+int(data2['global_status']['data']['Qcache_inserts'].values[0])),2)
		except Exception as e:
			msg1(e)
			baseinfo['query_cache_hits'] = -1
		try:
			baseinfo['innodb_buffer_read_hits'] = round((1-int(data2['global_status']['data']['Innodb_buffer_pool_reads'].values[0])/(int(data2['global_status']['data']['Innodb_buffer_pool_reads'].values[0])+int(data2['global_status']['data']['Innodb_buffer_pool_read_requests'].values[0])+int(data2['global_status']['data']['Innodb_buffer_pool_read_ahead'].values[0])))*100,2)
		except Exception as e:
			msg1(e)
			baseinfo['innodb_buffer_read_hits'] = -1
		try:
			baseinfo['table_open_cache_hits'] = round((int(data2['global_status']['data']['Table_open_cache_hits'].values[0])/(int(data2['global_status']['data']['Table_open_cache_hits'].values[0])+int(data2['global_status']['data']['Table_open_cache_misses'].values[0])))*100,2)
		except Exception as e:
			msg1(e)
			baseinfo['table_open_cache_hits'] = -1
		#内存使用
		try:
			baseinfo['innodb_mem_used_p'] = round(int(data2['global_status']['data']['Innodb_buffer_pool_pages_data'].values[0])/int(data2['global_status']['data']['Innodb_buffer_pool_pages_total'].values[0])*100,2)
		except Exception as e:
			msg1(e)
			baseinfo['innodb_mem_used_p'] = -1
		baseinfo['innodb_mem_total'] = round(int(data2['global_status']['data']['Innodb_buffer_pool_bytes_data'].values[0])/1024/1024,2) #MB
		#建议
		baseinfo['inspection_suggestion'] = inspection_suggestion
		#库表信息
		baseinfo['db_table'] = data2['db_table_info']

		#雷达图要的数据(word版不支持)
		baseinfo['radar'] = {}
		_tmp_radar_1 = {} #总分
		_tmp_radar_2 = {} #得分 计算百分比
		for x in inspection_data_result:
			if inspection_data_result[x]['status']:
				radar_type = inspection_data_result[x]['type']
				try:
					_tmp_radar_1[radar_type] += inspection_data_result[x]['old_score']
					_tmp_radar_2[radar_type] += inspection_data_result[x]['score']
				except:
					_tmp_radar_1[radar_type] = inspection_data_result[x]['old_score']
					_tmp_radar_2[radar_type] = inspection_data_result[x]['score']

		for y in _tmp_radar_1:
			try:
				baseinfo['radar'][y] = round(_tmp_radar_2[y]/_tmp_radar_1[y]*100,0)
			except:
				baseinfo['radar'][y] = 100

		baseinfo['radar_name'] = []
		baseinfo['radar1'] = []
		for z in baseinfo['radar']:
			baseinfo['radar_name'].append(c['OTHER']['inspection_type'][z][0])
			baseinfo['radar1'].append(baseinfo['radar'][z])
				

		#print(baseinfo)
		#print(data1_result['data']['Bytes_received'],data1_result['data']['time_seq'])

		#测试的时候太快了, 所以sleep(10)
		#time.sleep(7)

		#生成巡检报告
		report_result = [] #{'type:html, status:True,data:xxx.html'}
		if c['OTHER']['report_html']:
			report_result.append(report_html.run(c,data1_result,baseinfo,inspection_data_result,hostdata))
		if c['OTHER']['report_docx']:
			report_result.append(report_docx.run(c,data1_result,baseinfo,inspection_data_result,hostdata))


		inspection.set_task_detail(task_detail_id,'result',report_result)
		inspection.set_task_detail(task_detail_id,'end_time',end_time)
		inspection.set_task_detail(task_detail_id,'running','巡检完成')
		inspection.set_task_detail(task_detail_id,'score',inspection_score_percent)
		inspection.set_task_detail(task_detail_id,'baseinfo',baseinfo)
		inspection.set_task_detail(task_detail_id,'relation_data',relation_data)
		inspection.set_task_detail(task_detail_id,'role',role)
		inspection.set_task_detail(task_detail_id,'stat',2)


		#完成此个实例的巡检 (节点之间的关系由 web_console 计算)

		#更新task信息
		inspection.set_task_add(taskid,'complete',1)
		inspection.set_task_add(taskid,'running',-1)

		inspection.task_detail_running_remove(task_detail_id)
		


		#设置这个进程的状态
		if inspection.get_process(process_id) == 2:
			l.warning('收到退出信号, 本进程退出了..')
			break
		else:
			#inspection.set_process(pid,0)
			inspection.set_process(process_id,0)
	
		msg1('巡检完成. 巡检报告:{report}'.format(report=report_result))
