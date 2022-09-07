import os
from jinja2 import FileSystemLoader,Environment
import time

def get_data_from_file(filename):
	data = ''
	with open(filename,'r') as f:
		data = f.read()
	return data

def run(c,data1_result,baseinfo,inspection_data_result,hostdata):
	#data1_result 持续巡检项  baseinfo基础信息  inspection_data_result巡检项 hostdata主机相关信息
	data = inspection_data_result

	report_filepath = os.path.abspath(baseinfo['report_dir'])
	report_filename = '{taskid}_{host}_{port}_{time}.html'.format(taskid=baseinfo['taskid'], task_detail_id=baseinfo['task_detail_id'], host=baseinfo['host'], port=baseinfo['port'], time=str(int(time.time()))) #要返回的巡检报告的名字
	report_file = str(report_filepath) + '/' + str(report_filename) #用于生成巡检报告的(绝对路径)


	#模板文件
	(tmp_file_path,tmp_file_name) = os.path.split(c['OTHER']['report_html_template'])

	GLOBAL_STYLE = 0 #表示文件链接,  0 表示代码
	try:
		GLOBAL_STYLE = baseinfo['online']
	except:
		GLOBAL_STYLE = 0

	style = {}
	if GLOBAL_STYLE:
		style['jq'] = "<script src='../static/js/jquery-3.3.1.min.js'></script>"
		style['bcss'] = "<link href='../static/css/bootstrap.min.css' rel='stylesheet'>"
		style['btcss'] = "<link href='../static/css/bootstrap-table.min.css' rel='stylesheet'>"
		style['bjs'] = "<script src='../static/js/bootstrap.bundle.min.js'></script>"
		style['btjs'] = "<script src='../static/js/bootstrap-table.min.js'></script>"
		style['btzhjs'] = "<script src='../static/js/bootstrap-table-zh-CN.min.js'></script>"
		style['cjs'] = "<script src='../static/js/chart.min.js'></script>"
	else:
		style['jq'] = "<script>{data}</script>".format(data=get_data_from_file('./static/js/jquery-3.3.1.min.js'))
		style['bcss'] = "<style type='text/css'>{data}</style>".format(data=get_data_from_file('./static/css/bootstrap.min.css'))
		style['btcss'] = "<style type='text/css'>{data}</style>".format(data=get_data_from_file('./static/css/bootstrap-table.min.css'))
		style['bjs'] = "<script>{data}</script>".format(data=get_data_from_file('./static/js/bootstrap.bundle.min.js'))
		style['btjs'] = "<script>{data}</script>".format(data=get_data_from_file('./static/js/bootstrap-table.min.js'))
		style['btzhjs'] = "<script>{data}</script>".format(data=get_data_from_file('./static/js/bootstrap-table-zh-CN.min.js'))
		style['cjs'] = "<script>{data}</script>".format(data=get_data_from_file('./static/js/chart.min.js'))

	env = Environment(loader=FileSystemLoader(tmp_file_path))
	template = env.get_template(tmp_file_name)
	tmp_file = template.render(data=data, c=c, baseinfo=baseinfo, style=style, hostdata=hostdata, data1_result=data1_result) #新版
	#tmp_file = template.render(data=data, c=c, data1=baseinfo, style=style, data2=hostdata) #旧版

	with open(report_file,'w',encoding='utf-8') as fhtml:
		fhtml.write(tmp_file)

	return {'type':'html','status':True,'data':report_filename}
