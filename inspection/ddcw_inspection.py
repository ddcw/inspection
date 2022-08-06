#这个就是具体的巡检脚本了, 然后去队列里面找相关信息 
#q 巡检的队列
#c 要巡检的对象, 非文件形式(方便在线更新)
#l 打印日志的功能, 
#d 和父进程通信的字典
import time
import os
import sys
from . import log
from . import mysql_shell_conn
from . import format_mf
from . import coll_ana_data
def inspection(q,c,logfile,d,taskname):
	l = log.log(logfile=logfile, format_log="[{taskname}] [{osid}]".format(osid=os.getpid(), taskname=taskname))
	l.info("PID:{pid} BEGIN".format(pid=os.getpid()))
	while True:
		try:
			instance = q.get(block=False,timeout=10) #最多等10秒, 超过了就不管了
			time.sleep(1)
			#print(os.getpid(),"开始巡检    ",instance['port'])
		except:
			time.sleep(2)
			d['stat'] = 99 #表示这个进程结束了, 对应的监控进程也可以GG了
			l.info("PID:{pid} END".format(pid=os.getpid()))
			break

		#初始化日志, 记录每个实例的host和port
		l.format_log2("[{taskname}] [{osid}] {host}:{port}".format(osid=os.getpid(), taskname=taskname, host=instance['host'],port=instance['port']))

		#初始化d
		d['pid'] = os.getpid()
		d["type"] = c['GLOBAL']['Type']
		d["host"] = instance['host']
		d["port"] = instance['port']
		d["user"] = instance['user']
		d['begin_time'] = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())
		d['end_time'] = ""
		d['stat'] = 1
		d['running'] = "init"
		d['result'] = ""
		d['task_name'] = taskname
		d['score'] = 0
		#d['task_detail_name'] = "{host}_{port}_{time}".format(host=instance['host'],port=instance['port'],time=d['begin_time'])
		d['task_detail_name'] = "{host}_{port}_{time}".format(host=instance['host'],port=instance['port'],time=int(time.time()))
		#print(d['task_detail_name'])


		#校验数据库账号密码, 并生成连接信息
		instancef = format_mf.formatc(instance) #格式化, 把没得的对象补齐.
		cmysql = mysql_shell_conn.mysql(instancef)
		d['running'] = "连接mysql中..."
		l.info("连接mysql中...")
		if cmysql.status():
			conn = cmysql.conn()
			#cursor = conn.cursor()
			#cursor.execute("show databases");
			#data1 = cursor.fetchall()
			#print(data1)
		else:
			l.error("连接失败 {error}".format(error=cmysql.error))
			d['stat'] = 3
			d['end_time'] = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())
			d['running'] = "FAILED. See the log for details ({logfile})".format(logfile=logfile)
			#sys.exit(1)
			time.sleep(1)
			continue #巡检失败之后应该去队列里面找剩下的工作..... 但我允许休息1秒

		#采集主机信息, 最后才做的事情, 先写好而已
	#	d['running'] = "连接shell中..."
	#	if cshell.status():
	#		shell = cshell.conn()
	#	else:
	#		l.warning("无法巡检主机信息(自动跳过). {error}".format(error=cshell.error))


		#定义初始化信息采集结果
		result = {}

		d['running'] = "初始化固定采集信息..."
		l.info("开始采集固定信息(variables, status等)")
		#init() #获取固定采集数据
		initdata = coll_ana_data.init_data(conn)
		result['global_variables'] = initdata.global_variables()
		result['setup_instruments'] = initdata.setup_instruments()
		result['tables'] = initdata.tables()
		result['columns'] = initdata.columns()
		result['statement_analysis'] = initdata.statement_analysis()

		#收集global status
		d['running'] = "采集global status 预计 {s} 秒...".format(s=c['GLOBAL']['Data_collection_time'])
		l.info("采集global status 预计 {s} 秒...".format(s=c['GLOBAL']['Data_collection_time']))
		global_status_runtime = int(c['GLOBAL']['Data_collection_interval']) 
		time_col_0 = []
		global_status = initdata.global_status()['data']
		time_col_0.append(int(time.time()))
		time.sleep(c['GLOBAL']['Data_collection_interval'])
		while global_status_runtime < c['GLOBAL']['Data_collection_time']:
			global_status = global_status.append(initdata.global_status()['data'])
			time_col_0.append(int(time.time()))
			time.sleep(c['GLOBAL']['Data_collection_interval'])
			global_status_runtime += int(c['GLOBAL']['Data_collection_interval'])
			#d['running'] = "采集global status 剩余 {s} 秒...".format(s=int(c['GLOBAL']['Data_collection_time']) - global_status_runtime)
			#l.info("采集global status 剩余 {s} 秒...".format(s=int(c['GLOBAL']['Data_collection_time']) - global_status_runtime))
		
		global_status.insert(0,'time_col_0',time_col_0)
		result['global_status'] = {"status":True,"data":global_status}
		#print(result['global_status']['data'][['time_col_0','Uptime']])

		d['running'] = "global status采集完成, 即将开始巡检"
		l.info("global status采集完成, 即将开始巡检")

		#开始巡检
		#定义巡检保存结果在data里面
		data = {} #巡检结果项
		data1 = {} #汇总信息, 比如数据库信息, 巡检了多少项目, 有多少表, 多少库等
		#colldata = coll_ana_data.collanadata(conn=conn,global_variables=result['global_variables'],setup_instruments=result['setup_instruments'],tables=result['tables'],columns=result['columns'])
		colldata = coll_ana_data.collanadata(conn=conn,result=result,conf=c)
		total_score = 0 #总巡检项目的分
		get_score = 0 #总得分
		total_inspection_n = 0 #有多少巡检项
		inspection_n = 0 #巡检了多少项
		success_inspection_n = 0 #巡检成功了多少项
		inspection_error = 0 #巡检达到error级别
		inspection_warning = 0 #达到warning级别
		inspection_normal = 0
		radar = {}
		for x in c['INSPECTION']:
			total_inspection_n += 1
			#d['running'] = "正在巡检 {f}".format(f=x['Object_name'],)
			#time.sleep(0.3)
			try:
				abcdefg = x['Enabled'] 
			except Exception as e:
				l.info("自动启动巡检项 {f}".format(f=x['Object_name'],))
				x['Enabled'] = True
			if x['Enabled']:
				inspection_n += 1
				d["running"] = "巡检 {f}".format(f=x['Object_name'],)
				l.info("巡检 {f}".format(f=x['Object_name'],))
				execcmd = "data['{f}'] = colldata.{f}(x)".format(f=x['Object_name'],)
				exec(execcmd)
				data[x['Object_name']]['old_score'] = x['Score']
				data[x['Object_name']]['des'] = x['Des']
				data[x['Object_name']]['t1'] = x['Type']
				data[x['Object_name']]['enabled'] = x['Enabled']
				if data[x['Object_name']]['status']:
					d["running"] = "{f} OK".format(f=x['Object_name'],)
					total_score += x['Score']
					get_score += data[x['Object_name']]['score']
					success_inspection_n += 1
					if data[x['Object_name']]['type'] == 2:
						inspection_error += 1
					elif (data[x['Object_name']]['type'] == 1):
						inspection_warning += 1
					else:
						inspection_normal += 1
				else:
					d["running"] = "{f} FAILED".format(f=x['Object_name'])
					l.warning(data[x['Object_name']]['data'])
				#try:
				#	total_score += int(x['Score'])
				#	get_score += int(data[x['Object_name']]['score'])
				#except Exception as e:
				#	l.warning(e)
			else:
				l.warning("忽略巡检项:{f} ".format(f=x['Object_name']))
				continue

		#print(data['redundant_indexes'])
		#print("总分:{t1}   扣分:{t2}".format(t1=total_score, t2=get_score))
		score_percent2 = round(get_score/total_score*100,2)
		data1['total_score'] = total_score
		data1['get_score'] = get_score
		data1['score_percent'] = score_percent2
		data1['inspection_n'] = inspection_n
		data1['success_inspection_n'] = success_inspection_n
		data1['host'] = instance['host']
		data1['port'] = instance['port']
		data1['inspection_normal'] = inspection_normal
		data1['inspection_warning'] = inspection_warning
		data1['inspection_error'] = inspection_error


		#数据库角色判断中
		d['running'] = "正在识别数据库角色"
		#time.sleep(0.3)
		#data1['role'] = "主库"
		role = []
		#判断是否为从库
		if data['slave_info']['status']:
			try:
				if result['global_variables']['data']['rpl_semi_sync_master_wait_point'].values[0] == "AFTER_SYNC":
					role.append("从库(半同步)")
				elif result['global_variables']['data']['rpl_semi_sync_master_wait_point'].values[0] == "AFTER_COMMIT":
					role.append("从库(增强半同步)")
				else:
					role.append("从库")
			except Exception as e:
				role.append("从库")
				#_tmp_data = "SLAVE INFO: {e}".format(e=str(e))
				#l.warning(_tmp_data)
		
		#判断是否为PXC集群
		if data['pxc_info']['status']:
			role.append("PXC集群")

		#判断是否为MGR集群
		if data['mgr_info']['status']:
			try:
				if result['global_variables']['data']['group_replication_single_primary_mode'].values[0] == "ON":
					if result['global_status']['data'].tail(1)['group_replication_primary_member'].values[0] == result['global_variables']['data']['server_uuid'].values[0]:
						role.append("MGR集群 主节点(单主模式)")
					else:
						role.append("MGR集群 从节点(单主模式)")
				else:
					mode = "MGR集群 (多主模式)"
			except Exception as e:
				print("MGR: ",data['mgr_info'])
				_tmp_data = "MGR INFO: {e}".format(e=str(e))
				l.warning(_tmp_data)

		#判断是否为主库  #(show slave hosts;)
		if data['master_info']['status']:
			try:
				role.append('主库(可能有{n}个从库)'.format(n=len(data['master_info']['data'])))
			except Exception as e:
				pass
				_tmp_data = "MASTER INFO: {e}".format(e=str(e))
				l.warning(_tmp_data)


		#判断是否为空
		if len(role) == 0:
			data1['role'] = ['普通库']
		else:
			data1['role'] = role

		#生成雷达图数据[32,12,83,19,45,33]
		data1['radar'] = {}
		_tmp_radar_1 = {} #总分
		_tmp_radar_2 = {} #得分 计算百分比
		for x in data:
			radar_name = data[x]['t1']
			try:
				_tmp_radar_1[radar_name] += data[x]['old_score']
				_tmp_radar_2[radar_name] += data[x]['score']
			except:
				_tmp_radar_1[radar_name] = data[x]['old_score']
				_tmp_radar_2[radar_name] = data[x]['score']
				
				
		for y in _tmp_radar_1:
			data1['radar'][y] = round(_tmp_radar_2[y]/_tmp_radar_1[y]*100,)

		
		
		data1['radar_total_score'] = _tmp_radar_1
		data1['radar_get_score'] = _tmp_radar_2


		#转换成列表
		data1['radar_list1'] = []
		data1['radar_list2'] = []
		for z in data1['radar']:
			if z == 1:
				zname = '安全与稳定'
			elif z == 2:
				zname = '性能与规范'
			elif z == 3:
				zname = '高可用'
			elif z == 4:
				zname = '资源'
			elif z == 5:
				zname = '基础信息'
			elif z == 6:
				zname = '其它'
			else :
				zname = '其它'
			data1['radar_list1'].append(zname)
			data1['radar_list2'].append(data1['radar'][z])


		#巡检时间 定义为巡检开始时间
		data1['inspection_time'] = d['begin_time']


		#MYSQL版本
		try:
			data1['mysql_version'] = result['global_variables']['data']['version'].values[0]
		except:
			data1['mysql_version'] = 'unknown'

