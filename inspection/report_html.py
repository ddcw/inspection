import os
from jinja2 import FileSystemLoader,Environment

def get_data_from_file(filename):
	data = ''
	with open(filename,'r') as f:
		data = f.read()
	return data

def get_result(data,data1,c,report_filename,data2):
	#data巡检项  data1一些汇总信息  c 配置文件  report_filename巡检报告的名字  data2 主机信息
	hostdata = data2
	#print(hostdata)
	tmplatefile = c['GLOBAL']['Html']
	tmpdir = os.path.abspath(c['GLOBAL']['Tmp_dir'])
	(tmp_file_path,tmp_file_name) = os.path.split(tmplatefile)
	if len(tmp_file_path) == 0:
		tmp_file_path = "./"

	GLOBAL_STYLE = 0 #表示文件链接,  0 表示代码
	try:
		GLOBAL_STYLE = c['GLOBAL']['Online']
	except:
		GLOBAL_STYLE = 0
	style = {}
	if GLOBAL_STYLE == 1:
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
	tmp_file = template.render(data=data,c=c['INSPECTION'],data1=data1, style=style, data2=hostdata)

	file_dir_name = "{tmpdir}/{report_filename}.html".format(tmpdir=tmpdir, report_filename=report_filename)
	with open(file_dir_name,'w',encoding='utf-8') as fhtml:
		fhtml.write(tmp_file)


	return os.path.abspath(file_dir_name)
