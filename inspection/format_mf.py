def formatc(c):
	r = {}
	try:
		r['host'] = c['host']
	except:
		r['host'] = None

	try:
		r['port'] = c['port']
	except:
		r['port'] = None

	try:
		r['user'] = c['user']
	except:
		r['user'] = None

	try:
		r['password'] = c['password']
	except:
		r['password'] = None

	try:
		r['socket'] = c['socket']
	except:
		r['socket'] = None

	try:
		r['database'] = c['database']
	except:
		r['database'] = None

	try:
		r['ssh_port'] = c['ssh_port']
	except:
		r['ssh_port'] = None

	try:
		r['ssh_user'] = c['ssh_user']
	except:
		r['ssh_user'] = None

	try:
		r['ssh_password'] = c['ssh_password']
	except:
		r['ssh_password'] = None

	try:
		r['ssh_pkey'] = c['ssh_pkey']
	except:
		r['ssh_pkey'] = None

	return r
