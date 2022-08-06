

# 介绍

巡检mysql数据库的, 支持单机, 主从, MGR, PXC环境

备注: 尽量查询sys库(方便看)



# 要求

数据库启用performance_schema  巡检脚本查询的performance_schema, sys视图均依赖performance_schema

```
select @@performance_schema; -- 必须为1
```



# 支持范围

x86_64/aarch64 Linux  (其它环境请使用源码)

mysql 5.7/8.0 单主, 主从, 主主, MGR, PXC 





# 使用

## 命令行巡检

```shell
./ddcw_inspection --host 127.0.0.1 --port 3322  --user root --password 123456
```



## web控制台巡检

```shell
./ddcw_inspection   #然后登录控制台操作
```



## 源码使用

```shell
python main.py --help
```





# 巡检项描述

conf/conf.yaml 



# BUG修复记录

重构后第一个版本..



# change log

| 变更时间       | 版本    | 描述                                       |
| ---------- | ----- | ---------------------------------------- |
| 2022.03.17 | v0.11 | 测试版本..                                   |
| 2022.03.22 | v0.2  | 可以指定模板文件                                 |
| 2022.04.11 | v0.3  | 修复已知BUG                                  |
| 2022.04.29 | v1.0  | 1. 移除matplotlib.pyplot , 新增chartjs<br />2. 新增web控制台操作<br />3. 新增binlog变化<br />4. 新增批量巡检 |
| 2022.05.16 | v1.1  | 1. 支持windows使用此脚本<br />2. 美化前台界面<br />3. 修复已知BUG |
| 2022.06.07 | v1.2  | 1. 新增支持巡检PXC<br />2. 优化后台巡检进度显示          |
| 2022.07.05 | v2.0  | 重构(未发布).<br />增加配置文件(yaml)和日志功能.<br />优化并发巡检<br />新增持续巡检项(比如某段时间的网络流量,), 仅限数据库层面 |
| 2022.08.06 | v2.1  | 1. 引入bootstrap和bootstrap-table<br />2. 新增评分机制 |
|            |       |                                          |

