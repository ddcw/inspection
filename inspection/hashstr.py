import hashlib
#返回一个hash之后str (加上固定常量)
def hash1(str1):
	#暂时先不加上端口变量, 也就是只修改端口之后密码也是这个
	return hashlib.sha256('{data}_ddcw'.format(data=str1).encode('utf-8')).hexdigest()
