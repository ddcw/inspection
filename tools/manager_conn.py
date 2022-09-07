from ../inspection import manager_inspection
from ../inspection import hashstr
import yaml
with open('../conf/global.yaml', 'r', encoding="utf-8") as f:
	inf_data =  f.read()
c = yaml.load(inf_data,Loader=yaml.Loader)
manager_host = c['MANAGER']['host']
manager_port = c['MANAGER']['port']
manager_authkey = hashstr.hash1(c['MANAGER']['authkey'])

#manager_host = '127.0.0.1'
#manager_port = 6121
#manager_authkey = hashstr.hash1('1234567890abcdefghijklmn')
manager_instance = manager_inspection.task_manager()
m = manager_instance.conn(manager_host,manager_port,manager_authkey)
q = m.task_queue()
inspection = m.inspection()
#inspection.get_task_all()
while True:
	cmd = input('CMD> ')
	if cmd in ['exit','quit','q','e']:
		break
	exec(cmd)
