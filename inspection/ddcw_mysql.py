# -*- coding: utf-8 -*-
import pymysql

class set:
	def __init__(self,*args,**kwargs):
		try:
			self.host = kwargs["host"]
		except:
			self.host = "127.0.0.1"
		try:
			self.port = int(kwargs["port"])
		except:
			self.port = 3306
		try:
			self.user = kwargs["user"]
		except:
			self.user = "root"
		try:
			self.socket = kwargs["socket"]
		except:
			self.socket = None
		try:
			self.database = kwargs["database"]
		except:
			self.database = None
		try:
			self.password = kwargs["password"]
		except:
			self.password = ""
	
	#todo ssl

	#返回conn连接
	def get_conn(self):
		try:
			conn = pymysql.connect(
			host=self.host,
			port=self.port,
			user=self.user,
			password=self.password,
			database=self.database,
			unix_socket = self.socket,
			)
			return {"status":True,"data":conn}
		except Exception as e:
			#print(e)
			return {"status":False,"data":e}

	#测试连接, 成功返回True
	def test(self):
		try:
			conn = pymysql.connect(
			host=self.host,
			port=self.port,
			user=self.user,
			password=self.password,
			database=self.database,
			unix_socket = self.socket,
			)
			cursor = conn.cursor()
			cursor.execute("show databases;")
			data = cursor.fetchall()
			conn.close()
			return {"status":True,"data":conn}
		except Exception as e:
			#print(e)
			return {"status":False,"data":e}

	#设置连接, 设置连接之后才可以执行sql
	def set(self):
		try:
			conn = pymysql.connect(
			host=self.host,
			port=self.port,
			user=self.user,
			password=self.password,
			database=self.database,
			unix_socket = self.socket,
			)
			self.conn = conn
			#self.cursor = conn.cursor()
		except Exception as e:
			print(e)
			return False

	def get_result_dict(self,sql):
		cursor = self.conn.cursor()
		try:
			cursor.execute(sql)
			data = cursor.fetchall()
			istrue = True
		except Exception as e:
			data = e
			istrue = False
		finally:
			return {"istrue":istrue, "data":data}

	def close(self):
		self.conn.close()
