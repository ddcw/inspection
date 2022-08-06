import time
import os

class log:
	def __init__(self,*args,**kwargs):
		#self.format_log = ""
		logfile = kwargs["logfile"]
		try:
			format_log = kwargs["format_log"]
			self.format_log = format_log
		except:
			self.format_log = ""
		try:
			self.f = open(logfile,"a",encoding="utf-8",)
		except Exception as e:
			logfile = "/tmp/_tmpfilelog_{time}.log".format(time=time.time())
			print(e,"logfile will use {logfile}".format(logfile=logfile))
			self.f = open(logfile, "a", encoding="utf-8",)

	def format_log_add(self,format_log):
		self.format_log = self.format_log + str(format_log)

	def format_log2(self,format_log):
		self.format_log = format_log

	def error(self,msg):
		self.f.write('[{time}] [ERROR]   {format_log} {msg}\n'.format(time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), msg=msg, format_log=self.format_log))
		self.f.flush()

	def warning(self,msg):
		self.f.write('[{time}] [WARNING] {format_log} {msg}\n'.format(time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), msg=msg, format_log=self.format_log))
		self.f.flush()

	def info(self,msg):
		self.f.write('[{time}] [INFO]    {format_log} {msg}\n'.format(time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), msg=msg, format_log=self.format_log))
		self.f.flush()

	def close(self,):
		self.f.close()
