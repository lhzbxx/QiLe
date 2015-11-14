# -*- coding: utf-8 -*-
# 
from qiniu import Auth

def main():
	q = Auth('FCFQs6B-thjgt30-HEmCS9ZUCGQBxx2Zsg_WO1k5', 'Z8LCTm4gxo_dfX7HT0EhFnXmsFTGwZ8MyCFXmSXF')

	# 上传策略仅指定空间名和上传后的文件名，其他参数仅为默认值
	token = q.upload_token('qile')
	f = open('qiniu_auth_token.txt', 'w')
	f.write(str(token))

	# 上传策略除空间名和上传后的文件名外，指定上传凭证有效期为7200s
	# callcakurl为"http://callback.do"，
	# callbackBody为原始文件名和文件Etag值

if __name__ == '__main__':
	main()