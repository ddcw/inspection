# -*- coding: utf-8 -*-

import subprocess

class set:
	def __init__(self,*args,**kwargs):
		try:
			self.timeout = kwargs["timeout"]
		except:
			self.timeout = 30

	def get_result_dict(self,comm):
		timeout = self.timeout
		with subprocess.Popen(comm, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as f:
			try:
				return {
					"code":f.wait(timeout),
					"stdout":str(f.stdout.read().rstrip(),encoding="utf-8"),
					"stderr":str(f.stderr.read().rstrip(),encoding="utf-8"),
					}
			except Exception as e:
				f.kill()
				return {
					"code":-1,
					"stdout":str(f.stdout.read().rstrip(),encoding="utf-8"),
					"stderr":str(f.stderr.read().rstrip(),encoding="utf-8"),
					}
		
	#是本地IP就返回True, 不是就返回False,  使用	
	def is_local_ip(self,host):
		host = '127.0.0.1' if host is None else host #BUG修复: 当HOST为空的时候会抛出异常
		localiplist = self.get_result_dict("ifconfig | grep inet  | awk '{print $2}'")['stdout']
		if host in localiplist or host == '0.0.0.0':
			return True
		else:
			return False
