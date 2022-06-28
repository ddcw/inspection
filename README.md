#介绍

python编写的mysql数据库巡检工具, 巡检数据库和操作系统信息, 前端图表插件来自 chartjs

软件执行过程分为: 采集数据, 分析数据, 填充模板

主要使用组件如下:

pymysql  #连接mysql

paramiko #通过ssh连接主机

pandas #数据分析

jinja2  #模板填充

flask #提供后端服务(Werkzeug)

chartjs #前端图表



项目地址:https://github.com/ddcw/inspection



# 使用方法

## 命令行

```shell
python3 main.py  -p 123456
```

## web界面

```shell
python3 main.py --web #然后用浏览器访问 http://127.0.0.1:6121 
```



## 批量巡检

需要自己编写json文件,  (感觉还不如自己写个for... 所以后续不会对这一块做啥优化之类的)

PARALLEL表示并行度, 也就是同时巡检多少个

TEST_ONLY  True 表示仅测试, 和 --test-only一样的效果,  有任何一个都仅测试

格式参考如下:

```
{
"VERSION":"1.0",
"PARALLEL":2,
"TEST_ONLY":"False",
"DEFAULT_HOST":"127.0.0.1",
"DEFAULT_PORT":"3306",
"DEFAULT_USER":"root",
"DEFAULT_PASSWORD":"123456",
"DEFAULT_SSH_PORT":22,
"DEFAULT_SSH_USER":"root",
"DEFAULT_SSH_PASSWORD":"123456",
"DATA":[
	{"host":"192.168.101.51", "port":3312, "user":"root", "password":"123456", "ssh_port":22, "ssh_user":"root", "ssh_password":"123456"},
	{"host":"192.168.101.19", "port":"3308"}
	]
}
```

命令如下:

```shell
python main.py --mf testmf.json
```







# 数据采集对象

## mysql

详情请看文件 ../ddcw_inspection/collection_detail.py

sys, performance_schema, information_schema, mysql库都有涉及到



## 操作系统

/etc/os-release

/proc/sys/kernel/hostname

uname

lscpu

/proc/uptime

/proc/interrupts

/proc/meminfo

df

pvs

lsblk

/etc/localtime

/proc/net/tcp

/proc/loadavg

dmesg

还挺多的嘛....



# 数据格式

data["DBINFO"]  #数据库信息

data["HOSTINFO"] #主机信息



# 分析展示结果

| 对象         | 对象类型 | 描述                                       | 备注                                       |
| ---------- | ---- | ---------------------------------------- | ---------------------------------------- |
| 数据库基础信息    | 表    | 基础信息+基础信息+安全与稳定+数据库角色                    |                                          |
| 主机信息       | 表    | 数据目录,日志目录, 操作系统基础信息                      | 使用率超过90% 背景颜色变为黄色                        |
| 数据库信息      | 表+图  | 数据库表索引大小                                 | 有个图确实挺直观的                                |
| 用户信息       | 表    | 用户,是否过期,有没有被锁                            | 不采集密码字段,所以不考虑账号密码相等的问题                   |
| 重要参数       | 表    | 一些常见的数据库参数                               |                                          |
| 无主键的表      | 表    | 无主键的表                                    |                                          |
| 非InnoDB表   | 表+图  |                                          |                                          |
| 重复索引       | 表    |                                          | indx_1(id,name)  indx_2(id,age)  这种id也算重复索引 |
| 索引数量过多的表   | 表    | 索引数量超过5(不含)的表                            |                                          |
| SQL执行情况    | 表+图  | status种  Com_开头的统计                       |                                          |
| 统计信息过期的表   | 表    | 最近更新统计信息时间超过30天                          |                                          |
| 碎片率超过30%的表 | 表    | data_free/(data_length+data_free)>0.3    | 排除小表(data_free<40MB)                     |
| binlog信息变化 | 图    | binlog的切换频率和每天的大小变化                      | 数据来自操作系统, 参考命令 stat binlog00003          |
| 最大的表       | 表    | TOP20 表排序                                |                                          |
| 大表         | 表    | 大于1000W行 且大于30GB                         |                                          |
| 冷表         | 表    | 最近访问时间(UPDATE_TIME)是在60天以前               |                                          |
| 插件         | 表    |                                          |                                          |
| 锁等待        | 表    | sys.innodb_lock_waits                    |                                          |
| 使用全表扫描的表   | 表    | table_io_waits_summary_by_index_usage中INDEX_NAME为空 |                                          |
| 执行次数最多的SQL | 表    | events_statements_summary_by_digest中COUNT_STAR最多的前20条SQL | SQL太长(>130)会隐藏                           |
| 使用内存最多的表   | 表    | sys.innodb_buffer_stats_by_table         | 根据rows_cached排序                          |
| IO等待事件     | 表    | sys.io_global_by_wait_by_bytes           |                                          |
| 使用内存最多的主机  | 表    | memory_by_host_by_current_bytes          |                                          |
| 使用内存最多的用户  | 表    | memory_by_user_by_current_bytes          |                                          |
| 使用临时表的SQL  | 表    | events_statements_summary_by_digest      | 含临时文件                                    |
| 慢SQL       | 表    | 执行时间最长的前20条慢SQL                          | 本条是使用pt-query-digest分析的, 根据Query_time_median排序 |
| 错误日志       | 表    | error.log  中含ERROR的最新20条                 |                                          |
| 集群/主从信息    | 表    | show slave status replication_group_members replication_group_member_stats |                                          |
|            |      |                                          |                                          |



# 支持范围

操作系统: linux 

数据库: mysql5.7/8.0





# TODO

引入评分机制, 给数据库打分





# BUG修复

2022.05.17

修复 jinja2 计算cpu使用率 为0 的异常



2022.05.16

修复无主键表,非innodb表含视图问题

修复碎片表Cannot perform 'rand_' with a dtyped [float64] array and scalar of type [bool]



2022.05.13

修复win环境乱码问题, 在特定情况下 可以在windows上使用此脚本



# changelog

2022.06.07 v1.2

新增支持巡检PXC

优化后台巡检进度显示



2022.05.16  v1.1

支持windows使用此脚本

美化前台界面

修复已知BUG





2022.04.29    v1.0   

移除matplotlib.pyplot , 新增chartjs

新增web控制台操作

新增binlog变化

新增批量巡检



2022.04.11   v0.3  

修复已知BUG



2022.03.22    v0.2  

可以指定模板文件



2022.03.17    v0.11 

测试版本..

