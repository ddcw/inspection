def return_content():
	return  """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{data["DBTYPE"]}}巡检报告({{data["AUTHOR"]}}) </title>
	{{chart}}


<script>
//定义个颜色列表, 要颜色就来这取....
const colorlist = ["rgb(54, 162, 235)", "rgb(255, 99, 132)", "rgb(255, 205, 86)","rgb(25, 202, 173)","rgb(214, 213, 183)","rgb(140, 199, 181)","rgb(209, 186, 116)","rgb(160, 238, 225)","rgb(230, 206, 172)","rgb(190, 231, 233)","rgb(236, 173, 158)","rgb(190, 237, 199)","rgb(244, 96, 108)"]
</script>
<style type="text/css">
body.awr {font:bold 10pt Arial,Helvetica,Geneva,sans-serif;color:black; background:White;}
pre.awr  {font:8pt Courier;color:black; background:White;}
h1.awr   {font:bold 20pt Arial,Helvetica,Geneva,sans-serif;color:#336699;background-color:White;border-bottom:1px solid #cccc99;margin-top:0pt; margin-bottom:0pt;padding:0px 
0px 0px 0px;}
h2.awr   {font:bold 18pt Arial,Helvetica,Geneva,sans-serif;color:#336699;background-color:White;margin-top:4pt; margin-bottom:0pt;}
h3.awr {font:bold 16pt Arial,Helvetica,Geneva,sans-serif;color:#336699;background-color:White;margin-top:4pt; margin-bottom:0pt;}
li.awr {font: 8pt Arial,Helvetica,Geneva,sans-serif; color:black; background:White;}
th.awrbg {font:bold 8pt Arial,Helvetica,Geneva,sans-serif; color:White; background:#0066CC;padding-left:4px; padding-right:4px;padding-bottom:2px}
th.awrbg a {text-decoration: none;color:White;}
a.awr {font:bold 8pt Arial,Helvetica,sans-serif;color:#663300; vertical-align:top;margin-top:0pt; margin-bottom:0pt;}
table.tdiff {  border_collapse: collapse; }
.hidden   {position:absolute;left:-10000px;top:auto;width:1px;height:1px;overflow:hidden;}
.pad   {margin-left:17px;}
.doublepad {margin-left:34px;}
tr:hover   {background-color: yellow;}
td {text-align:center;}
</style>

<style type="text/css">
	#NavRight{
		width:222px;
		height:400px;
		position:fixed;
		right:0px;top:15%;      
		}
	#NavRight #NavCon ul li a:hover{
		background:yellow;
		}
</style>

<script type="text/javascript">
console.log("ddcw_inspection 版本为: {{data['VERSION']}}")
console.log("最新下载地址:  https://github.com/ddcw/inspection")
</script>



</head>
<body class="awr">
<!-- 右侧固定导航栏  --> 
<div id="NavRight">
	 <div id="NavCon">
		<ul>
			<li><a href="#summary_base">数据库基础信息</a></li>
			{%if data["havehostdata"] %}<li><a href="#hostinfo">主机信息</a></li>{%endif%}
			<li><a href="#databases">数据库表信息</a></li>
			<li><a href="#user">用户信息</a></li>
			<li><a href="#variables">重要参数</a></li>
			<li><a href="#no_primary_key">无主键的表</a></li>
			<li><a href="#no_innodb_table">非InnoDB表</a></li>
			<li><a href="#no_innodb_table">非InnoDB表</a></li>
			<li><a href="#repeat_index">重复索引的表</a></li>
			<li><a href="#over_5_index">索引过多的表</a></li>
			<li><a href="#sql_comm">SQL执行占比</a></li>
			<li><a href="#over30days_table_static">统计信息过期的表</a></li>
			<li><a href="#over30days_index_static">统计信息过期的索引</a></li>
			<li><a href="#fragment_table">碎片率超过30%的表</a></li>
			{% if data["havehostdata"] %}<li><a href="#binlog_grows">binlog变化频率</a></li>{%endif%}
			<li><a href="#top20_table">最大的表 (TOP20)</a></li>
			<li><a href="#big_table">大表</a></li>
			<li><a href="#cold_table">冷表</a></li>
			<li><a href="#innodb_lock_waits">锁等待</a></li>
			<li><a href="#full_table">走全表扫描的表</a></li>
			<li><a href="#top20_sql">执行次数最多的SQL (TOP20)</a></li>
			<li><a href="#innodb_buffer_stats_by_table">使用内存最多表 (TOP20)</a></li>
			<li><a href="#io_global_by_wait_by_bytes">IO等待事件</a></li>
			<li><a href="#memory_by_host_by_current_bytes">使用内存最多的主机 (TOP20)</a></li>
			<li><a href="#memory_by_user_by_current_bytes">使用内存最多的用户 (TOP20)</a></li>
			<li><a href="#tmp_table_file">使用临时表的SQL</a></li>
			<li><a href="#slow_sql">慢SQL (TOP20)</a></li>
			<li><a href="#error_log">错误日志</a></li>
			{% if data["current_role"]["istrue"] %}<li><a href="#cluster_slave">主从/集群信息</a></li>{%endif%}
		</ul>
	</div>
</div>

<!-- <h1>汇总</h1> -->
<h3 class="awr" id="summary_base"><a class="awr"></a>基础信息</h3>
<table border="0" width="70%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col">巡检时间</th>
		<th class="awrbg" scope="col">数据库端口</th>
		<th class="awrbg" scope="col">数据库版本</th>
		<th class="awrbg" scope="col"><a href="#databases">数据库数量</a></th>
		<th class="awrbg" scope="col"><a href="#databases">表数量</a></th>
		<th class="awrbg" scope="col"><a href="#databases">表数据大小</a></th>
		<th class="awrbg" scope="col"><a href="#databases">表索引大小</a></th>
		<th class="awrbg" scope="col"><a href="#user">用户数量</a></th>
		<th class="awrbg" scope="col">运行时间</th>
	</tr>
	<tr>
		<td>{{data["time"]}}</th>
		<td>{{data["variables"]["data"]["value"]["port"]}}</th>
		<td>{{data["variables"]["data"]["value"]["version"]}}</th>
		<td>{{ data["databases"]["data"]["databases"] | count }}</th>
		<td>{{ data["all_engine_table"]["data"]["all_engine_table_T"][1] | sum}}</th>
		<td>{{data["table_sum_size_gb"]["data"]}} GB</th>
		<td>{{data["index_sum_size_gb"]["data"]}} GB</th>
		<td>{{data["user"]["data"]|count}}</th>
		<td>{{ (data["status"]["data"]["value"]["Uptime"] | int / 3600 / 24) | round(2)}} 天</th>
	</tr>
</table>
<table border="0" width="70%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col">平均TPS</th>
		<th class="awrbg" scope="col">平均QPS</th>
		<th class="awrbg" scope="col"><a href="#processlist">PROCESSLIST</a></th>
		<th class="awrbg" scope="col"><a href="#threads">THREADS</a></th>
		<th class="awrbg" scope="col"><a href="#sql_comm">SQL COMM TYPE</a></th>
		<th class="awrbg" scope="col"><a href="#plugins">插件</a></th>
	</tr>
	<tr>
		<td>{{ ((data["status"]["data"]["value"]["Com_commit"]|int+data["status"]["data"]["value"]["Com_rollback"]|int)/data["status"]["data"]["value"]["Uptime"]|int) | round(2) }}</td>
		<td>{{(data["status"]["data"]["value"]["Questions"]|int/data["status"]["data"]["value"]["Uptime"]|int) | round(2)}}</td>
		<td>{{data["processlist"]["data"]|count}}</td>
		<td>{{data["threads"]["data"]|count}}</td>
		<td>{{data["sql_comm"]["data"]["sql_comm"]|count}}</td>
		<td>{{data["plugins"]["data"]|count}}</td>
	</tr>
</table>


<h3 class="awr" id="summary_performance"><a class="awr"></a>性能与规范</h3>
<table border="0" width="70%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col">缓存命中率</th>
		<th class="awrbg" scope="col"><a href="#no_innodb_table">非innodb表</a></th>
		<th class="awrbg" scope="col"><a href="#no_primary_key">无主键表</a></th>
		<th class="awrbg" scope="col"><a href="#repeat_index">重复索引表</a></th>
		<th class="awrbg" scope="col"><a href="#over_5_index">索引过多表</a></th>
		<th class="awrbg" scope="col"><a href="#big_table">大表</a></th>
		<th class="awrbg" scope="col"><a href="#cold_table">冷表</a></th>
		<th class="awrbg" scope="col"><a href="#fragment_table">碎片表</a></th>
		<th class="awrbg" scope="col"><a href="#over30days_table_static">统计信息过期的表</a></th>
	</tr>
	<tr>
		<td {% if (100-(data["status"]["data"]["value"]["Innodb_buffer_pool_reads"]|int/data["status"]["data"]["value"]["Innodb_buffer_pool_read_requests"]|int*100))|round(2) < 95 %}style="background:red" {% elif (100-(data["status"]["data"]["value"]["Innodb_buffer_pool_reads"]|int/data["status"]["data"]["value"]["Innodb_buffer_pool_read_requests"]|int*100))|round(2) < 98  %} style="background:yellow" {% endif %} >{{(100-(data["status"]["data"]["value"]["Innodb_buffer_pool_reads"]|int/data["status"]["data"]["value"]["Innodb_buffer_pool_read_requests"]|int*100))|round(2)}}%</td>
		{%if data["no_innodb_table"]["istrue"]%}<td>{{data["no_innodb_table"]["data"]|count}}</td>{%else%}<td>无</td>{%endif%}
		<td>{{data["no_primary_key"]["data"]|count}}</td>
		<td>{{data["repeat_index"]["data"]|count}}</td>
		<td>{{data["over_5_index"]["data"]|count}}</td>
		<td>{{data["big_table"]["data"]|count}}</td>
		<td>{{data["cold_table"]["data"]|count}}</td>
		{%if data["fragment_table"]["istrue"]%}<td>{{data["fragment_table"]["data"]|count}}</td>{%else%}<td>无</td>{%endif%}
		<td>{{data["over30days_table_static"]["data"]|count}}</td>
	</tr>
</table>
<table border="0" width="70%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col">innodb 内存使用百分比</th>
		<th class="awrbg" scope="col">innodb 总内存(page)</th>
		<th class="awrbg" scope="col">innodb LRU(page)(已使用内存)</th>
		<th class="awrbg" scope="col">innodb 剩余内存(page)</th>
		<th class="awrbg" scope="col">innodb 脏数据(page)</th>
		<th class="awrbg" scope="col">innodb 刷新页面次数</th>
		<th class="awrbg" scope="col">innodb 页面大小(字节)</th>
	</tr>
	<tr>
		<td {%if (data["status"]["data"]["value"]["Innodb_buffer_pool_pages_data"]|int/data["status"]["data"]["value"]["Innodb_buffer_pool_pages_total"]|int*100) > 93  %} style="background-color:red" {%elif (data["status"]["data"]["value"]["Innodb_buffer_pool_pages_data"]|int/data["status"]["data"]["value"]["Innodb_buffer_pool_pages_total"]|int*100) > 80%} style="background-color:yellow" {%elif (data["status"]["data"]["value"]["Innodb_buffer_pool_pages_data"]|int/data["status"]["data"]["value"]["Innodb_buffer_pool_pages_total"]|int*100) < 3%} title="还挺闲的...." style="background-color:green"  {%endif%}>{{ (data["status"]["data"]["value"]["Innodb_buffer_pool_pages_data"]|int/data["status"]["data"]["value"]["Innodb_buffer_pool_pages_total"]|int*100)|round(2) }}%</td>
		<td>{{data["status"]["data"]["value"]["Innodb_buffer_pool_pages_total"]|int}} 页 ({{(data["status"]["data"]["value"]["Innodb_buffer_pool_pages_total"]|int*data["status"]["data"]["value"]["Innodb_page_size"]|int/1024/1024)|round(2)}} MB)</td>
		<td>{{data["status"]["data"]["value"]["Innodb_buffer_pool_pages_data"]|int}} 页 </td>
		<td>{{data["status"]["data"]["value"]["Innodb_buffer_pool_pages_free"]|int}} 页</td>
		<td>{{data["status"]["data"]["value"]["Innodb_buffer_pool_pages_dirty"]|int}} 页</td>
		<td>{{data["status"]["data"]["value"]["Innodb_buffer_pool_pages_flushed"]|int}} 次</td>
		<td>{{data["status"]["data"]["value"]["Innodb_page_size"]|int}} </td>
	</tr>
</table>



<table border="0" width="70%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col">剩余连接百分比</th>
		<th class="awrbg" scope="col"><a href="#tmp_table_file">使用临时表(文件)的SQL</a></th>
		<th class="awrbg" scope="col"><a href="#full_table">使用全表扫描的表</a></th>
		<th class="awrbg" scope="col"><a href="#innodb_lock_waits">锁等待</a></th>
	</tr>
	<tr>
		<td>{{100 - ((data["status"]["data"]["value"]["Threads_connected"]|int)/(data["variables"]["data"]["value"]['max_connections']|int)*100)|round(2) }}%</td>
		<td>{{data["tmp_table_file"]["data"]|count}}</td>
		<td>{{data["full_table"]["data"]|count}}</td>
		<td>{{data["innodb_lock_waits"]["data"]|count}}</td>
	</tr>
</table>





<h3 class="awr" id="summary_security"><a class="awr"></a>安全与稳定</h3>
<table border="0" width="70%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col"><a href="#user">超级用户</a></th>
		<th class="awrbg" scope="col"><a href="#user">密码过期用户</a></th>
	</tr>
	<tr>
		<td>{{data["super_user"]["data"]|count}}</td>
		<td>{{data["password_expired_user"]["data"]|count}}</td>
	</tr>
</table>


<h3 class="awr" id="summary_ha"><a class="awr"></a>高可用(集群/主从)信息</h3>
<table border="0" width="70%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col"><a href="#cluster_slave">当前角色</a></th>
	</tr>
	<tr>
		<td>
		{% if data["current_role"]["istrue"] %} {{data["current_role"]["data"]}}
		{%else%}主库{%endif%}
		{% if data["variables"]["data"]["value"]["group_replication_single_primary_mode"] == "ON" %} (单主模式)
		{% elif data["variables"]["data"]["value"]["group_replication_single_primary_mode"] == "OFF" %} (多主模式)
		{% elif (data["variables"]["data"]["value"]["rpl_semi_sync_master_enabled"] == "ON") or (data["variables"]["data"]["value"]["rpl_semi_sync_slave_enabled"] == "ON")  %} 
			{% if data["variables"]["data"]["value"]["rpl_semi_sync_master_wait_point"] == "AFTER_SYNC" %}(半同步)
			{%elif data["variables"]["data"]["value"]["rpl_semi_sync_master_wait_point"] == "AFTER_COMMIT" %} (增强半同步)
			{%endif%}
		{%endif%}
		</td>
	</tr>
</table>



<!-- <h1>明细</h1> -->
</br>
</br>
</br>
</br>



<!-- 主机信息-->
{% if data["havehostdata"] %}
<h3 class="awr" id="hostinfo"><a class="awr"></a>主机相关信息</h3>
<table border="0" width="70%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col"></th>
		<th class="awrbg" scope="col">磁盘</th>
		<th class="awrbg" scope="col">文件系统类型</th>
		<th class="awrbg" scope="col">总大小</th>
		<th class="awrbg" scope="col">已使用空间</th>
		<th class="awrbg" scope="col">可用空间</th>
		<th class="awrbg" scope="col">使用百分比</th>
		<th class="awrbg" scope="col">挂载点</th>
	</tr>
{% if data["data_log_dir"]["istrue"]  %}
	<tr>
		<td>数据目录({{data["variables"]["data"]["value"]['datadir']}})</td>
		<td>{{data["data_log_dir"]["data"][0]}}</td>
		<td>{{data["data_log_dir"]["data"][1]}}</td>
		<td>{{((data["data_log_dir"]["data"][2] | int)/1024/1024)|round(2)}} GB</td>
		<td>{{((data["data_log_dir"]["data"][3] | int)/1024/1024)|round(2)}} GB</td>
		<td>{{((data["data_log_dir"]["data"][4] | int)/1024/1024)|round(2)}} GB</td>
		<td {% if data["data_log_dir"]["data"][5].split("%")[0] | int > 90 %}style="background:yellow" {% endif %}>{{data["data_log_dir"]["data"][5]}}</td>
		<td>{{data["data_log_dir"]["data"][6]}}</td>
	</tr>
{% endif %}
{% if data["log_bin_index"]["istrue"]  %}
	<tr>
		<td>数据目录({{data["variables"]["data"]["value"]['log_bin_index']}})</td>
		<td>{{data["log_bin_index"]["data"][0]}}</td>
		<td>{{data["log_bin_index"]["data"][1]}}</td>
		<td>{{((data["log_bin_index"]["data"][2] | int)/1024/1024)|round(2)}} GB</td>
		<td>{{((data["log_bin_index"]["data"][3] | int)/1024/1024)|round(2)}} GB</td>
		<td>{{((data["log_bin_index"]["data"][4] | int)/1024/1024)|round(2)}} GB</td>
		<td {% if data["log_bin_index"]["data"][5].split("%")[0] | int > 90 %}style="background:yellow" {% endif %}>{{data["log_bin_index"]["data"][5]}}</td>
		<td>{{data["log_bin_index"]["data"][6]}}</td>
	</tr>
{% endif %}
</table>
{%endif%}

{% if data["havehostdata"] and data["cpu_mem"]["istrue"] %}
<table border="0" width="70%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col">总CPU使用率</th>
		<th class="awrbg" scope="col">总内存使用率</th>
		<th class="awrbg" scope="col">SWAP使用率</th>
		<th class="awrbg" scope="col">系统版本</th>
		<th class="awrbg" scope="col">内核版本</th>
		<th class="awrbg" scope="col">负载</th>
		<th class="awrbg" scope="col">时区</th>
	</tr>
	<tr>
		<td>{{ ((1 - data["cpu_mem"]["uptime"][1]|int/(data["cpu_mem"]["uptime"][0]|int*data["cpu_mem"]["cpu_socket"]|int*data["cpu_mem"]["cpu_core"]|int*data["cpu_mem"]["cpu_thread"]|int))*100)|round(2) }}% </td>
		<td> {{ ((1-data["cpu_mem"]["mem"]["MemAvailable"]|int/data["cpu_mem"]["mem"]["MemTotal"]|int)*100)|round(2) }}%</td>
		<td>{%if data["cpu_mem"]["mem"]["SwapTotal"]|int>0 %} {{ ((1-data["cpu_mem"]["mem"]["SwapFree"]|int/data["cpu_mem"]["mem"]["SwapTotal"]|int)*100)|round(2) }}%{%else%}无SWAP{%endif%}</td>
		<td>{{data["cpu_mem"]["osname"]}}</td>
		<td>{{data["cpu_mem"]["kernel"]}}</td>
		<td>{{data["cpu_mem"]["loadavg"][0]}} {{data["cpu_mem"]["loadavg"][1]}} {{data["cpu_mem"]["loadavg"][2]}}</td>
		<td>{{data["cpu_mem"]["timezone"]}}</td>
	</tr>
</table>
<table border="0" width="25%" class="tdiff">
	<tr>
		<td class="awrbg" scope="col" style="text-align:left">总内存</td>
		<td>{{(data["cpu_mem"]["mem"]["MemTotal"]|int/1024/1024)|round(2)}} GB</td>
	<tr>
	<tr>
		<td class="awrbg" scope="col" style="text-align:left">可用内存</td>
		<td>{{(data["cpu_mem"]["mem"]["MemAvailable"]|int/1024/1024)|round(2)}} GB</td>
	</tr>
	<tr>
		<td class="awrbg" scope="col" style="text-align:left">剩余内存</td>
		<td>{{(data["cpu_mem"]["mem"]["MemFree"]|int/1024/1024)|round(2)}} GB</td>
	</tr>
	<tr>
		<td class="awrbg" scope="col" style="text-align:left">总SWAP</td>
		<td>{{(data["cpu_mem"]["mem"]["SwapTotal"]|int/1024/1024)|round(2)}} GB</td>
	</tr>
	<tr>
		<td class="awrbg" scope="col" style="text-align:left">剩余SWAP</td>
		<td>{{(data["cpu_mem"]["mem"]["SwapFree"]|int/1024/1024)|round(2)}} GB</td>
	</tr>
	<tr>
		<td class="awrbg" scope="col" style="text-align:left">swappiness</td>
		<td>{{data["cpu_mem"]["swappiness"]}}</td>
	</tr>
	<tr>
		<td class="awrbg" scope="col" style="text-align:left">CPU物理颗数</td>
		<td>{{data["cpu_mem"]["cpu_socket"]}}</td>
	</tr>
	<tr>
		<td class="awrbg" scope="col" style="text-align:left">每颗CPU的核心数量</td>
		<td>{{data["cpu_mem"]["cpu_core"]}}</td>
	</tr>
	<tr>
		<td class="awrbg" scope="col" style="text-align:left">每核的线程数</td>
		<td>{{data["cpu_mem"]["cpu_thread"]}}</td>
	</tr>
	<tr>
		<td class="awrbg" scope="col" style="text-align:left">主机名</td>
		<td>{{data["cpu_mem"]["hostname"]}}</td>
	</tr>
	<tr>
		<td class="awrbg" scope="col" style="text-align:left">系统架构</td>
		<td>{{data["cpu_mem"]["platform"]}}</td>
	</tr>
	<tr>
		<td class="awrbg" scope="col" style="text-align:left">内核版本</td>
		<td>{{data["cpu_mem"]["kernel"]}}</td>
	</tr>
	<tr>
		<td class="awrbg" scope="col" style="text-align:left">系统负载</td>
		<td>{{data["cpu_mem"]["loadavg"][0]}} {{data["cpu_mem"]["loadavg"][1]}} {{data["cpu_mem"]["loadavg"][2]}}</td>
	</tr>
</table>
{%endif%}


<!-- 库表信息  -->
<h3 class="awr" id="databases"><a class="awr"></a>数据库信息</h3>
<table border="0" width="70%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col">数据库名</th>
		<th class="awrbg" scope="col">表数量</th>
		<th class="awrbg" scope="col">数据大小</th>
		<th class="awrbg" scope="col">索引大小</th>
		<th class="awrbg" scope="col">总大小</th>
	</tr>
{% if data["databases"]["istrue"] %}
	{% for db in data["databases"]["data"]["databases"]%}
		<tr>
			<td >{{db[0]}}</td>
			<td >{{db[1]}}</td>
			<td >{{(db[2] / 1024 /1024) | round(2) }} MB</td>
			<td >{{(db[3] / 1024 /1024) | round(2) }} MB</td>
			<td >{{((db[3] + db[2]) / 1024 /1024) | round(2) }} MB</td>
		</tr>
	{% else %}
		<tr>无数据库信息</tr>
	{%endfor%}
{%endif%}
</table>

<!-- 库表信息画个图  -->
{% if data["databases"]["istrue"] %}
<div style="margin-bottom:0px;">
<canvas id="databases_p"></canvas>
</div>
<script>
const ctx = document.getElementById('databases_p');
const myChart = new Chart(ctx, {
	type: 'bar',
	data: {
		labels: ['{{data["databases"]["data"]["databases_T"][0] | join("','") }}'],
			datasets: [
				{label: '数据大小',
				data:[{{data["databases"]["data"]["databases_T"][2] | join(",")}}],
				backgroundColor:["rgb(54, 162, 235)"],
				},
				{label: '索引大小',
				data:[{{data["databases"]["data"]["databases_T"][3] | join(",")}}],
				backgroundColor:["rgb(255, 205, 86)"],
				},
				]
		
	},
	options: {
		scales: {
			y: {
				beginAtZero: true
			}
		}
	}
});
myChart.canvas.parentNode.style.height = '50vh'; // 注意bar 长宽比是 2:1  不然会多一块空的出来... 巨TM坑...
myChart.canvas.parentNode.style.width = '100vh';
</script>
{%endif%}


<!-- 用户信息 -->
<h3 class="awr" id="user"><a class="awr"></a>用户信息</h3>
<table border="0" width="70%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col">Host</th>
		<th class="awrbg" scope="col">User</th>
		<th class="awrbg" scope="col">plugin</th>
		<th class="awrbg" scope="col">password_expired</th>
		<th class="awrbg" scope="col">password_lifetime</th>
		<th class="awrbg" scope="col">Super_priv</th>
		<th class="awrbg" scope="col">Grant_priv</th>
		<th class="awrbg" scope="col">account_locked</th>
	</tr>
{% if data["user"]["istrue"] %}
	{% for db in data["user"]["data"]%}
		<tr>
			<td >{{db[0]}}</td>
			<td >{{db[1]}}</td>
			<td >{{db[2]}}</td>
			<td >{{db[3]}}</td>
			<td >{{db[4]}}</td>
			<td >{{db[5]}}</td>
			<td >{{db[6]}}</td>
			<td >{{db[7]}}</td>
		</tr>
	{% else %}
		<tr>无</tr>
	{%endfor%}
{%endif%}
</table>





<!-- 基础参数 -->
<h3 class="awr" id="variables"><a class="awr"></a>重要参数</h3>
<table border="0" width="40%" class="tdiff"">
	<tr>
		<th class="awrbg" scope="col">参数名</th>
		<th class="awrbg" scope="col">值</th>
		<th class="awrbg" scope="col">建议</th>
	</tr>
	<tr>
		<td style="text-align:left">log_bin</td>
		<td>{{data["variables"]["data"]["value"]['log_bin']}}</td>
		{% if data["variables"]["data"]["value"]['log_bin'] != "ON" %} <td style="background:yellow">建议打开binlog</td> {%endif%}
	</tr>
	<tr>
		<td style="text-align:left">innodb_buffer_pool_size</td>
		<td>{{data["variables"]["data"]["value"]['innodb_buffer_pool_size']}}</td>
	</tr>
	<tr>
		<td style="text-align:left">innodb_buffer_pool_instances</td>
		<td>{{data["variables"]["data"]["value"]['innodb_buffer_pool_instances']}}</td>
	</tr>
	<tr>
		<td style="text-align:left">default_storage_engine</td>
		<td>{{data["variables"]["data"]["value"]['default_storage_engine']}}</td>
		{% if data["variables"]["data"]["value"]['default_storage_engine'] != "InnoDB" %} <td style="background:yellow">建议设置InnoDB引擎为默认引擎</td> {%endif%}
	</tr>
	<tr>
		<td style="text-align:left">sync_binlog</td>
		<td>{{data["variables"]["data"]["value"]['sync_binlog']}}</td>
		{% if data["variables"]["data"]["value"]['sync_binlog'] != "1" %} <td style="background:yellow">建议设置sync_binlog=1</td> {%endif%}
	</tr>
	<tr>
		<td style="text-align:left">innodb_flush_log_at_trx_commit</td>
		<td>{{data["variables"]["data"]["value"]['innodb_flush_log_at_trx_commit']}}</td>
		{% if data["variables"]["data"]["value"]['innodb_flush_log_at_trx_commit'] != "1" %} <td style="background:yellow">建议设置innodb_flush_log_at_trx_commit=1</td> {%endif%}
	</tr>
	<tr>
		<td style="text-align:left">transaction_isolation</td>
		<td>{{data["variables"]["data"]["value"]['transaction_isolation']}}</td>
	</tr>
	<tr>
		<td style="text-align:left">read_only</td>
		<td>{{data["variables"]["data"]["value"]['read_only']}}</td>
	</tr>
	<tr>
		<td style="text-align:left">max_connections</td>
		<td>{{data["variables"]["data"]["value"]['max_connections']}}</td>
	</tr>
	<tr>
		<td style="text-align:left">binlog_format</td>
		<td>{{data["variables"]["data"]["value"]['binlog_format']}}</td>
	</tr>
	<tr>
		<td style="text-align:left">binlog_row_image</td>
		<td>{{data["variables"]["data"]["value"]['binlog_row_image']}}</td>
	</tr>
	<tr>
		<td style="text-align:left">expire_logs_days</td>
		<td>{{data["variables"]["data"]["value"]['expire_logs_days']}}</td>
	</tr>
	<tr>
		<td style="text-align:left">max_binlog_size</td>
		<td>{{data["variables"]["data"]["value"]['max_binlog_size']}}</td>
	</tr>
	<tr>
		<td style="text-align:left">innodb_log_file_size</td>
		<td>{{data["variables"]["data"]["value"]['innodb_log_file_size']}}</td>
	</tr>
	<tr>
		<td style="text-align:left">innodb_log_files_in_group</td>
		<td>{{data["variables"]["data"]["value"]['innodb_log_files_in_group']}}</td>
	</tr>
	<tr>
		<td style="text-align:left">innodb_page_size</td>
		<td>{{data["variables"]["data"]["value"]['innodb_page_size']}}</td>
	</tr>
	<tr>
		<td style="text-align:left">innodb_io_capacity</td>
		<td>{{data["variables"]["data"]["value"]['innodb_io_capacity']}}</td>
	</tr>
	<tr>
		<td style="text-align:left">innodb_io_capacity_max</td>
		<td>{{data["variables"]["data"]["value"]['innodb_io_capacity_max']}}</td>
	</tr>
	<tr>
		<td style="text-align:left">server_id</td>
		<td>{{data["variables"]["data"]["value"]['server_id']}}</td>
	</tr>
	<tr>
		<td style="text-align:left">server_uuid</td>
		<td>{{data["variables"]["data"]["value"]['server_uuid']}}</td>
	</tr>
	<tr>
		<td style="text-align:left">slow_query_log</td>
		<td>{{data["variables"]["data"]["value"]['slow_query_log']}}</td>
		{% if data["variables"]["data"]["value"]['slow_query_log'] == "OFF" %} <td style="background:yellow">建议开启慢日志</td> {%endif%}
	</tr>
	<tr>
		<td style="text-align:left">general_log</td>
		<td>{{data["variables"]["data"]["value"]['general_log']}}</td>
		{% if data["variables"]["data"]["value"]['general_log'] == "ON" %} <td style="background:yellow">为了节省空间, 建议关闭general_log</td> {%endif%}
	</tr>
	<tr>
		<td style="text-align:left">gtid_mode</td>
		<td>{{data["variables"]["data"]["value"]['gtid_mode']}}</td>
	</tr>
	<tr>
		<td style="text-align:left">gtid_next</td>
		<td>{{data["variables"]["data"]["value"]['gtid_next']}}</td>
	</tr>
{% if data["variables"]["data"]["value"]["group_replication_single_primary_mode"] is defined %}
	<tr>
		<td style="text-align:left">group_replication_single_primary_mode</td>
		<td>{{data["variables"]["data"]["value"]['group_replication_single_primary_mode']}}</td>
	</tr>
{%endif%}
</table>


<!-- 无主键表 -->
<h3 class="awr" id="no_primary_key"><a class="awr"></a>无主键的表</h3>
<table border="0" width="30%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col">数据库名</th>
		<th class="awrbg" scope="col">表名</th>
	</tr>
{% if data["no_primary_key"]["istrue"] %}
	{% for db in data["no_primary_key"]["data"]%}
		<tr>
			<td >{{db[0]}}</td>
			<td >{{db[1]}}</td>
		</tr>
	{% else %}
		<tr>无</tr>
	{%endfor%}
{%endif%}
</table>

<!-- 非INNODB表-->
<h3 class="awr" id="no_innodb_table"><a class="awr"></a>非INNODB表</h3>
<table border="0" width="40%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col">数据库名</th>
		<th class="awrbg" scope="col">表名</th>
		<th class="awrbg" scope="col">引擎名</th>
	</tr>
{% if data["no_innodb_table"]["istrue"] %}
	{% for db in data["no_innodb_table"]["data"]%}
		<tr>
			<td >{{db[0]}}</td>
			<td >{{db[1]}}</td>
			<td >{{db[2]}}</td>
		</tr>
	{% else %}
		<tr>无</tr>
	{%endfor%}
{%endif%}
</table>

<!-- 各引擎表的数量 -->
{% if data["all_engine_table"]["istrue"] %}
<div>
<canvas id="all_engine_table_p"></canvas>
</div>
<script>
const ctx_all_engine_table = document.getElementById('all_engine_table_p');
const myChart_all_engine_table = new Chart(ctx_all_engine_table, {
	type: 'pie',
	data: {
		labels: ['{{data["all_engine_table"]["data"]["all_engine_table_T"][0] | join("','") }}'],
			datasets: [
				{label: '引擎',
				data:[{{data["all_engine_table"]["data"]["all_engine_table_T"][1] | join(",")}}],
				backgroundColor:colorlist,
				},
				]
		
	},
	options: {
		scales: {
			y: {
				beginAtZero: true
			}
		}
	}
});
myChart_all_engine_table.canvas.parentNode.style.height = '70vh';
myChart_all_engine_table.canvas.parentNode.style.width = '70vh';
//myChart_all_engine_table.canvas.parentNode.style.marginTop = '0vh';
</script>
{%endif%}

<!-- 重复索引的表 -->
<h3 class="awr" id="repeat_index"><a class="awr"></a>重复索引的表</h3>
<table border="0" width="50%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col">数据库名</th>
		<th class="awrbg" scope="col">表名</th>
		<th class="awrbg" scope="col">索引名</th>
		<th class="awrbg" scope="col">字段名</th>
	</tr>
{% if data["repeat_index"]["istrue"] %}
	{% for db in data["repeat_index"]["data"]%}
		<tr>
			<td >{{db[0]}}</td>
			<td >{{db[1]}}</td>
			<td >{{db[2]}}</td>
			<td >{{db[3]}}</td>
		</tr>
	{% else %}
		<tr>无</tr>
	{%endfor%}
{%endif%}
</table>

<!-- 索引数量过多的表-->
<h3 class="awr" id="over_5_index"><a class="awr"></a>索引数量过多的表</h3>
<table border="0" width="40%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col">数据库名</th>
		<th class="awrbg" scope="col">表名</th>
		<th class="awrbg" scope="col">索引数量</th>
	</tr>
{% if data["over_5_index"]["istrue"] %}
	{% for db in data["over_5_index"]["data"]%}
		<tr>
			<td >{{db[0]}}</td>
			<td >{{db[1]}}</td>
			<td >{{db[2]}}</td>
		</tr>
	{% else %}
		<tr>无</tr>
	{%endfor%}
{%endif%}
</table>


<!-- SQL命令执行情况 -->
<h3 class="awr" id="sql_comm"><a class="awr"></a>SQL命令执行情况</h3>
<table border="0" width="40%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col">SQL类型</th>
		<th class="awrbg" scope="col">执行次数</th>
	</tr>
{% if data["sql_comm"]["istrue"] %}
	{% for db in data["sql_comm"]["data"]["sql_comm"]%}
		<tr>
			<td >{{db[0]}}</td>
			<td >{{db[1]}}</td>
		</tr>
	{% else %}
		<tr>无</tr>
	{%endfor%}
{%endif%}
</table>

{% if data["sql_comm"]["istrue"] %}
<div width="100px" height="50px">
<canvas id="sql_comm_p" width="100" height="50"></canvas>
</div>
<script>
const ctx_sql_comm = document.getElementById('sql_comm_p');
const myChart_sql_comm = new Chart(ctx_sql_comm, {
	type: 'doughnut',
	data: {
		labels: ['{{data["sql_comm"]["data"]["sql_comm_T"][0] | join("','") }}'],
			datasets: [
				{label: 'SQL执行情况',
				data:[{{data["sql_comm"]["data"]["sql_comm_T"][1] | join(",")}}],
				backgroundColor:colorlist
				},
				]
		
	},
	options: {
		scales: {
			y: {
				beginAtZero: true
			}
		}
	}
});
myChart_sql_comm.canvas.parentNode.style.height = '70vh';
myChart_sql_comm.canvas.parentNode.style.width = '70vh';
</script>
{%endif%}

	
<!-- 统计信息过期的表 -->
<h3 class="awr" id="over30days_table_static"><a class="awr"></a>统计信息过期的表</h3>
<table border="0" width="70%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col">数据库名</th>
		<th class="awrbg" scope="col">表名</th>
		<th class="awrbg" scope="col">上次更新时间</th>
		<th class="awrbg" scope="col">行数</th>
		<th class="awrbg" scope="col">主索引(页)</th>
		<th class="awrbg" scope="col">其它索引(页)</th>
	</tr>
{% if data["over30days_table_static"]["istrue"] %}
	{% for db in data["over30days_table_static"]["data"]%}
		<tr>
			<td >{{db[0]}}</td>
			<td >{{db[1]}}</td>
			<td >{{db[2]}}</td>
			<td >{{db[3] | int }}</td>
			<td >{{db[4] | int }}</td>
			<td >{{db[5] | int }}</td>
		</tr>
	{% else %}
		<tr>无</tr>
	{%endfor%}
{%endif%}
</table>
	
<!-- 统计信息过期的索引 -->
<h3 class="awr" id="over30days_index_static"><a class="awr"></a>统计信息过期的索引</h3>
<table border="0" width="70%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col">数据库名</th>
		<th class="awrbg" scope="col">表名</th>
		<th class="awrbg" scope="col">索引名</th>
		<th class="awrbg" scope="col">上次更新时间</th>
		<th class="awrbg" scope="col">stat_name</th>
		<th class="awrbg" scope="col">stat_value</th>
		<th class="awrbg" scope="col">stat_description</th>
	</tr>
{% if data["over30days_index_static"]["istrue"] %}
	{% for db in data["over30days_index_static"]["data"]%}
		<tr>
			<td >{{db[0]}}</td>
			<td >{{db[1]}}</td>
			<td >{{db[2]}}</td>
			<td >{{db[3]}}</td>
			<td >{{db[4]}}</td>
			<td >{{db[5] | int }}</td>
			<td >{{db[7]}}</td>
		</tr>
	{% else %}
		<tr>无</tr>
	{%endfor%}
{%endif%}
</table>


<!-- 碎片率超过30%的表-->
<h3 class="awr" id="fragment_table"><a class="awr"></a>碎片率超过30%的表</h3>
<table border="0" width="40%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col">数据库名</th>
		<th class="awrbg" scope="col">表名</th>
		<th class="awrbg" scope="col">碎片大小</th>
		<th class="awrbg" scope="col">碎片率</th>
	</tr>
{% if data["fragment_table"]["istrue"] %}
	{% for db in data["fragment_table"]["data"]%}
		<tr>
			<td >{{db[0]}}</td>
			<td >{{db[1]}}</td>
			<td >{{(db[2]/1024/1024)|round(2)}} MB</td>
			<td >{{db[3] * 100}} %</td>
		</tr>
	{% else %}
		<tr>无</tr>
	{%endfor%}
{%endif%}
</table>



<h3 class="awr" id="binlog_grows"><a class="awr"></a>binlog信息变化</h3>
<!-- 这个地方的顺序也是很重要, binlog_grows放在前面, 可能会报错, 因为python是从左往右执行的 -->
{% if data["havehostdata"] and  data["binlog_grows"]["istrue"] %}
<div ">
<canvas id="binlog_grows_p" width="100" height="50"></canvas>
</div>
<script>
const ctx_binlog_grows = document.getElementById('binlog_grows_p');
const myChart_binlog_grows = new Chart(ctx_binlog_grows, {
	type: 'line',
	data: {
		labels: ['{{data["binlog_grows"]["data"]["binlog_stat_df_group_by_T"][0] | join("','") }}'],
			datasets: [
				{label: 'binlog增长变化',
				data:[{{data["binlog_grows"]["data"]["binlog_stat_df_group_by_T"][1] | join(",")}}],
				backgroundColor:colorlist,
				yAxisID:'A',
				fill: true,
				},
				{label: 'binlog切换次数',
				data:[{{data["binlog_grows"]["data"]["binlog_stat_df_group_by_T"][2] | join(",")}}],
				backgroundColor:colorlist,
				yAxisID:'B',
				},
				]
		
	},
	options: {
		scales: {
			// v3版本 yAexs --> y  https://www.chartjs.org/docs/master/getting-started/v3-migration.html
			y:{
			display: true,
			stacked: true,
			}
		}
	}
});
myChart_binlog_grows.canvas.parentNode.style.height = '50vh';
myChart_binlog_grows.canvas.parentNode.style.width = '100vh';
//myChart_binlog_grows.canvas.parentNode.style.marginTop = 'auto';
</script>
{%else%}
<p>无binlog信息</p>
{%endif%}

<!--</table>-->

<!-- TOP20 表-->
<h3 class="awr" id="top20_table"><a class="awr"></a>最大的前20张表</h3>
<table border="0" width="40%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col">数据库名</th>
		<th class="awrbg" scope="col">表名</th>
		<th class="awrbg" scope="col">引擎</th>
		<th class="awrbg" scope="col">行数</th>
		<th class="awrbg" scope="col">数据大小</th>
		<th class="awrbg" scope="col">索引大小</th>
		<th class="awrbg" scope="col">总大小</th>
	</tr>
{% if data["top20_table"]["istrue"] %}
	{% for db in data["top20_table"]["data"]%}
		<tr>
			<td >{{db[0]}}</td>
			<td >{{db[1]}}</td>
			<td >{{db[2]}}</td>
			<td >{{db[3]}}</td>
			<td >{{(db[4] / 1024 /1024) | round(2)}} MB</td>
			<td >{{(db[5] / 1024 /1024) | round(2)}} MB</td>
			<td >{{((db[4] +db[5]) / 1024 /1024) | round(2)}} MB</td>
		</tr>
	{% else %}
		<tr>无</tr>
	{%endfor%}
{%endif%}
</table>

<!-- 大表-->
<h3 class="awr" id="big_table"><a class="awr"></a>大表</h3>
<table border="0" width="40%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col">数据库名</th>
		<th class="awrbg" scope="col">表名</th>
		<th class="awrbg" scope="col">数据行数</th>
		<th class="awrbg" scope="col">数据大小</th>
	</tr>
{% if data["big_table"]["istrue"] %}
	{% for db in data["big_table"]["data"]%}
		<tr>
			<td >{{db[0]}}</td>
			<td >{{db[1]}}</td>
			<td >{{db[2]|int}}</td>
			<td >{{(db[3]|int/1024/1024) | round(2)}} MB</td>
		</tr>
	{% else %}
		<tr>无</tr>
	{%endfor%}
{%endif%}
</table>

<!-- 冷表-->
<h3 class="awr" id="cold_table"><a class="awr"></a>冷表(超过60天未使用的表)</h3>
<table border="0" width="40%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col">数据库名</th>
		<th class="awrbg" scope="col">表名</th>
		<th class="awrbg" scope="col">最近访问时间</th>
	</tr>
{% if data["cold_table"]["istrue"] %}
	{% for db in data["cold_table"]["data"]%}
		<tr>
			<td >{{db[0]}}</td>
			<td >{{db[1]}}</td>
			<td >{{db[2]}}</td>
		</tr>
	{% else %}
		<tr>无</tr>
	{%endfor%}
{%endif%}
</table>

<!-- 插件-->
<h3 class="awr" id="plugins"><a class="awr"></a>插件</h3>
<table border="0" width="70%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col" title="插件名字">PLUGIN_NAME</th>
		<th class="awrbg" scope="col" title="">PLUGIN_STATUS</th>
		<th class="awrbg" scope="col" title="">PLUGIN_TYPE</th>
		<th class="awrbg" scope="col" title="">PLUGIN_TYPE_VERSION</th>
		<th class="awrbg" scope="col" title="">PLUGIN_AUTHOR</th>
		<th class="awrbg" scope="col" title="">LOAD_OPTION</th>
	</tr>
{% if data["plugins"]["istrue"] %}
	{% for db in data["plugins"]["data"]%}
		<tr>
			<td >{{db[0]}}</td>
			<td >{{db[1]}}</td>
			<td >{{db[2]}}</td>
			<td >{{db[3]}}</td>
			<td >{{db[4]}}</td>
			<td >{{db[5]}}</td>
		</tr>
	{%endfor%}
{%endif%}
</table>


<!-- 下面结果跟性能相关 -->
<!-- 锁等待-->
<h3 class="awr" id="innodb_lock_waits"><a class="awr"></a>锁等待</h3>
<table border="0" width="70%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col" title="">locked_table</th>
		<th class="awrbg" scope="col" title="阻塞时间">wait_age_secs</th>
		<th class="awrbg" scope="col" title="相关索引">locked_index</th>
		<th class="awrbg" scope="col" title="阻塞类型">locked_type</th>
		<th class="awrbg" scope="col" title="被阻塞SQL">waiting_query</th>
		<th class="awrbg" scope="col" title="阻塞SQL">blocking_query</th>
		<th class="awrbg" scope="col" title="">sql_kill_blocking_query</th>
	</tr>
{% if data["innodb_lock_waits"]["istrue"] %}
	{% for db in data["innodb_lock_waits"]["data"]%}
		<tr>
			<td >{{db[0]}}</td>
			<td >{{db[1]}}</td>
			<td >{{db[2]}}</td>
			<td >{{db[3]}}</td>
			<td >{{db[4]}}</td>
			<td >{{db[5]}}</td>
			<td >{{db[6]}}</td>
		</tr>
	{% else %}
		<tr>无</tr>
	{%endfor%}
{%endif%}
</table>

<!-- 未使用索引的表 (performance_schema库下的时间均为皮秒  (皮秒 纳秒 微秒 毫秒 秒))-->
<h3 class="awr" id="full_table"><a class="awr"></a>使用全表扫描的表</h3>
<table border="0" width="70%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col">数据库名</th>
		<th class="awrbg" scope="col">表名</th>
		<th class="awrbg" scope="col">访问次数</th>
		<th class="awrbg" scope="col">总时间</th>
		<th class="awrbg" scope="col">平均时间</th>
		<th class="awrbg" scope="col">select数据量(行)</th>
		<th class="awrbg" scope="col">select总时间</th>
		<th class="awrbg" scope="col">select平均时间</th>
	</tr>
{% if data["full_table"]["istrue"] %}
	{% for db in data["full_table"]["data"]%}
		<tr>
			<td >{{db[0]}}</td>
			<td >{{db[1]}}</td>
			<td >{{db[2]}}</td>
			<td >{{(db[3] |int / 1000000000) |round(2)}} ms</td>
			<td >{{(db[4] |int / 1000000) | round(2) }} us</td>
			<td >{{db[5]}} </td>
			<td >{{(db[6]|int/1000000000)|round(2)}} ms</td>
			<td >{{(db[7]|int/1000000)|round(2)}} us</td>
		</tr>
	{% else %}
		<tr>无</tr>
	{%endfor%}
{%endif%}
</table>


<!-- top20 sql-->
<h3 class="awr" id="top20_sql"><a class="awr"></a>执行次数最多的SQL TOP20</h3>
<table border="0" width="70%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col">数据库名</th>
		<th class="awrbg" scope="col">执行次数</th>
		<th class="awrbg" scope="col">第一次执行时间</th>
		<th class="awrbg" scope="col">最后一次执行时间</th>
		<th class="awrbg" scope="col">影响行数</th>
		<th class="awrbg" scope="col">SQL摘要(脱敏)</th>
	</tr>
{% if data["top20_sql"]["istrue"] %}
	{% for db in data["top20_sql"]["data"]%}
		<tr>
			<td >{{db[0]}}</td>
			<td >{{db[1]}}</td>
			<td >{{db[2]}}</td>
			<td >{{db[3]}}</td>
			<td >{{db[4]}}</td>
			{%if (db[5] | length) > 130 %}
				<td>
				<details>
				<summary>SQL太长, 请点击查看详情</summary>
				<p>{{db[5]}}</p>
				</details>
				</td>
			{%else%}
				<td >{{db[5]}}')"</td>
			{%endif%}
		</tr>
	{% else %}
		<tr>无</tr>
	{%endfor%}
{%endif%}
</table>

<!-- 使用内存最多的前20张表 sql-->
<h3 class="awr" id="innodb_buffer_stats_by_table"><a class="awr"></a>使用内存最多的表 TOP20</h3>
<table border="0" width="70%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col">object_schema</th>
		<th class="awrbg" scope="col">object_name</th>
		<th class="awrbg" scope="col" title="为表分配的总字节数">allocated</th>
		<th class="awrbg" scope="col" title="为表分配的数据字节数">data</th>
		<th class="awrbg" scope="col" title="为表分配的总页数">pages</th>
		<th class="awrbg" scope="col" title="为表分配的hash页数">pages_hashed</th>
		<th class="awrbg" scope="col" >pages_old</th>
		<th class="awrbg" scope="col" title="表的缓存行数">rows_cached</th>
	</tr>
{% if data["innodb_buffer_stats_by_table"]["istrue"] %}
	{% for db in data["innodb_buffer_stats_by_table"]["data"]%}
		<tr>
			<td >{{db[0]}}</td>
			<td >{{db[1]}}</td>
			<td >{{db[2]}}</td>
			<td >{{db[3]}}</td>
			<td >{{db[4]}}</td>
			<td >{{db[5]}}</td>
			<td >{{db[6]}}</td>
			<td >{{db[7]}}</td>
	{%endfor%}
{%endif%}
</table>

<!-- IO等待事件汇总 -->
<h3 class="awr" id="io_global_by_wait_by_bytes"><a class="awr"></a>IO等待事件</h3>
<table border="0" width="70%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col" title="I/O 事件名称">event_name</th>
		<th class="awrbg" scope="col" title="I/O 事件的总发生次数">total</th>
		<th class="awrbg" scope="col" title="I/O 事件定时发生的总等待时间">total_latency</th>
		<th class="awrbg" scope="col" title="I/O 事件定时发生的最小单次等待时间">min_latency</th>
		<th class="awrbg" scope="col" title="I/O 事件每次定时发生的平均等待时间">avg_latency</th>
		<th class="awrbg" scope="col" title="I/O 事件定时发生的最大单次等待时间">max_latency</th>
		<th class="awrbg" scope="col" title="I/O 事件的读取请求数">count_read</th>
		<th class="awrbg" scope="col" title="I/O 事件读取的总字节数">total_read</th>
		<th class="awrbg" scope="col" title="I/O 事件每次读取的平均字节数">avg_read</th>
		<th class="awrbg" scope="col" title="I/O 事件的写入请求数">count_write</th>
		<th class="awrbg" scope="col" title="I/O 事件写入的总字节数">total_written</th>
		<th class="awrbg" scope="col" title="I/O 事件每次写入的平均字节数">avg_written</th>
		<th class="awrbg" scope="col" title="I/O 事件读取和写入的总字节数">total_requested</th>
	</tr>
{% if data["io_global_by_wait_by_bytes"]["istrue"] %}
	{% for db in data["io_global_by_wait_by_bytes"]["data"]%}
		<tr>
			<td >{{db[0]}}</td>
			<td >{{db[1]}}</td>
			<td >{{db[2]}}</td>
			<td >{{db[3]}}</td>
			<td >{{db[4]}}</td>
			<td >{{db[5]}}</td>
			<td >{{db[6]}}</td>
			<td >{{db[7]}}</td>
			<td >{{db[8]}}</td>
			<td >{{db[9]}}</td>
			<td >{{db[10]}}</td>
			<td >{{db[11]}}</td>
			<td >{{db[12]}}</td>
	{%endfor%}
{%endif%}
</table>

<!-- 使用内存最多的主机 -->
<h3 class="awr" id="memory_by_host_by_current_bytes"><a class="awr"></a>使用内存最多的主机 TOP20</h3>
<table border="0" width="70%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col" title="">host</th>
		<th class="awrbg" scope="col" title="当前使用的内存(尚未释放)块数">current_count_used</th>
		<th class="awrbg" scope="col" title="当前使用的内存(尚未释放)大小">current_allocated</th>
		<th class="awrbg" scope="col" title="当前为主机分配的每个内存块的字节数">current_avg_alloc</th>
		<th class="awrbg" scope="col" title="主机的最大单个当前内存分配(字节)">current_max_alloc</th>
		<th class="awrbg" scope="col" title="主机的总内存分配大小">total_allocated</th>
	</tr>
{% if data["memory_by_host_by_current_bytes"]["istrue"] %}
	{% for db in data["memory_by_host_by_current_bytes"]["data"]%}
		<tr>
			<td >{{db[0]}}</td>
			<td >{{db[1]}}</td>
			<td >{{db[2]}}</td>
			<td >{{db[3]}}</td>
			<td >{{db[4]}}</td>
			<td >{{db[5]}}</td>
	{%endfor%}
{%endif%}
</table>

<!-- 使用内存最多的用户 -->
<h3 class="awr" id="memory_by_user_by_current_bytes"><a class="awr"></a>使用内存最多的用户 TOP20</h3>
<table border="0" width="70%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col" title="">user</th>
		<th class="awrbg" scope="col" title="当前使用的内存(尚未释放)块数">current_count_used</th>
		<th class="awrbg" scope="col" title="当前使用的内存(尚未释放)大小">current_allocated</th>
		<th class="awrbg" scope="col" title="当前为主机分配的每个内存块的字节数">current_avg_alloc</th>
		<th class="awrbg" scope="col" title="主机的最大单个当前内存分配(字节)">current_max_alloc</th>
		<th class="awrbg" scope="col" title="主机的总内存分配大小">total_allocated</th>
	</tr>
{% if data["memory_by_user_by_current_bytes"]["istrue"] %}
	{% for db in data["memory_by_user_by_current_bytes"]["data"]%}
		<tr>
			<td >{{db[0]}}</td>
			<td >{{db[1]}}</td>
			<td >{{db[2]}}</td>
			<td >{{db[3]}}</td>
			<td >{{db[4]}}</td>
			<td >{{db[5]}}</td>
	{%endfor%}
{%endif%}
</table>



<!-- 使用临时表的SQL-->
<h3 class="awr" id="tmp_table_file"><a class="awr"></a>使用临时表/文件的SQL</h3>
<table border="0" width="70%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col">数据库名</th>
		<th class="awrbg" scope="col">执行次数</th>
		<th class="awrbg" scope="col">使用临时文件次数</th>
		<th class="awrbg" scope="col">使用临时表次数</th>
		<th class="awrbg" scope="col">影响行数</th>
		<th class="awrbg" scope="col">SQL摘要(脱敏)</th>
	</tr>
{% if data["tmp_table_file"]["istrue"] %}
	{% for db in data["tmp_table_file"]["data"]%}
		<tr>
			<td >{{db[0]}}</td>
			<td >{{db[1]|int}}</td>
			<td >{{db[2]|int}}</td>
			<td >{{db[3]|int}}</td>
			<td >{{db[4]|int}}</td>
			{%if (db[5] | length) > 130 %}
				<td>
				<details>
				<summary>SQL太长, 请点击查看详情</summary>
				<p>{{db[5]}}</p>
				</details>
				</td>
			{%else%}
				<td >{{db[5]}}')"</td>
			{%endif%}
		</tr>
	{% else %}
		<tr>无</tr>
	{%endfor%}
{%endif%}
</table>


<!-- top20 慢sql-->
<h3 class="awr" id="slow_sql"><a class="awr"></a>top20 慢sql</h3>
<table border="0" width="70%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col">执行次数</th>
		<th class="awrbg" scope="col">Query_time_avg</th>
		<th class="awrbg" scope="col">Query_time_max</th>
		<th class="awrbg" scope="col">Query_time_median</th>
		<th class="awrbg" scope="col">Query_time_pct_95</th>
		<th class="awrbg" scope="col">数据库</th>
		<th class="awrbg" scope="col">checksum</th>
		<th class="awrbg" scope="col">sql</th>
	</tr>
{% if data["havehostdata"] and data["slow_sql"]["istrue"] %}
	{% for db in data["slow_sql"]["data"]%}
		<tr>
			<td >{{db[1]}}</td>
			<td >{{db[2]}}</td>
			<td >{{db[3]}}</td>
			<td >{{db[5]}}</td>
			<td >{{db[6]}}</td>
			<td >{{db[7]}}</td>
			<td >{{db[0]}}</td>
			{%if (db[8] | length) > 200 %}
				<td><details><summary>SQL太长, 请点击查看详情</summary><p>{{db[8]}}</p></details></td>
			{%else%}
				<td >{{db[8]}}')"</td>
			{%endif%}
		</tr>
	{% else %}
		<tr>无</tr>
	{%endfor%}
{%endif%}
</table>

<!-- 错误日志 -->
<h3 class="awr" id="error_log"><a class="awr"></a>错误日志</h3>
<table border="0" width="70%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col">Time</th>
		<th class="awrbg" scope="col">error</th>
		<th class="awrbg" scope="col">info</th>
	</tr>
{% if data["havehostdata"] and data["error_log"]["istrue"] %}
	{% for db in data["error_log"]["data"]%}
		<tr>
			<td >{{db[0]}}</td>
			<td >{{db[2]}}</td>
			<td >{{db[3]}}</td>
		</tr>
	{%endfor%}
{%endif%}
</table>

<!-- 主从信息-->
{% if data["current_role"]["istrue"]  %}
<h3 class="awr" id="cluster_slave"><a class="awr"></a>集群/主从信息</h3>
{% if data["slave_status"]["istrue"] and (data["slave_status"]["data"]|count)>0 %}
<table border="0" width="70%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col">主库地址</th>
		<th class="awrbg" scope="col">主库端口</th>
		<th class="awrbg" scope="col">Slave_IO_Running</th>
		<th class="awrbg" scope="col">Slave_SQL_Running</th>
		<th class="awrbg" scope="col">Master_Bind(延迟)</th>
	</tr>
	<tr>
		<td>{{data["slave_status"]["data"][1]}}</td>
		<td>{{data["slave_status"]["data"][3]}}</td>
		<td {% if data["slave_status"]["data"][10] != "Yes" %}style="background:red"{%endif%} >{{data["slave_status"]["data"][10]}}</td>
		<td {% if data["slave_status"]["data"][11] != "Yes" %}style="background:red"{%endif%} >{{data["slave_status"]["data"][11]}}</td>
		<td {% if data["slave_status"]["data"][46]|int > 300 %}style="background:yellow" {%endif%}>{{data["slave_status"]["data"][46]}}</td>
	</tr>
</table>
{%endif%}

{% if data["replication_group_members"]["istrue"] and (data["replication_group_members"]["data"]|count)>0 %}
<table border="0" width="70%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col">CHANNEL_NAME</th>
		<th class="awrbg" scope="col">MEMBER_ID</th>
		<th class="awrbg" scope="col">MEMBER_HOST</th>
		<th class="awrbg" scope="col">MEMBER_PORT</th>
		<th class="awrbg" scope="col">MEMBER_STATE</th>
	</tr>
	{% for db in data["replication_group_members"]["data"] %}
		<tr>
			<td>{{db[0]}}</td>
			<td>{{db[1]}}</td>
			<td>{{db[2]}}</td>
			<td>{{db[3]}}</td>
			<td {% if (db[4] == "OFFLINE") or (db[4] == "ERROR") or (db[4] == "UNREACHABLE") %} style="background-color:red" {%elif db[4] == "RECOVERING" %} style="background-color:yellow" {%endif%} >{{db[4]}}</td>
		</tr>
	{%else%}
	<tr>无</tr>
	{%endfor%}
</table>
{%endif%}

{% if data["replication_group_member_stats"]["istrue"] and (data["replication_group_member_stats"]["data"]|count)>0 %}
<table border="0" width="80%" class="tdiff">
	<tr>
		<th class="awrbg" scope="col">CHANNEL_NAME</th>
		<th class="awrbg" scope="col" title="该组的当前视图标识符">VIEW_ID</th>
		<th class="awrbg" scope="col" title="成员服务器 UUID">MEMBER_ID</th>
		<th class="awrbg" scope="col" title="队列中等待冲突检测检查的事务数。一旦检查了事务是否存在冲突，如果它们通过了检查，它们也会排队等待应用">COUNT_TRANSACTIONS_IN_QUEUE</th>
		<th class="awrbg" scope="col" title="已检查冲突的事务数">COUNT_TRANSACTIONS_CHECKED</th>
		<th class="awrbg" scope="col" title="未通过冲突检测检查的事务数">COUNT_CONFLICTS_DETECTED</th>
		<th class="awrbg" scope="col" title="可用于认证但尚未被垃圾回收的事务行数">COUNT_TRANSACTIONS_ROWS_VALIDATING</th>
	</tr>
	{% for db in data["replication_group_member_stats"]["data"] %}
		<tr>
			<td>{{db[0]}}</td>
			<td>{{db[1]}}</td>
			<td>{{db[2]}}</td>
			<td>{{db[3]}}</td>
			<td>{{db[4]}}</td>
			<td>{{db[5]}}</td>
			<td>{{db[6]}}</td>
		</tr>
	{%else%}
	<tr>无</tr>
	{%endfor%}
</table>
{%endif%}

{%endif%}
</body>
</html>
"""
