import xml.etree.ElementTree as ET
import pandas as pd

#因为是pandas 1.1 不支持read_xml... 所以得自己封装个
def resultset_to_pandas(data):
	rdata = {}
	for y in data[0]:
		rdata[y.attrib['name']] = []
	for x in data:
		for y in x:
			name = y.attrib['name']
			value = y.text
			rdata[name].append(value)
	return_data = pd.DataFrame(rdata).set_index('Variable_name').T
	return return_data

def resultset_to_pandas2(data):
	rdata = {}
	index = []
	if len(data) > 0:
		for y in data[0]:
			rdata[y.attrib['name']] = []
			index.append(y.attrib['name'])
		for x in data:
			for y in x:
				name = y.attrib['name']
				value = y.text
				rdata[name].append(value)
		return_data = pd.DataFrame(rdata)
		return return_data
	else:
		#print(data.attrib['statement'],'iSNLLLLLLLL')
		return pd.DataFrame()


def return_obj(filename):
	return_data = {}
	return_data['data1'] = {}
	return_data['data2'] = {}
	return_data['data3'] = {}
	return_data['hostdata'] = {}
	return_data['baseinfo'] = {}
	tree = ET.ElementTree(file = filename)
	root = tree.getroot()

	#处理data1 持续巡检项
	#print(root[0][0][0],'AAA')
	#print(root[0][0][0][0].attrib,'BBB')
	return_data['data1']['status'] = 'True'
	dfdata = resultset_to_pandas(root[0][0][0][0][0])
	dfdata.insert(0,'time_col1',root[0][0][0][0].attrib)
	data1_isfirst = True
	for x in root[0][0][0]:
		if data1_isfirst:
			data1_isfirst = False
			continue
		_dfdata = resultset_to_pandas(x[0])
		_dfdata.insert(0,'time_col_0',int(x.attrib['time']))
		dfdata = dfdata.append(_dfdata)
	return_data['data1']['data'] = dfdata
		

	#处理data2 固定采集项
	#print(root[0][1])
	for x in root[0][1]:
		objname = x.tag
		if objname in ['global_variables','global_status']:
			_dfdata = resultset_to_pandas(x[0])
		else:
			_dfdata = resultset_to_pandas2(x[0])
		return_data['data2'][objname] = {'status':True,'data':_dfdata}

	#print(return_data['data2']['sys.memory_global_total']['data'],'ACCCCCCCCCCCCC')
	#for x in return_data['data2']:
	#	print(x,len(return_data['data2'][x]['data']))

	#处理data3 巡检项
	#print(root[0][2])
	for x in root[0][2]:
		objname = x.tag
		if objname == 'simple_password':
			continue
		try:
			_dfdata = resultset_to_pandas2(x[0])
		except:
			print(objname,'XXXX')
		return_data['data3'][objname] = _dfdata

	#print(return_data['data3']['no_primary_key'],'AAAAAAAAAAAa')

	#处理hostdata 主机信息
	#print(root[1])
	return_data['hostdata']['status'] = True
	return_data['hostdata']['data'] = {}
	for x in root[1]:
		objname = x.tag
		_data = x.text
		return_data['hostdata']['data'][objname] = {'stdout':_data}
	return_data['hostdata']['data']['dirstatus'] = False #暂不支持目录信息

	#处理baseinfo  只有mysql主机和端口
	#print(root[2])
	for x in root[2]:
		objname = x.tag
		_data = x.text
		return_data['baseinfo'][objname] = _data.strip('\n')

	#print(root[0][0][0].text)
	#print(root[0][0][0].attrib)
	#print(root[0][0][0].tag)

	return return_data
