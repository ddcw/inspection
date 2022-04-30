# -*- coding: utf-8 -*-

import time
import os
from jinja2 import FileSystemLoader,Environment
from . import chartjs

class set:
	def __init__(self,*args,**kwargs):
		try:
			self.data = kwargs["data"]
		except:
			print("请指定data")
			return False
		try:
			self.file_name = kwargs["file_name"] #指定保存到的文件
		except:
			self.file_name = "tmp_" + str(time.time()) #为空的话,就自动生成...

		try:
			self.file_dir = kwargs["file_dir"]
		except:
			self.file_dir = "./"

		try:
			self.html_template = kwargs["html_template"] #指定模板文件的路径, 为空或者不存在的话, 就自动生成
		except:
			self.html_template = "template.html"

		try:
			self.html_mode = kwargs["html_mode"]  # 0 表示chartjs使用cdn,  1 表示把chartjs放到html文件,  2 表示使用服务器上的chartjs(http模式)
		except:
			self.html_mode = 0

	#返回生成的html路径
	def return_html(self):
		file_name = self.file_name + ".html"
		#file_name = "tmp_1650266637.0289428.html"  #方便测试的, 要删掉
		html_template = self.html_template
		data = self.data
		html_mode = self.html_mode

		if html_mode == 0:
			chart = """<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.7.1/chart.min.js"></script>"""
		chart = "<script>" + chartjs.return_chartjs() + "</script>"

		#看下模板文件是否存在,不存在就自动导入(不判断内容...)
		if not os.path.exists(html_template):  #因为方便测试, 所以加了个恒等的条件, 要删掉
			from . import t_html
			html_content = t_html.return_content()
			#print(html_content,"xxxxxxxxx")
			with open(html_template,'w',1) as f:
				f.write(html_content)


		#部分jinja2不支持的py写法, 这里做转换
		#aa = str(data["databases"]["data"]["databases_T"][0])
		#print(data["databases"]["data"]["databases_T"][0])


		#jinja2根据模板生成巡检报告
		(tmp_file_path,tmp_file_name) = os.path.split(html_template)
		if len(tmp_file_path) == 0:
			tmp_file_path = "./"
		env = Environment(loader=FileSystemLoader(tmp_file_path))
		template = env.get_template(tmp_file_name)
		tmp_file = template.render(data=data, chart=chart)


		#print(data["databases"]["data"]["databases_T"][0])
		#exit(1)


		#保存巡检报告
		file_dir_name = str(self.file_dir) + "/" + file_name
		with open(file_dir_name,'w') as fhtml:
			fhtml.write(tmp_file)
			

		return {"istrue":True,"data":file_name}


	#返回生成的word路径
	def return_word(self):
		return False


	#返回生成的pdf路径
	def return_pdf(self):
		return False
