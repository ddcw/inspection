# -*- coding: utf-8 -*-
import paramiko

#支持私钥类型  DSSKey(dsa) RSAKey(rsa) try试一试....

class set:
	def __init__(self,*args,**kwargs):
		try:
			self.host = kwargs["host"]
		except:
			self.host = "127.0.0.1"
		try:
			self.port = int(kwargs["port"])
		except:
			self.port = 22
		try:
			self.user = kwargs["user"]
		except:
			self.user = "root"
		try:
			self.password = kwargs["password"]
		except:
			self.password = None
		try:
			self.key = kwargs["key"]
		except:
			self.key = None

	def set(self):
		HOST = self.host
		SSH_PORT = self.port
		SSH_USER = self.user
		SSH_PASSWORD = self.password
		SSH_PKEY = self.key
		try:
			ssh = paramiko.SSHClient()
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			if self.key is None:
				ssh.connect(hostname=HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASSWORD, )
			else:
				try:
					ssh.connect(hostname=HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASSWORD, pkey=paramiko.RSAKey.from_private_key_file(SSH_PKEY))
				except:
					try:
						ssh.connect(hostname=HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASSWORD, pkey=paramiko.DSSKey.from_private_key_file(SSH_PKEY))
					except Exception as e:
						#print(e)
						return {"status":False,"data":e}
			self.ssh = ssh
		except Exception as e:
			self.ssh = False
			return {"status":False,"data":e}
		return {"status":True,"data":""}


	def get_conn(self):
		HOST = self.host
		SSH_PORT = self.port
		SSH_USER = self.user
		SSH_PASSWORD = self.password
		SSH_PKEY = self.key
		try:
			ssh = paramiko.SSHClient()
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			if self.key is None:
				ssh.connect(hostname=HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASSWORD, )
			else:
				try:
					ssh.connect(hostname=HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASSWORD, pkey=paramiko.RSAKey.from_private_key_file(SSH_PKEY))
				except:
					try:
						ssh.connect(hostname=HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASSWORD, pkey=paramiko.DSSKey.from_private_key_file(SSH_PKEY))
					except:
						pass
		except Exception as e:
			#print(e)
			return {"status":False,"data":e}
		finally:
			return ssh
					
		return conn


	def test(self):
		HOST = self.host
		SSH_PORT = self.port
		SSH_USER = self.user
		SSH_PASSWORD = self.password
		SSH_PKEY = self.key
		try:
			ssh = paramiko.SSHClient()
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			if self.key is None:
				ssh.connect(hostname=HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASSWORD, )
			else:
				try:
					ssh.connect(hostname=HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASSWORD, pkey=paramiko.RSAKey.from_private_key_file(SSH_PKEY))
				except:
					try:
						ssh.connect(hostname=HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASSWORD, pkey=paramiko.DSSKey.from_private_key_file(SSH_PKEY))
					except Exception as e:
						#print(e,". Please select dsa or rsa private key file")
						return {"status":False, "data":e}
			return {"status":True, "data":""}
		except Exception as e:
			#print(e)
			return {"status":False, "data":e}

	#注:命令不存在返回状态码仍为0 得用是否有标准错误来辅助衡量, 其实有stderr或者return code 不为0 也不能说明执行失败....
	def get_result_dict(self,comm):
		try:
			ssh = self.ssh
			stdin, stdout, stderr = ssh.exec_command(comm)
			return {"code":stdout.channel.recv_exit_status(), 
				"stdout":str(stdout.read().rstrip(),encoding="utf-8"),
				"stderr":str(stderr.read().rstrip(),encoding="utf-8"),
				}
		except Exception as e:
			return {"code":-1, "stdout":"请先连接ssh, 或者执行命令失败", "stderr":e}

	def close(self):
		self.ssh.close()
