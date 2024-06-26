

# 介绍

自动巡检MYSQL数据库, 支持主从,MGR,PXC环境. 能自动识别节点关系.

支持html和word版巡检报告.

可多台服务器共同完成一个task.

备注:V2.2版本的评分策略较为宽泛,得分都有点显高....



# 支持范围

x86_64/aarch64 Linux  (其它环境请使用源码)

mysql 5.7/8.0 单主, 主从, 主主, MGR, PXC 



# mini版(SHELL版)

本来准备3.0使用纯shell来写的, 但shell太有限了. 所以就取消了3.0版, 还是维持2.x版本的这种风格吧....

这个shell版算未完成版吧.. 但还是有参考价值的.

下载地址: [https://github.com/ddcw/inspection/blob/main/ddcw_inspection_v3.0.sh](https://github.com/ddcw/inspection/blob/main/ddcw_inspection_v3.0.sh)

用法:

```bash
sh ddcw_inspection_v3.0.sh --help
sh ddcw_inspection_v3.0.sh -h127.0.0.1 -P3314 -p123456 -uroot
```



# 使用

## 创建巡检用户并授权(可以跳过)

```mysql

create user 'u1'@'%' identified by '123456';

grant select on *.* to 'u1'@'%';

grant replication client on *.* to 'u1'@'%';

grant execute on *.* to 'u1'@'%';

```

## 命令行巡检

巡检报告默认均在 tmp目录下面(配置文件指定的路径)

### 单机巡检

应用场景: 不方便使用web控制台(无浏览器,或者网络不允许),  简单的巡检下某台主机

```shell
./ddcw_inspection --host 127.0.0.1 --port 3322  --user root --password 123456
```

### 批量巡检

应用场景: 批量巡检数据库

```shell
./ddcw_inspection -f mf.yaml #具体信息看mf.yaml(conf目录下有例子)
```

### 特殊情况

采集数据和生成报告得分开的场景, 采集报告使用shell, 生成报告使用python/二进制程序

采集数据

```shell
cd tools
vim coll_data.sh #修改对应的主机名,端口,账号密码等信息
sh coll_data.sh coll_data_by_shell.conf #采集数据
```

生成巡检报告

```shell
./ddcw_inspection -a xxxx.xml  #目前只支持单个文件.
```





## web控制台巡检

```shell
./ddcw_inspection   #然后登录控制台操作 http://127.0.0.1 
```

登录控制台, 在<开始巡检>处填写对应信息, 然后点击开始巡检即可.

巡检中的状态可在<巡检中>查看.

巡检完成的结果可在<巡检完成>中查看.





## 源码使用

```shell
python main.py --help
```





## 多台服务器共同协作

manager可以在多台服务器之间共享对象. 所以可以多台服务器之间共同巡检某个task(都去队列里面竞争)

server_1启动 `./ddcw_inspection`

server_2修改对应的manager的ip和端口和密码, 然后启动 `./ddcw_inspection`

server_n 同理.

注: 其它server在巡检的时候不能暂停, 否则对应的实例信息就会丢失. (可以捕获信号量, 然后重新把实例的信息加入队列..)



# 关于MYSQL巡检

## 异常(告警)级别定义

根据影响程度扣分程度也不同, 默认扣分只是多数巡检项的扣分策略. 巡检扣分由巡检项自己定义.

注: 主机巡检内容不计入评分

| 级别           | code | 描述                                       | 默认扣分 |
| ------------ | ---- | ---------------------------------------- | ---- |
| 普通( general) | 0    | 仅展示, 不做评分计算. 方便使用者了解数据库的情况.(比如数据库基础信息,版本等, 巡检期间的TPS/QPS流量等) | 0%   |
| 正常(normal)   | 1    | 数据库此巡检项符合预期, 数据库正常运行                     | 0%   |
| 提示(tips)     | 2    | 影响微乎其微, 可以忽略. 对系统正常运行不影响. (比如字符集)        | 10%  |
| 警告(Warning)  | 3    | 对系统影响一般, 会导致数据库性能降低. (比如redo大小.)         | 40%  |
| 严重(serious)  | 4    | 对系统影响严重. 严重拖慢数据库运行(比如统计信息太旧,无主键查询), 或者对数据库安全有影响.(比如双1, 用户密码一样) | 75%  |
| 致命(deadly)   | 5    | 对数据库影响特别严重. 可能导致数据库无法运行或者宕机.             | 100% |



## 巡检分类定义

| 类型     | code | 描述                                       |
| ------ | ---- | ---------------------------------------- |
| 资源     | 1    | 内存和磁盘空间相关                                |
| 安全与稳定  | 2    | 系统账号的安全, 数据的安全(不丢数据) 比如:弱密码, 双1等         |
| 集群与高可用 | 3    | 主从,MGR,PXC等                              |
| 性能与规范  | 4    | 对MYSQL运行有影响的, 或者数据库设计规范(比如字段不能为空, 非innodb表) |
| 参数     | 5    | 数据库参数.(此选项仅含参数, 也只有此选项有参数. 其它项可能有关于参数的, 但都归于这一项) |
| 其它     | 6    | 不好归类的.                                   |



## 配置文件

conf/global.conf为全局配置选项. 里面有注释, 这里就不介绍了



##  巡检项详情

巡检项分为3部分

固定巡检项(数据库状态的show global status)

固定巡检项(数据库基础信息和其它巡检项需要使用的数据)

可配置的巡检项(conf/inspection.conf)



## 各进程介绍

main: 主进程, 负责启动其它进程和接收用户的参数(1个)

work_inspection: 巡检进程, 生成巡检报告(可自定义数量, 默认4个)

manager_instance: 负责各进程间通信(1个)

work_relation: 识别各节点关系的进程(限制1个)



备注:manager共享函数

task_queue: 把要巡检的主机信息放入这个队列, work进程就来获取信息并巡检

inspection: 巡检期间进程间的通信

queue_relation: 要分析节点间关系的task(等task完成之后才会开始)



# WEB端接口

## 开始巡检

接口地址: inspection_web

接口方法: POST

接口例子. F12自己查看



## 查看状态

接口地址:inspection_status

接口方法: POST

例子:  curl  -X POST  192.168.101.21:80/inspection_status



## 下载巡检报告

接口地址:download

接口方法: get

例子:curl -X GET http://192.168.101.21/download?file_name=task_20220907_095527_127.0.0.1_3308_1662515758.html\&file_type=html



# BUG修复记录

2022.08.29   当host为空的时候, 抛出异常. (已修复, 加了个默认值)

2022.09.07   [主机信息巡检完成后无反应](https://github.com/ddcw/inspection/issues)



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
| 2022.09.07 | v2.2  | 1. 细化巡检项(只有47项了)<br />2. 新增word巡检报告<br />3. 支持多个服务器共同巡检一个task(貌似用处不大)<br />4. 支持节点关系分析<br />5. 支持shell采集数据然后生成巡检报告<br />6. 新增了巡检建议功能<br />7. 优化了界面, 现在看起来更酷了<br />8. 移除了在线调整并发度功能 |
| 2024.03.19 | v2.3  | 1. 修复tmp目录不会自动创建<br />2. 可为空的字段太多会导致docx生成太慢. 现在只取20个<br />3. running状态转为字符串(不然无法格式化为json.  issue 8)<br />4. work_inspection增加更多提示词, 不然不知道到哪一步了...<br />5. node_relation 默认值设置为False (issue 6)<br />6. 美化了建议部分(虽然还是没有加上参数名) issue 3<br /> |

