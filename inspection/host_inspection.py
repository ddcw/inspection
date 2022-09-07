class inspection:
	def __init__(self,shell,result,c):
		self.shell = shell
		file_list = {}
		dir_list = {}
		if result['global_variables']['status']:
			global_variables = result['global_variables']['data'].tail(1)
			dir_list['datadir']=global_variables['datadir']
			dir_list['redodir']=global_variables['innodb_data_home_dir']
			dir_list['binlogdir']=global_variables['log_bin_index']
			dir_list['tmpdir']=global_variables['tmpdir']

			file_list['slow_query_log_file']=global_variables['slow_query_log_file']
			file_list['error_log_file']=global_variables['log_error']
		self.file_list = file_list
		self.dir_list = dir_list
		self.global_variables = global_variables
		self.Mysql_Error_Log = c['mysql_error_log']
		self.Mysql_Slow_Log = c['mysql_slow_log']
			

	def run(self):
		shell = self.shell
		hostinfo = {}

		#CPU部分
		hostinfo["cpu_socket"] = shell.get_result_dict("lscpu | grep 'Socket(s)' | awk '{print $NF}'")
		hostinfo["cpu_core"] = shell.get_result_dict("lscpu | grep 'Core(s)' | awk '{print $NF}'")
		hostinfo["cpu_thread"] = shell.get_result_dict("lscpu | grep 'Thread(s)' | awk '{print $NF}'")
		hostinfo["cpu_name"] = shell.get_result_dict("""lscpu | grep name | awk '$1="";$2=""; {print $0}'""")

		#内存部分(含swap) 大页能提高innodb性能, 但是不明显(百分之几), 又太麻烦, 所以不建议使用大页
		hostinfo['mem_total'] = shell.get_result_dict("""cat /proc/meminfo | awk  '{ if ( $1 == "MemTotal:") print $2}'""")
		hostinfo['mem_total']['stdout'] = round(int(hostinfo['mem_total']['stdout'])/1024/1024,2)
		hostinfo['mem_free'] = shell.get_result_dict("""cat /proc/meminfo | awk  '{ if ( $1 == "MemFree:") print $2}'""")
		hostinfo['mem_free']['stdout'] = round(int(hostinfo['mem_free']['stdout'])/1024/1024,2)
		hostinfo['mem_available'] = shell.get_result_dict("""cat /proc/meminfo | awk  '{ if ( $1 == "MemAvailable:") print $2}'""") #centos 6.5等版本无此选项 可以内存计算较为复杂, 后续版本再考虑是否计算
		hostinfo['mem_available']['stdout'] = round(int(hostinfo['mem_available']['stdout'])/1024/1024,2)

		#swappiness建议为1,  MYSQL要尽可能的使用内存, 但是又不能宕掉...
		hostinfo["swappiness"] = shell.get_result_dict("cat /proc/sys/vm/swappiness")
		hostinfo['swap_total'] = shell.get_result_dict("""cat /proc/meminfo | awk  '{ if ( $1 == "SwapTotal:") print $2}'""")
		hostinfo['swap_total']['stdout'] = round(int(hostinfo['swap_total']['stdout'])/1024/1024,2)
		hostinfo['swap_free'] = shell.get_result_dict("""cat /proc/meminfo | awk  '{ if ( $1 == "SwapFree:") print $2}'""")
		hostinfo['swap_free']['stdout'] = round(int(hostinfo['swap_free']['stdout'])/1024/1024,2)

		#numactl部分  #计划 v2.4版本
		#hostinfo['numactl_show'] = shell.get_result_dict("numactl --show")


		#mysql error日志
		#need_day=$(date +%Y-%m-%d --date '-1 days') ; eval sed -n '/${need_day}T[0-9][0-9]:[0-9][0-9]:[0-9][0-9]/,\$p' /data/mysql_3308/mysqllog/dblogs/mysql3308.err  #有BUG, 如果日期不存在的话, 就为空... 后面有空了再修改.  所以目前就只使用tail -500这种
		if self.Mysql_Error_Log:
			hostinfo['mysql_error_log'] = shell.get_result_dict("tail -n 500 {error_log_file} | grep '\[ERROR\]'".format(error_log_file=self.file_list['error_log_file']))
		else:
			hostinfo['mysql_error_log'] = {"code":-1, "stdout":"请先启用", "stderr":""}


		#mysql 慢日志(暂不支持) v1.X 版本依赖pt-query-digest 后续可能还是会使用这种方式吧...
		#if self.Mysql_Slow_Log:
		#	hostinfo['slow_log'] = shell.get_result_dict("pt-query-digest {slow_log} --output json".format(slow_log=self.file_list['slow_query_log_file']))
		#else:
		#	hostinfo['mysql_error_log'] = {"code":-1, "stdout":"请先启用", "stderr":""}


		#MYSQL各目录大小  如果不是绝对路径的话, 就是datadir下面 所以判断是否以/开头就行
		for x in self.dir_list:
			dirname = self.dir_list[x][0]
			if dirname == '':
				dirname = str(self.global_variables['datadir'].tail(1)[0])
			elif dirname[0] != '/':
				dirname = str(self.global_variables['datadir'].tail(1)[0]) + "/" + dirname
			#hostinfo[x] = shell.get_result_dict("df -PT {dirname} | tail -n +2".format(dirname=dirname))
			dirf = shell.get_result_dict("df -PT {dirname} | tail -n +2".format(dirname=dirname))
			dir_size = shell.get_result_dict("du -sh %s | awk '{print $1}'" %(dirname))
			dirf['stdout'] = dirf['stdout'].split()
			dirf['stdout'][2] = round(int(dirf['stdout'][2])/1024/1024,1)
			dirf['stdout'][3] = round(int(dirf['stdout'][3])/1024/1024,1)
			dirf['stdout'][4] = round(int(dirf['stdout'][4])/1024/1024,1)
			dirf['other'] = dir_size
			hostinfo[x] = dirf


		#其它信息, 主机名, 发行版本, 内核版本, 负载, 时区
		hostinfo['hostname'] = shell.get_result_dict("cat /proc/sys/kernel/hostname")
		hostinfo['version'] = shell.get_result_dict("""grep "^NAME=" /etc/os-release  | awk -F = '{print $2}' | sed 's/\"//g'""")
		hostinfo['kernel'] = shell.get_result_dict('uname -r')
		hostinfo['platform'] = shell.get_result_dict('uname -m')
		hostinfo['loadavg'] = shell.get_result_dict('cat /proc/loadavg')
		hostinfo['timezone'] = shell.get_result_dict("ls -l /etc/localtime | awk -F /zoneinfo/ '{print $NF}'")

		#主机日志(主要看有没得OOM). dmesg -T  #计划v2.3版本
		#hostinfo['dmesg'] = shell.get_result_dict('dmesg -T')

		#硬件信息,比如硬件厂商, 物理插槽等 lshw #v2.3之后的版本, 具体的得看时间...
		#hostinfo['lshw'] = shell.get_result_dict('lshw')

		#print(hostinfo)
		return {"status":True,"data":hostinfo}