#		print("总分: {t}  得分: {g} {percent}%".format(t=data1['total_score'], g=data1['get_score'], percent=score_percent2))
#		try:
#			for x in c['INSPECTION']:
#				objname = x["Object_name"]
#				try:
#					print(objname,data[objname]['score'],'/',x['Score'])
#				except:
#					pass
#		except:
#			pass
#
		#print(data['auto_increment_columns'])
		#print(data1)
		#print(data['table_fragment']['data'])

		#print("\n",data['mgr_info'])


		data2 = {} #主机巡检信息
		data2['havedata'] = False
		#开始主机信息巡检
		if c['GLOBAL']['Enable_Shell']:	
			l.info('开始主机巡检')
			cshell = mysql_shell_conn.shell(instancef)
			d['running'] = "连接shell中..."
			if cshell.status():
				shell = cshell.conn()
				from . import host_inspection
				host_instance_1 = host_inspection.inspection(shell,result,c['GLOBAL']['Mysql_Error_Log'],c['GLOBAL']['Mysql_Slow_Log'])
				d['running'] = "巡检主机信息中..."
				l.info('巡检主机信息中....')
				host_data = host_instance_1.run()
				if host_data['status']:
					l.info('主机信息巡检完成')
					d['running'] = "主机信息巡检完成"
				else:
					l.warning('主机巡检失败,{error}'.format(error=host_data['data']))
				data2['data'] = host_data
				data2['havedata'] = True
			else:
				l.warning("无法巡检主机信息(自动跳过). {error}".format(error=cshell.error))
				d['running'] = "无法巡检主机信息(自动跳过). {error}".format(error=cshell.error)
		else:
			l.warning('忽略主机信息巡检')
			d['running'] = '忽略主机信息巡检'


		#根据巡检结果生成巡检报告
		report_result = ""
		report_filename = "{host}_{port}_{taskname}".format(host=instance['host'],port=instance['port'],taskname=taskname) #不含后缀
		if c['GLOBAL']['Type'] == "html":
			from . import report_html
			report_result = report_html.get_result(data,data1,c,report_filename,data2)
		elif c['GLOBAL']['Type'] == "word":
			report_result = "待完成"

		elif c['GLOBAL']['Type'] == "xls":
			report_result = "待完成"

		elif c['GLOBAL']['Type'] == "csv":
			report_result = "待完成"

		else:
			report_result = "xxx.json" #原始巡检数据


		d['stat'] = 2
		d['result'] = report_result
		#break
		conn.close() #关闭mysql连接 每个实例
		d['running'] = "巡检完成"
		d['end_time'] = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())
		d['score'] = data1['score_percent']
		l.info("巡检完成")

		#下一次初始化前, 等待监控线程同步完信息..
		time.sleep(2)

	l.close() #关闭日志 这个进程
	return True
