from . import ddcw_mysql
from . import ddcw_ssh
from . import get_local_comm
class mysql:
	def __init__(self,instancef):
		self.mysql = ddcw_mysql.set(
			host=instancef['host'],
			port=instancef['port'],
			user=instancef['user'],
			password=instancef['password'],
			socket=instancef['socket'],
			database=instancef['database'],
			)
		self.error = "test error"

	def status(self,):
		mysql_status = self.mysql.test()
		if mysql_status['status']:
			return True
		else:
			self.error = mysql_status["data"]
			return False
		#return self.mysql.test()

	def conn(self,):
		mysql_conn = self.mysql.get_conn()
		if mysql_conn['status']:
			return mysql_conn['data']
		else:
			self.error=mysql_conn['data']
			return False
class shell:
	def __init__(self,instancef):
		self.erro = "test error"
		host = instancef['host']
		self.islocalip = get_local_comm.set().is_local_ip(host)
		if self.islocalip:
			self.shell = get_local_comm.set()
			self.statu = True
		else:
			tssh = ddcw_ssh.set(
				host = host,
				port = instancef['ssh_port'],
				user = instancef['ssh_user'],
				password = instancef['ssh_password'],
				key = instancef['ssh_pkey'],
			)
			testssh = tssh.set()
			if testssh['status']:
				self.statu = True
				self.shell = tssh
			else:
				self.error = testssh['data']
				self.statu = False
		

	def status(self,):
		return self.statu

	def conn(self,):
		return self.shell

	def close(self,):
		return self.shell.close()
