def get_role(relation_data,global_variables,global_status):
	role = []
	if 'master_info' in relation_data:
		try:
			#masterinfo = relation_data['master_info']['data']['data']
			master_size = relation_data['master_info']['data']['data'].shape[0]
			if master_size > 0:
				role.append('主库({s}个从库)'.format(s=master_size))
		except:
			pass

	if 'slave_info' in relation_data:
		try:
			slave_size = relation_data['slave_info']['data']['data'].shape[0]
			if slave_size > 0:
				if global_variables['data']['rpl_semi_sync_master_wait_point'].values[0] == "AFTER_SYNC":
					role.append('从库(半同步)')
				elif global_variables['data']['rpl_semi_sync_master_wait_point'].values[0] == "AFTER_COMMIT":
					role.append('从库(增强半同步)')
				else:
					role.append('从库')
		except:
			pass

	if 'pxc_info' in relation_data:
		try:
			if relation_data['pxc_info']['data']['status']:
				role.append('PXC集群')
		except:
			pass

	if 'mgr_info' in relation_data:
		try:
			if global_variables['data']['group_replication_single_primary_mode'].values[0] == "ON":
				if global_status['data'].tail(1)['group_replication_primary_member'].values[0] == global_variables['data']['server_uuid'].values[0]:
					role.append("MGR集群 主节点(单主模式)")
				else:
					role.append("MGR集群 从节点(单主模式)")
			else:
				role.append('MGR集群(多主模式)')
		except:
			pass

	return role
