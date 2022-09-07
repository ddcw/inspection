import yaml
with open('../conf/inspection.yaml', 'r', encoding="utf-8") as f:
	inf_data =  f.read()
conf = yaml.load(inf_data,Loader=yaml.Loader)
for x in conf['INSPECTION']:
	try:
		if not x['enabled']:
			pass
		else:
			print("{name}__DDCW_FLAG_SPIT__{sql}".format(name=x['object_name'],sql=x['sql']))
	except:
		print("{name}__DDCW_FLAG_SPIT__{sql}".format(name=x['object_name'],sql=x['sql']))
