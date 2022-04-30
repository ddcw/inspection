def return_index():
	return '''
<!DOCTYPE html>
<html>
<head lang="en">
	<meta charset="UTF-8">
	<title>DDCW_INSPECTION</title>
	<style type="text/css">
		.leftnav{
			height: 100%;
			width: 200px;
			position: fixed;
			z-index: 1;
			top: 0;
			left: 0;
			background-color: #111;
			overflow-x: hidden;
			padding-top: 20px;
		}
		.leftnav button {
			background-color: #111;
			width: 200px;
			border:0;
		}
		.leftnav a {
			padding: 6px 8px 6px 16px;
			text-decoration: none;
			font-size: 25px;
			color: #818181;
			display: block;
		}

		.leftnav a:hover {
			color: #f1f1f1;
		}
		.main {
			margin-left: 200px; /* 与leftnav的宽度相同 */
			//font-size: 28px; /* 字体放大，让页面可滚动 */
			padding: 0px 10px;
		}
		@media screen and (max-height: 450px) {
			.sidenav {padding-top: 15px;}
			.sidenav a {font-size: 18px;}
		}
		tr:hover   {background-color: yellow;}
	</style>
	<script>
	function get_json_len(jsdata){
		var jssize = 0;
		for (var i in jsdata){
			jssize += 1;
		}
		return jssize;
	}


	function click_running_complate(stat){
		urls = location.protocol + "//" + location.hostname + ":" + location.port + "/status"
		if (stat=="running"){
			formdata = new FormData();
			formdata.append("running_status","True");
			let xhr = new XMLHttpRequest();
			xhr.open('POST', urls, true);
			xhr.onreadystatechange = function () {
				if (this.readyState == 4 && this.status == 200) {
					rsp_text = JSON.parse(xhr.responseText)
					//alert(Object.keys(rsp_text["running_status"]["data"]))
					//alert(xhr.responseText)
					// 拼接html
					document.getElementById("brunning").innerHTML = '<a href="#running">进行中 ('+get_json_len(rsp_text["running_status"]["data"])+')</a>' 
					running_html = '<table border="0" width="75%" style="border_collapse: collapse;" >'
					running_html += '<tr><th style="font:bold 8pt Arial,Helvetica,Geneva,sans-serif; color:White; background:#0066CC;padding-left:4px; padding-right:4px;padding-bottom:2px">任务名</th><th style="font:bold 8pt Arial,Helvetica,Geneva,sans-serif; color:White; background:#0066CC;padding-left:4px; padding-right:4px;padding-bottom:2px">主机</th><th style="font:bold 8pt Arial,Helvetica,Geneva,sans-serif; color:White; background:#0066CC;padding-left:4px; padding-right:4px;padding-bottom:2px">端口</th><th style="font:bold 8pt Arial,Helvetica,Geneva,sans-serif; color:White; background:#0066CC;padding-left:4px; padding-right:4px;padding-bottom:2px">用户</th><th style="font:bold 8pt Arial,Helvetica,Geneva,sans-serif; color:White; background:#0066CC;padding-left:4px; padding-right:4px;padding-bottom:2px">巡检MYSQL</th><th style="font:bold 8pt Arial,Helvetica,Geneva,sans-serif; color:White; background:#0066CC;padding-left:4px; padding-right:4px;padding-bottom:2px">巡检主机</th><th style="font:bold 8pt Arial,Helvetica,Geneva,sans-serif; color:White; background:#0066CC;padding-left:4px; padding-right:4px;padding-bottom:2px">状态</th></tr>'
					running_data = ""
					if (rsp_text["running_status"]["havedata"] == "true"){
						for (var task in rsp_text["running_status"]["data"]){
							running_data += "<tr>" + "<td>" + task + "</td>"  + "<td>" + rsp_text["running_status"]["data"][task]["host"] + "</td>"  +  "<td>" + rsp_text["running_status"]["data"][task]["port"] + "</td>" + "<td>" + rsp_text["running_status"]["data"][task]["user"] + "</td>"  + "<td>" + rsp_text["running_status"]["data"][task]["mysql"] + "</td>"  + "<td>" + rsp_text["running_status"]["data"][task]["ssh"] + "</td>"  + "<td>" + rsp_text["running_status"]["data"][task]["status"] + "</td>"  + "</tr>"
						}
					}
					running_html += running_data + "</table>"
					document.getElementById(stat).innerHTML = running_html
				}
			}
			xhr.send(formdata)
		}

		if (stat=="complete"){
			formdata = new FormData();
			formdata.append("complate_status","True");
			let xhr = new XMLHttpRequest();
			xhr.open('POST', urls, true);
			xhr.onreadystatechange = function () {
				if (this.readyState == 4 && this.status == 200) {
					rsp_text = JSON.parse(xhr.responseText)
					//alert(xhr.responseText)
					document.getElementById("bcomplete").innerHTML = '<a href="#complete">已完成 ('+get_json_len(rsp_text["complate_status"]["data"])+')</a>' 
					running_html = '<table border="0" width="100%" style="border_collapse: collapse;" >'
					running_html += '<tr><th style="font:bold 8pt Arial,Helvetica,Geneva,sans-serif; color:White; background:#0066CC;padding-left:4px; padding-right:4px;padding-bottom:2px">任务名</th><th style="font:bold 8pt Arial,Helvetica,Geneva,sans-serif; color:White; background:#0066CC;padding-left:4px; padding-right:4px;padding-bottom:2px">主机</th><th style="font:bold 8pt Arial,Helvetica,Geneva,sans-serif; color:White; background:#0066CC;padding-left:4px; padding-right:4px;padding-bottom:2px">端口</th><th style="font:bold 8pt Arial,Helvetica,Geneva,sans-serif; color:White; background:#0066CC;padding-left:4px; padding-right:4px;padding-bottom:2px">用户</th><th style="font:bold 8pt Arial,Helvetica,Geneva,sans-serif; color:White; background:#0066CC;padding-left:4px; padding-right:4px;padding-bottom:2px">巡检MYSQL</th><th style="font:bold 8pt Arial,Helvetica,Geneva,sans-serif; color:White; background:#0066CC;padding-left:4px; padding-right:4px;padding-bottom:2px">巡检主机</th><th style="font:bold 8pt Arial,Helvetica,Geneva,sans-serif; color:White; background:#0066CC;padding-left:4px; padding-right:4px;padding-bottom:2px">文件名</th><th style="font:bold 8pt Arial,Helvetica,Geneva,sans-serif; color:White; background:#0066CC;padding-left:4px; padding-right:4px;padding-bottom:2px">操作</th></tr>'
					running_data = ""
					if (rsp_text["complate_status"]["havedata"] == "true"){
						for (var task in rsp_text["complate_status"]["data"]){
							running_data = "<tr>" + "<td>" + task + "</td>"  + "<td>" + rsp_text["complate_status"]["data"][task]["host"] + "</td>"  +  "<td>" + rsp_text["complate_status"]["data"][task]["port"] + "</td>" + "<td>" + rsp_text["complate_status"]["data"][task]["user"] + "</td>"  + "<td>" + rsp_text["complate_status"]["data"][task]["mysql"] + "</td>"  + "<td>" + rsp_text["complate_status"]["data"][task]["ssh"] + "</td>" + "<td>" + rsp_text["complate_status"]["data"][task]["status"] + "</td>"  + "<td>" + '<a href="/view/' + rsp_text["complate_status"]["data"][task]["status"]+'"  target="_blank"> 预览</a>' + ' &nbsp | &nbsp <a href="/download?file_name=' + rsp_text["complate_status"]["data"][task]["status"] + '&file_type=html' +'">下载HTML</a>' + '<a href="/download?file_name=' + rsp_text["complate_status"]["data"][task]["status"] + '&file_type=pdf' +'" style="display:none">下载PDF</a>' +  "</td>"  + "</tr>" + running_data // 把最新的放在最上面...
						}
					}
					running_html += running_data + "</table>"
					document.getElementById(stat).innerHTML = running_html
				}
			}
			xhr.send(formdata)

		}
	}


	function showe(e){
		var be="b"+e
		document.getElementById("new_inspection").style.display="none"
		document.getElementById("analyze_inspection").style.display="none"
		document.getElementById("running").style.display="none"
		document.getElementById("complete").style.display="none"
		document.getElementById("multi_inspection").style.display="none"
		
		document.getElementById("bnew_inspection").style.backgroundColor="#111"
		document.getElementById("banalyze_inspection").style.backgroundColor="#111"
		document.getElementById("brunning").style.backgroundColor="#111"
		document.getElementById("bcomplete").style.backgroundColor="#111"
		document.getElementById("bmulti_inspection").style.backgroundColor="#111"

		document.getElementById(e).style.display=""
		document.getElementById(be).style.backgroundColor="#0000FF"

		click_running_complate(e)


	};


	function test_conn(aa){
		formdata = new FormData(document.getElementById("xunjian"))
		if (aa == "only_test"){formdata.append("only_test","True")}
		else {formdata.append("only_test","False"); document.getElementById("ksxj").value="正在巡检";document.getElementById("ksxj").style.backgroundColor="#FFFF00";}
		//for (var [a,b] of formdata.entries()){alert(a);alert(b)}
		urls = location.protocol + "//" + location.hostname + ":" + location.port + "/inspection"
		//alert(urls)
		let xhr = new XMLHttpRequest()
		xhr.open('POST', urls, true);
		xhr.onreadystatechange = function () {
			 if (this.readyState == 4 && this.status == 200) {
				rsp_text = JSON.parse(xhr.responseText)
				if(rsp_text["type"] != "test"){
					document.getElementById("ksxj").value="开始巡检";document.getElementById("ksxj").style.backgroundColor="#FF0000";
					if(rsp_text["type"] == "false"){alert(rsp_text["data"])}
					click_running_complate("complete")
					click_running_complate("running")
					// alert(rsp_text["data"])  // 弹窗太烦了, 就关掉了....
					//document.getElementById("bcomplete").style.fontcolor="#FF0000"
				}
				else if(rsp_text["type"] == "test"){
					if(rsp_text["data"]["mysql"] == true){
						alert("mysql连接成功")
					}
					else{
						alert("[ERROR] mysql连接失败")
					}
					if (rsp_text["data"]["ssh"] == true){
						alert("SHELL 可用")
					}
					else{
						alert("[ERROR] ssh连接失败")
					}
				}
			}
			else if (this.status != 200) {
				document.getElementById("ksxj").value="开始巡检";document.getElementById("ksxj").style.backgroundColor="#FF0000";
				alert("巡检脚本所在的服务器网络有问题.... 或者服务未启动, 或者端口不对.")
			}
		}
		xhr.send(formdata)
		setTimeout(function(){click_running_complate("running")},500)
		//click_running_complate("running")
		
	}

	function m_fun_ksxj(){
		alert("暂不支持.... 有空了再写")
	}


window.onload = function(){
open_tab = location.hash.split("#")[1]
if (typeof(open_tab) != "undefined"){
	showe(open_tab)
	click_running_complate("running")
	click_running_complate("complete")
}
}
console.log("最新下载地址: https://github.com/ddcw/inspection")
	</script>
</head>
<body>

<div class="leftnav">
	<button id="bnew_inspection" onclick="showe('new_inspection')" style="background-color:#0000FF"><a href="#new_inspection">新建巡检任务</a></button>
	<button id="bmulti_inspection" onclick="showe('multi_inspection')"><a href="#multi_inspection">批量巡检</a></button>
	<button id="banalyze_inspection" onclick="showe('analyze_inspection')"><a href="#analyze_inspection">生成巡检报告</a></button>
	<button id="brunning" onclick="showe('running')"><a href="#running">进行中</a></button>
	<button id="bcomplete" onclick="showe('complete')"><a href="#complete">已完成</a></button>
</div>



<!-- 内容 -->
<div class="main">
<div id="new_inspection" >
<form method = "post" id="xunjian" action = "/inspection">
<span>数据库服务器地址</span> <input id="host" type="text" name="host" value="127.0.0.1" /></br>
<span>数据库端口</span> <input id="port" type="number" name="port" value="3306" /></br>
<span>数据库用户名</span> <input id="user" type="text" name="user" value="root" /></br>
<span>数据库密码</span> <input id="password" type="password" name="password" value="123456" /></br>
<span>SSH端口</span> <input id="ssh_port" type="number" name="ssh_port" value="22" />
<span>SSH用户</span> <input id="ssh_user" type="text" name="ssh_user" value="root" />
<span>SSH密码</span> <input id="ssh_password" type="password" name="ssh_password" value="123456" />
</br>
</br><input type="button" onclick="test_conn('only_test')"  value="测试连接" style="background-color:#7CFC00;boder:0;height:30px;width:80px;"/>&nbsp;&nbsp;&nbsp;&nbsp;
<input id="ksxj" type="button" value="开始巡检" onclick="test_conn('not')" style="background-color:#FF0000;boder:0;height:30px;width:80px;" />
</form>
</div>


<div id="multi_inspection" style="display:none">
批量巡检
<form  method="post" action="/mf"  enctype="multipart/form-data">
	<input name="file" id="file" type="file">
	<input id="mksxj" type="submit" value="开始巡检" "></input>
</form>
</div>


<div id="analyze_inspection" style="display:none">
请上传采集的json文件
<form  method="post" action="/uploads"  enctype="multipart/form-data">
	<input name="file" type="file">
	<input type="submit" value="上传"></input>
</form>
</div>


<div id="running" style="display:none">
查看进行中
</div>

<div id="complete" style="display:none">
查看已完成
<a href="/view/test.html"  target="_blank"> 预览功能测试 点击跳转到test.html 方便测试</a>
</div>


</div>
</body>
</html>

'''
