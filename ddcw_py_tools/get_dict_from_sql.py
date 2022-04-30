# -*- coding: utf-8 -*-

#传递过来一个sql和cursor, 返回一个dict {"istrue":True,"data":data}
class get:
	def __init__(self, cursor, sql):
		self.cursor = cursor
		self.sql = sql

	def get_result(self):
		cursor = self.cursor
		sql = self.sql
		try:
			cursor.execute(sql)
			data = cursor.fetchall()
			istrue = True
		except Exception as e:
			data = e
			istrue = False
		finally:
			return {"istrue":istrue, "data":data}
			
