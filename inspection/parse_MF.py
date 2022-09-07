def get_result(mf):
	return_data = []
	mf_global = mf['GLOBAL']
	mf_data = mf['DATA']

	for x in mf_data:
		if 'DEFAULT_HOST' in mf_global:
			x['host'] = mf_global['DEFAULT_HOST'] if 'host' not in x else x['host']
		if 'DEFAULT_PORT' in mf_global:
			x['port'] = mf_global['DEFAULT_PORT'] if 'port' not in x else x['port']
		if 'DEFAULT_USER' in mf_global:
			x['user'] = mf_global['DEFAULT_USER'] if 'user' not in x else x['user']
		if 'DEFAULT_PASSWORD' in mf_global:
			x['password'] = mf_global['DEFAULT_PASSWORD'] if 'password' not in x else x['password']
		if 'DEFAULT_SSHPORT' in mf_global:
			x['sshport'] = mf_global['DEFAULT_SSHPORT'] if 'sshport' not in x else x['sshport']
		if 'DEFAULT_SSHUSER' in mf_global:
			x['sshuser'] = mf_global['DEFAULT_SSHUSER'] if 'sshuser' not in x else x['sshuser']
		if 'DEFAULT_SSHPASSWORD' in mf_global:
			x['sshpassword'] = mf_global['DEFAULT_SSHPASSWORD'] if 'sshpassword' not in x else x['sshpassword']
		if 'DEFAULT_SSHENABLE' in mf_global:
			x['sshenable'] = mf_global['DEFAULT_SSHENABLE'] if 'sshenable' not in x else x['sshenable']
		if 'DEFAULT_SSHFORCE' in mf_global:
			x['sshforce'] = mf_global['DEFAULT_SSHFORCE'] if 'sshforce' not in x else x['sshforce']
		return_data.append(x)
	return return_data
