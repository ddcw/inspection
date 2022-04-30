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
			
