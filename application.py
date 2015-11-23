# -*- coding: utf-8 -*-
# 
# RESTful-API
# 
# 

#########
#
# 模块导入&初始化
# 
#########
from flask import *
import sqlite3
import os
import time
import uuid
import urllib
import urllib2
import random
import requests
import md5
import string
from datetime import date, timedelta
from qiniu import Auth
import xml.etree.ElementTree as ET

#########
#
# 初始化
# 
#########
app = Flask(__name__)
app.config.update(dict(
	DATABASE=os.path.join(app.root_path, 'db/main.db'),
	DEBUG=True,
	# 生成秘钥
	SECRET_KEY=os.urandom(24),
	USERNAME='admin',
	PASSWORD='default'
))
#
#
#
#########

#########
#
# 0. 测试
# 
#########
@app.route('/test/api/hello')
def test_hello():
	r = {'status': 100, "msg": "Hello!"}
	return jsonify(r)
@app.route('/test/api/post', methods=['POST'])
def test_post():
	if not request.args:
		r = {'status': 200, "msg": "缺少参数"}
	else:
		r = {'status': 100, "msg": request.args.get('param', '')}
	return jsonify(r)
@app.route('/test/WorkWatcher/listen_work', methods=['POST'])
def WW_listen():
	return "success"
@app.route('/test/WorkWatcher/upload_image', methods=['GET', 'POST'])
def WW_upload():
    if request.method == 'POST':
        file = request.files['file']
        file.save(os.path.join("img", file.filename))
        return "success"

#
#
#
#########

#########
#
# 前端页面
# 
#########
# 首页
@app.route('/')
def index_page():
	s = signal()
	# user = query_db('select * from users where uuid = ?', [s.login], one=True)
	# if not user['open_id']:
	# 	return redirect('https://open.weixin.qq.com/connect/oauth2/authorize?appid=wxfee84b23a06c2b97&redirect_uri=https%3A%2F%2F' + debug + '&response_type=100&scope=snsapi_base#wechat_redirect')
	return render_template("index.html", signal = s)
# 搜索结果
@app.route('/search')
def search_page():
	s = signal()
	if session.get('t'):
		# print session['t']
		rooms = query_db('select * from rooms where room_switch = ?', [1])
		for j in range(len(rooms)-1, -1, -1):
			# 366位的库存信息
			p = int(rooms[j]['stock'])
			for i in range(session['t'][0]-1, session['t'][1]):
				if 1<<i & p == 0:
					del rooms[j]
					break
		return render_template("list.html", signal = s, rooms = rooms)
	else:
		rooms = query_db('select * from rooms where room_switch = ?', [1])
		return render_template("list.html", signal = s, rooms = rooms)
# 房源详情
@app.route('/detail/<id>')
def detail_page(id):
	s = signal()
	room = query_db('select * from rooms where uuid = ?', [id], one=True)
	photoes = query_db('select * from photoes where room_uuid = ?', [id])
	return render_template("detail.html", signal = s, room = room, photoes = photoes)
# 优惠券列表
@app.route('/coupon_list')
def coupon_list_page():
	s = signal()
	user = query_db('select * from users where uuid = ?', [s.login], one=True)
	coupons = query_db('select * from coupons where phone_number = ?', [user['phone_number']])
	for coupon in coupons:
		coupon['limit_time'] = time.strftime("%Y-%m-%d", time.localtime(coupon['limit_time'])) 
	return render_template("coupon_list.html", signal = s, coupons = coupons, current = int(time.time()))
# 订单中心
@app.route('/order_list')
def order_list_page():
	s = signal()
	if not s.login:
		return redirect(url_for('index_page'))
	orders = query_db('select * from orders where user_uuid = ?', [s.login])
	for i in orders:
		i['deal_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(i['deal_time']))
		room = query_db('select * from rooms where uuid = ?', [i['room_uuid']], one=True)
		i['deal_cost'] = room['room_img_url']
	return render_template("order_list.html", signal = s, orders = orders)
# 下单详细
@app.route('/order_detail/<id>')
def order_detail_page(id):
	s = signal()
	if not s.login:
		return redirect(url_for('index_page'))
	order = query_db('select * from orders where uuid = ?', [id], one=True)
	liver = eval(order['liver_info'])
	del liver[0]
	if order['coupon_uuid']:
		coupon = query_db('select * from coupons where uuid = ?', [order['coupon_uuid']], one=True)
		return render_template("order_detail.html", signal = s, order = order, liver = liver, coupon = coupon)
	return render_template("order_detail.html", signal = s, order = order, liver = liver)
# 个人设置
@app.route('/user_setting')
def user_setting_page():
	s = signal()
	return render_template("user_setting.html", signal = s)
# 操作成功
@app.route('/success')
def success_page():
	return render_template("success.html")
# 结果页面
@app.route('/result/<sign>/<title>/<content>/<remark>')
def result_page(sign, title, content, remark):
	return render_template("result.html", sign = sign, title = title, content = content, remark = remark)
# 下单页面
@app.route('/order/<id>')
def order_page(id):
	s = signal()
	if not s.login:
		return redirect(url_for('index_page'))
	user = query_db('select * from users where uuid = ?', [s.login], one=True)
	room = query_db('select * from rooms where uuid = ?', [id], one=True)
	checkins = query_db('select * from user_checkin where user_uuid = ?', [s.login])
	coupons = query_db('select * from coupons where phone_number = ?', [user['phone_number']])
	for coupon in coupons:
		coupon['limit_time'] = time.strftime("%Y-%m-%d", time.localtime(coupon['limit_time']))
	t = []
	if session.get('t'):
		p1 = session['t'][2].split('-')
		t1 = date(int(p1[0]), int(p1[1]), int(p1[2])).strftime("%Y-%m-%d")
		p2 = session['t'][3].split('-')
		t2 = date(int(p2[0]), int(p2[1]), int(p2[2])).strftime("%Y-%m-%d")
		t = [t1, t2, session['t'][0], session['t'][1]]
	else:
		# 临时的方案，这里还是需要改的，就是说如果直接进入了房源详情的页面。这里的时间先选择成今明两天。
		today = date.today().strftime('%Y-%m-%d')
		tomorrow = (date.today()+timedelta(days=1)).strftime('%Y-%m-%d')
		t1 = int(date.today().strftime('%j'))
		t2 = int(t1 + 1)
		t = [today, tomorrow, t1, t2]
		session['t'] = [t1, t2, today, tomorrow]
	return render_template("order.html", signal = s, room = room, user = user, checkins = checkins, coupons = coupons, current = int(time.time()), t = t)
# 支付页面
@app.route('/pay/<id>')
def pay_page(id):
	s = signal()
	# 如果没有登录，则返回首页。
	if not s.login:
		return redirect(url_for('index_page'))
	params = request.args.items()
	print ">>>pay_page all params: " + params.__str__()
	user = query_db('select * from users where uuid = ?', [s.login], one=True)
	# if not request.args.get('id'):
	# 	return redirect(url_for('index_page'))
	# id = request.args.get('id')
	openid = ''
	if not user['open_id']:
		c = request.args.get('code')
		print ">>>pay_page code get from weixin: " + str(c)
		openid = get_weixin_user_openid(c)
		g.db.execute('update users set open_id = ? where uuid = ?', [openid, s.login])
		g.db.commit()
	else:
		openid = user['open_id']
	print ">>>pay_page order uuid: " + str(id)
	print ">>>pay_page order openid: " + str(openid)
	# if not user['open_id']:
	# 	if request.args.get('code'):
	# 		id = request.args.get('state')
	# 		c = request.args.get('code')
	# 		openid = get_weixin_user_openid(c)
	# 		# g.db.execute('update users set open_id = ? where uuid = ?', [openid, s.login])
	# 		# g.db.commit()
	# 	else:
	# 		return redirect(get_weixin_user_code(id))
	order = query_db('select * from orders where uuid = ?', [id], one=True)
	if not order:
		return redirect(url_for('index_page'))
	order['liver_info'] = len(eval(order['liver_info']))-1
	rand_str = random_str(32)
	time_str = int(time.time())
	xml = """<xml>
			<appid>wxfee84b23a06c2b97</appid>
			<attach>支付测试</attach>
			<body>JSAPI支付测试</body>
			<mch_id>1271526501</mch_id>
			<nonce_str>""" + str(rand_str) + """</nonce_str>
			<notify_url>http://wxpay.weixin.qq.com/pub_v2/pay/notify.v2.php</notify_url>
			<openid>""" + str(openid) + """</openid>
			<out_trade_no>""" + str(id[:32]) + """</out_trade_no>
			<spbill_create_ip>""" + str(request.remote_addr) + """</spbill_create_ip>
			<total_fee>""" + str(order['deal_price']) + """</total_fee>
			<trade_type>JSAPI</trade_type>
			<sign>""" + sign_algorithm_one("appid=wxfee84b23a06c2b97&attach=支付测试&body=JSAPI支付测试&mch_id=1271526501&nonce_str="+str(rand_str)+
				"&notify_url=http://wxpay.weixin.qq.com/pub_v2/pay/notify.v2.php&openid="+str(openid)+"&out_trade_no="+str(id[:32])+"&spbill_create_ip="+
				str(request.remote_addr)+"&total_fee="+str(order['deal_price'])+"&trade_type=JSAPI") + """</sign>
			</xml>"""
	print ">>> pay_page xml: " + xml
	headers = {'Content-Type': 'application/xml'}
	r = requests.post('https://api.mch.weixin.qq.com/pay/unifiedorder', data=xml, headers=headers)
	r.encoding = 'utf-8'
	arr = xmlToArray(r.text)
	prepay_id = arr['prepay_id']
	print '>>>pay_page xml result: ' + r.text
	print '>>>pay_page prepay_id: ' + arr['prepay_id']
	sign = sign_algorithm_one("appid=wxfee84b23a06c2b97&nonceStr=" + rand_str + "&package=prepay_id=" + prepay_id + "&signType=MD5&timeStamp=" + str(time_str))
	sign = [time_str, rand_str, sign, prepay_id]
	return render_template("pay.html", signal = s, order = order, sign = sign)
def xmlToArray(xml):
	"""将xml转为array"""
	array_data = {}
	root = ET.fromstring(xml)
	for child in root:
		value = child.text
		array_data[child.tag] = value
	return array_data
# 登录页面
@app.route('/login')
def login_page():
	return render_template("login.html")
# 发放优惠券页面_弃用！！！
@app.route('/distribute_coupon/<limit>/<discount>/<date>')
def distribute_coupon_shanghai_ver1_page(limit, discount, date):
	new_user_coupon = {'limit': limit, 'discount': discount, 'date': date}
	session['coupon'] = new_user_coupon
	return render_template("distribute_coupon_abandon.html")
# 发放优惠券页面2（含有地区信息）
@app.route('/distribute_coupon_with_block/<id>/<block>')
def distribute_coupon_with_block_page(id, block):
	p = query_db('select * from coupon_template where uuid = ?', [id], one=True)
	if p is None:
		return redirect(url_for('index_page'))
	return render_template("distribute_coupon_with_block.html", template = p, block = block)
# 发放优惠券页面1（不含有地区信息）
@app.route('/distribute_coupon/<id>')
def distribute_coupon_page(id):
	p = query_db('select * from coupon_template where uuid = ?', [id], one=True)
	if p is None:
		return redirect(url_for('index_page'))
	return render_template("distribute_coupon.html", template = p)
# 重置密码页面
@app.route('/resetpwd')
def resetpwd_page():
	return render_template("resetpwd.html")
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

#########
#
# 管理页面
# 
#########
# 首页
@app.route('/admin')
def admin_index_page():
	s = admin_signal()
	if not s.login:
		return redirect(url_for('admin_login_page'))
	return render_template("admin/1.html")
@app.route('/admin/test')
def admin_test_page():
	return render_template("admin/1-test.html")
# login
@app.route('/admin/login')
def admin_login_page():
	return render_template("admin/login.html")
# 订单列表
@app.route('/admin/order_list')
def admin_order_list_page():
	s = admin_signal()
	if not s.login:
		return redirect(url_for('admin_login_page'))
	orders = query_db('select * from orders where deal_state == 1')
	for i in orders:
		i['deal_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(i['deal_time']))
	return render_template("admin/2.1.html", orders = orders)
# 待订单列表
@app.route('/admin/order_to_deal_list')
def admin_order_to_deal_list_page():
	s = admin_signal()
	if not s.login:
		return redirect(url_for('admin_login_page'))
	orders = query_db('select * from orders where deal_state != 1')
	for i in orders:
		i['deal_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(i['deal_time']))
	return render_template("admin/2.3.html", orders = orders)
# 商家列表
@app.route('/admin/merchant_list')
def admin_merchant_list_page():
	s = admin_signal()
	if not s.login:
		return redirect(url_for('admin_login_page'))
	merchants = query_db('select * from merchants')
	return render_template("admin/3.1.html", merchants = merchants)
# 添加商家
@app.route('/admin/add_merchant')
def admin_add_merchant_page():
	s = admin_signal()
	if not s.login:
		return redirect(url_for('admin_login_page'))
	return render_template("admin/3.2.html")
# 修改商家
@app.route('/admin/modify_merchant/<id>')
def admin_modify_merchant_page(id):
	s = admin_signal()
	if not s.login:
		return redirect(url_for('admin_login_page'))
	if len(id) != 36:
		return redirect(url_for('admin_add_merchant_page'))
	merchant = query_db('select * from merchants where uuid = ?', [id], one=True)
	return render_template("admin/3.2_m.html", merchant = merchant)
# 房源列表
@app.route('/admin/room_list')
def admin_room_list_page():
	s = admin_signal()
	if not s.login:
		return redirect(url_for('admin_login_page'))
	rooms = query_db('select * from rooms')
	return render_template("admin/3.3.html", rooms = rooms)
# 添加房源
@app.route('/admin/add_room')
def admin_add_room_page():
	s = admin_signal()
	if not s.login:
		return redirect(url_for('admin_login_page'))
	q = Auth('FCFQs6B-thjgt30-HEmCS9ZUCGQBxx2Zsg_WO1k5', 'Z8LCTm4gxo_dfX7HT0EhFnXmsFTGwZ8MyCFXmSXF')
	# 上传策略仅指定空间名和上传后的文件名，其他参数仅为默认值
	auth = q.upload_token('qile')
	merchants = query_db('select * from merchants')
	return render_template("admin/3.4.html", merchants = merchants, auth = auth)
# 修改房源
@app.route('/admin/modify_room/<id>')
def admin_modify_room_page(id):
	s = admin_signal()
	if not s.login:
		return redirect(url_for('admin_login_page'))
	if len(id) != 36:
		return redirect(url_for('admin_add_room_page'))
	q = Auth('FCFQs6B-thjgt30-HEmCS9ZUCGQBxx2Zsg_WO1k5', 'Z8LCTm4gxo_dfX7HT0EhFnXmsFTGwZ8MyCFXmSXF')
	# 上传策略仅指定空间名和上传后的文件名，其他参数仅为默认值
	auth = q.upload_token('qile')
	merchants = query_db('select * from merchants')
	room = query_db('select * from rooms where uuid = ?', [id], one=True)
	photoes = query_db('select * from photoes where room_uuid = ?', [id])
	return render_template("admin/3.4_m.html", merchants = merchants, auth = auth, room = room, photoes = photoes)
@app.route('/admin/layout')
def admin_layout_page():
	s = admin_signal()
	if not s.login:
		return redirect(url_for('admin_login_page'))
	return render_template("admin/admin_layout.html")
# 优惠券模板列表
@app.route('/admin/coupon_template_list')
def admin_coupon_template_list_page():
	s = admin_signal()
	if not s.login:
		return redirect(url_for('admin_login_page'))
	coupon_template = query_db('select * from coupon_template')
	return render_template("admin/4.3.html", coupon_template = coupon_template)
# 添加优惠券模板
@app.route('/admin/add_coupon_template')
def admin_add_coupon_template_page():
	s = admin_signal()
	if not s.login:
		return redirect(url_for('admin_login_page'))
	return render_template("admin/4.4.html")
#
#
#
#########

#########
#
# 后台函数
# 
#########
# 登录
@app.route('/login-back', methods=['POST'])
def login():
	t1 = request.form.get("t1")
	t2 = request.form.get("t2")
	user = query_db('select * from users where user_name = ?', [t1], one=True)
	if user is None:
		# 用户名不存在。
		return jsonify({"data": 101})
	else:
		if t2 != user['user_passwd']:
			# 密码错误。
			return jsonify({"data": 102})
		else:
			# 登录成功。
			session['user'] = user['uuid']
			return jsonify({"data": 100, "uuid": user['uuid']})
# 后台登录
@app.route('/admin_login-back', methods=['POST'])
def admin_login():
	session['admin_user'] = 'ahahah'
	return jsonify({"data": 100})
# 登出
@app.route('/logout-back', methods=['POST'])
def logout():
	session.pop('user', None)
	return jsonify({"data": 100})
# 检查是否登录
@app.route('/check-back', methods=['POST'])
def check():
	if session.get('user'):
		return jsonify({"data": 100})
	else:
		return jsonify({"data": 101})
# 注册
@app.route('/register-back', methods=['POST'])
def register():
	t1 = request.form.get("t1")
	t2 = request.form.get("t2")
	t3 = request.form.get("t3")
	if not session.get('vcode') or int(t3) != session['vcode']:
		# 验证码错误。
		return jsonify({"data": 102})
	user = query_db('select * from users where user_name = ?', [t1], one=True)
	if user is not None:
		# 用户名已存在。
		return jsonify({"data": 101})
	u = str(uuid.uuid4())
	g.db.execute('insert into users (uuid, user_name, user_passwd, phone_number, register_time) values (?, ?, ?, ?, ?)', [u, t1, t2, t1, int(time.time())])
	g.db.commit()
	# 注册成功。
	send_coupon(t1, 'init0')
	send_coupon(t1, 'init1')
	send_coupon(t1, 'init2')
	send_coupon(t1, 'init3')
	# 成功后送优惠券
	session['user'] = u
	return jsonify({"data": 100, "uuid": u})
# 修改密码
@app.route('/resetpwd-back', methods=['POST'])
def resetpwd():
	t1 = request.form.get("t1")
	t2 = request.form.get("t2")
	t3 = request.form.get("t3")
	if not session.get('vcode') or int(t3) != session['vcode']:
		# 验证码错误。
		return jsonify({"data": 102})
	user = query_db('select * from users where user_name = ?', [t1], one=True)
	if user is None:
		# 用户名不存在。
		return jsonify({"data": 101})
	g.db.execute('update users set user_passwd = ? where uuid = ?', [t2, user['uuid']])
	g.db.commit()
	# 修改成功。
	return jsonify({"data": 100})
# 发送验证码
@app.route('/sendVerifyCode-back', methods=['POST'])
def sendVerifyCode():
	vcode = random.randint(10000, 99999)
	session['vcode'] = vcode
	send_sms(request.form.get("t1"), '验证码：' + str(vcode))
	print vcode
	return jsonify({"data": 100})
# 添加商家
@app.route('/addMerchant-back', methods=['POST'])
def addMerchant():
	t1 = request.form.get("t1")
	t2 = request.form.get("t2")
	t3 = request.form.get("t3")
	t4 = request.form.get("t4")
	t5 = request.form.get("t5")
	t6 = request.form.get("t6")
	merchant = query_db('select * from merchants where merchant_username = ?', [t2], one=True)
	if merchant is not None:
		# 用户名已存在。
		return jsonify({"data": 101})
	u = str(uuid.uuid4())
	g.db.execute('insert into merchants (uuid, merchant_name, merchant_username, merchant_password, merchant_remark, merchant_phone_number1, merchant_description, register_time) values (?, ?, ?, ?, ?, ?, ?, ?)', [u, t1, t2, t3, t4, t5, t6, int(time.time())])
	g.db.commit()
	# 添加成功。
	return jsonify({"data": 100})
# 添加房源
@app.route('/addRoom-back', methods=['POST'])
def addRoom():
	t1 = request.form.get("t1")
	t2 = request.form.get("t2")
	t3 = request.form.get("t3")
	t4 = request.form.get("t4")
	t5 = request.form.get("t5")
	t6 = request.form.get("t6")
	t7 = request.form.get("t7")
	t8 = request.form.get("t8")
	img = request.form.getlist('img[]')
	# 生成房源的UUID
	u = str(uuid.uuid4())
	if not img:
		# 缺少图片
		return jsonify({"data": 102})
	for i in img:
		try:
			uu = str(uuid.uuid4())
			g.db.execute('insert into photoes (uuid, url, room_uuid) values (?, ?, ?)', [uu, i, u])
			g.db.commit()
		except Exception, e:
			# 插入数据失败
			return jsonify({"data": 101})
	try:
		g.db.execute('insert into rooms (uuid, room_name, room_price, room_remark1, room_type, merchant_uuid, room_description, room_address, register_time, room_cost, room_img_url) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
			[u, t1, t2, t3, t4, t5, t6, t7, t8, int(time.time()), img[0]])
		g.db.commit()
	except Exception, e:
		# 插入数据失败
		return jsonify({"data": 101})
	# 添加成功。
	return jsonify({"data": 100})
# 添加照片
@app.route('/addPhoto-back', methods=['POST'])
def addPhoto():
	t1 = request.form.get("t1")
	img = request.form.get('img')
	uu = str(uuid.uuid4())
	g.db.execute('insert into photoes (uuid, url, room_uuid) values (?, ?, ?)', [uu, img, t1])
	g.db.commit()
	return jsonify({"data": 100})
# 删除照片
@app.route('/deletePhoto-back', methods=['POST'])
def deletePhoto():
	t1 = request.form.get("t1")
	img = request.form.get('img')
	g.db.execute('delete from photoes where room_uuid = ? and url = ?', [t1, img])
	g.db.commit()
	return jsonify({"data": 100})
# 修改商家
@app.route('/modifyMerchant-back', methods=['POST'])
def modifyMerchant():
	t1 = request.form.get("t1")
	t2 = request.form.get("t2")
	t3 = request.form.get("t3")
	t4 = request.form.get("t4")
	t5 = request.form.get("t5")
	t6 = request.form.get("t6")
	t7 = request.form.get('t7')
	merchant = query_db('select * from merchants where merchant_username = ?', [t2], one=True)
	if merchant is None:
		# 商家不存在。
		return jsonify({"data": 101})
	g.db.execute('update merchants set merchant_name = ?, merchant_username = ?, merchant_password = ?, merchant_remark = ?, merchant_phone_number1 = ?, merchant_description = ? where uuid = ?', [t1, t2, t3, t4, t5, t6, t7])
	g.db.commit()
	# 修改成功。
	return jsonify({"data": 100})
# 修改房源
@app.route('/modifyRoom-back', methods=['POST'])
def modifyRoom():
	t1 = request.form.get("t1")
	t2 = request.form.get("t2")
	t3 = request.form.get("t3")
	t4 = request.form.get("t4")
	t5 = request.form.get("t5")
	t6 = request.form.get("t6")
	t7 = request.form.get("t7")
	t8 = request.form.get("t8")
	uu = request.form.get("uu")
	img = request.form.getlist('img[]')
	if not img:
		# 缺少图片
		return jsonify({"data": 102})
	try:
		g.db.execute('update rooms set room_name = ?, room_price = ?, room_remark1 = ?, room_type = ?, merchant_uuid = ?, room_description = ?, room_address = ?, room_cost = ?, room_img_url = ? where uuid = ?', 
			[t1, t2, t3, t4, t5, t6, t7, t8, img[0], uu])
		g.db.commit()
	except Exception, e:
		# 插入数据失败
		print e 
		return jsonify({"data": 101})
	# 修改成功。
	return jsonify({"data": 100})
# 更新真实姓名
@app.route('/add_true_name-back', methods=['POST'])
def add_true_name():
	s = signal()
	t1 = request.form.get("t1")
	g.db.execute('update users set true_name = ? where uuid = ?', [t1, s.login])
	g.db.commit()
	return jsonify({"data": 100})
# 添加入住人
@app.route('/add_checkin-back', methods=['POST'])
def add_checkin():
	s = signal()
	t1 = request.form.get("t1")
	t2 = request.form.get("t2")
	t3 = request.form.get("t3")
	uu = str(uuid.uuid4())
	g.db.execute('insert into user_checkin (uuid, user_uuid, name, type, identify) values (?, ?, ?, ?, ?)', [uu, s.login, t1, t2, t3])
	g.db.commit()
	return jsonify({"data": 100, 'uuid': uu})
# 移除入住人
@app.route('/remove_checkin-back', methods=['POST'])
def remove_checkin():
	t1 = request.form.get("t1")
	g.db.execute('delete from user_checkin where uuid = ?', [t1])
	g.db.commit()
	return jsonify({"data": 100})
# 移除商家
@app.route('/remove_merchant-back', methods=['POST'])
def admin_remove_merchant():
	id = request.form.get("t1")
	try:
		g.db.execute('delete from merchants where uuid = ?', [id])
		g.db.commit()
		return jsonify({"data": 100})
	except Exception, e:
		print e
		raise e
		return jsonify({"data": 101})
# 移除房源
@app.route('/remove_room-back', methods=['POST'])
def admin_remove_room():
	id = request.form.get("t1")
	try:
		g.db.execute('delete from rooms where uuid = ?', [id])
		g.db.commit()
		return jsonify({"data": 100})
	except Exception, e:
		print e
		raise e
		return jsonify({"data": 101})
# 添加优惠券模板
@app.route('/add_coupon_template-back', methods=['POST'])
def add_coupon_template():
	uu = str(uuid.uuid4())
	t1 = request.form.get("t1")
	t2 = request.form.get("t2")
	t3 = request.form.get("t3")
	t4 = request.form.get("t4")
	t5 = request.form.get("t5")
	t6 = request.form.get("t6")
	t7 = request.form.get("t7")
	try:
		g.db.execute('insert into coupon_template (uuid, coupon_name, coupon_discount, coupon_limit, limit_time, coupon_remark, coupon_stock, coupon_color, create_time) values (?, ?, ?, ?, ?, ?, ?, ?, ?)',
		 [uu, t1, t2, t3, t4, t5, t6, t7, int(time.time())])
		g.db.commit()
	except Exception, e:
		print e
		return jsonify({"data": 101})
	return jsonify({"data": 100})
# 删除优惠券模板
@app.route('/remove_coupon_template-back/<id>')
def remove_coupon_template(id):
	g.db.execute('delete from coupon_template where uuid = ?', [id])
	g.db.commit()
	return redirect(url_for('admin_coupon_template_list_page'))
# 发放优惠券（不含有地区信息）
@app.route('/distribute_coupon-back', methods=['POST'])
def distribute_coupon():
	t1 = request.form.get("t1")
	t2 = request.form.get("t2")
	p = query_db('select * from coupon_template where uuid = ?', [t2], one=True)
	# 检查该用户是否已经领取该优惠券。
	# p = query_db('select * from coupons where phone_number = ? and coupon_name = ?', [t1, u'新人券'], one=True)
	# if p is None:
	# 	a = session['coupon']
	# 	send_coupon(u'新人券', t1, a['limit'], a['discount'], int(time.time())+int(a['date']), u'上海地区', 1)
	# 	return jsonify({"data": 100})
	# else:
	# 	return jsonify({"data": 101})
	if send_coupon(t1, t2):
		return jsonify({"data": 100})
	else:
		return jsonify({"data": 101})
# 发放优惠券（含有地区信息）
@app.route('/distribute_coupon_with_block-back', methods=['POST'])
def distribute_coupon_with_block():
	t1 = request.form.get("t1")
	t2 = request.form.get("t2")
	t3 = request.form.get("t3")
	p = query_db('select * from coupon_template where uuid = ?', [t2], one=True)
	q = query_db('select * from coupon_block where block = ?', [t3], one=True)
	if q is None:
		g.db.execute('insert into coupon_block (block, coupon_uuid, create_time) values (?, ?, ?)', [t3, t2, int(time.time())])
	else:
		g.db.execute('update coupon_block set count = ? where coupon_uuid = ? and block = ?', [q['count']+1, t2, t3])
	g.db.commit()
	# 检查该用户是否已经领取该优惠券。
	if send_coupon(t1, t2):
		return jsonify({"data": 100})
	else:
		return jsonify({"data": 101})
def signal():
	if session.get('user'):
		# print session['user']
		signal.login = session['user']
	else:
		signal.login = None
	return signal
# 发放优惠券_弃用！！！
@app.route('/distribute_coupon_abandon-back', methods=['POST'])
def distribute_coupon_abandon():
	t1 = request.form.get("t1")
	p = query_db('select * from coupons where phone_number = ? and coupon_name = ?', [t1, u'新人券'], one=True)
	if p is None:
		a = session['coupon']
		send_coupon(u'新人券', t1, a['limit'], a['discount'], int(time.time())+int(a['date']), u'上海地区', 1)
		return jsonify({"data": 100})
	else:
		return jsonify({"data": 101})
# 搜索房源的参数处理
@app.route('/search-back', methods=['POST'])
def search():
	t1 = request.form.get("t1")
	t2 = request.form.get("t2")
	p = t1.split('-')
	t3 = int(date(int(p[0]), int(p[1]), int(p[2])).strftime('%j'))
	p = t2.split('-')
	t4 = int(date(int(p[0]), int(p[1]), int(p[2])).strftime('%j'))
	t = [t3, t4, t1, t2]
	session['t'] = t
	return jsonify({"data": 100})
# 支付的参数处理
@app.route('/pay-back', methods=['POST'])
def pay():
	s = signal()
	if not s.login:
		# 未登录
		return jsonify({"data": 101})
	room = request.form.get("room")
	coupon = request.form.get("coupon")
	t1 = request.form.get("t1")
	t2 = request.form.get("t2")
	true_name = request.form.get("true_name")
	room_name = request.form.get("room_name")
	# 检查优惠券是否可用。
	discount = 0
	limit = 0
	if coupon != '':
		c = query_db('select * from coupons where uuid = ?', [coupon], one=True)
		if c['coupon_state'] != 1 and c['limit_time'] < int(time.time()):
			# 如果优惠券已经不可用，或者已经超过期限。
			pass
		else:
			discount = c['coupon_discount']
			limit = c['coupon_discount']
	room = query_db('select * from rooms where uuid = ?', [room], one=True)
	if room is None:
		# 错误的房源。
		return jsonify({"data": 103})
	price = 0
	# 总价=天数*单价-折扣
	if not session.get('t'):
		return jsonify({"data": 104})
	total_day = session['t'][1] - session['t'][0] + 1
	price = room['room_price'] * (total_day)
	if price > int(limit):
		price = price - discount
		if price < 0:
			price = 0
	# 检查房间是否可用。
	# 未完成！！！
	if True == False:
		# 房源已不可用。
		return jsonify({"data": 102})
	u = str(uuid.uuid4())
	p = query_db('select * from user_checkin where user_uuid = ?', [s.login])
	liver = [len(p)]
	if len(p) != 0:
		for q in p:
			liver.append([q['name'], q['type'], q['identify']])
	liver = repr(liver)
	try:
		g.db.execute('insert into orders (uuid, user_uuid, room_uuid, date1, date2, deal_time, deal_price, deal_cost, liver_info, coupon_uuid, true_name, room_name) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
		 [u, s.login, room['uuid'], t1, t2, int(time.time()), price, room['room_cost'], liver, coupon, true_name, room_name])
		g.db.commit()
		user = query_db('select * from users where uuid = ?', [s.login], one=True)
		send_sms(user['phone_number'], "下了一个新订单，快付钱！")
		if not user['open_id']:
			return jsonify({'data': 105, 'url': get_weixin_user_code(u)})
		# thread.start_new_thread( check_order_valid, (u, ) )
	except Exception, e:
		print e
		raise e
	# 插入订单
	return jsonify({"data": 100, "id": u})
# 取消订单
@app.route('/cancel_order-back', methods=['POST'])
def cancel_order():
	t1 = request.form.get("t1")
	g.db.execute('update orders set deal_state = 5 where uuid = ?', [t1])
	g.db.commit()
	return jsonify({"data": 100})
# 删除订单
@app.route('/remove_order-back', methods=['POST'])
def remove_order():
	t1 = request.form.get("t1")
	g.db.execute('delete from orders where uuid = ?', [t1])
	g.db.commit()
	return jsonify({"data": 100})
# 房源的开关
@app.route('/change_room_state-back', methods=['POST'])
def change_room_state():
	t1 = request.form.get("t1")
	t2 = request.form.get("t2")
	if t2 == '0':
		g.db.execute('update rooms set room_switch = ? where uuid = ?', [1, t1])
		g.db.commit()
		return jsonify({"data": 100})
	if t2 == '1':
		g.db.execute('update rooms set room_switch = ? where uuid = ?', [0, t1])
		g.db.commit()
		return jsonify({"data": 100})
def signal():
	if session.get('user'):
		# print session['user']
		signal.login = session['user']
	elif request.cookies.get('username'):
		signal.login = request.cookies.get('username')
	else:
		signal.login = None
	return signal
def admin_signal():
	if session.get('admin_user'):
		# print session['user']
		signal.login = session['admin_user']
	else:
		signal.login = None
	return signal
# 送优惠券1
# 参数分别是：名称，手机号，限额，折扣，截止时间，备注（例如地区）和颜色。
def send_coupon(name, phone_number, limit, discount, date, remark, color=1):
	uu = str(uuid.uuid4())
	g.db.execute('insert into coupons (uuid, coupon_name, phone_number, coupon_limit, coupon_discount, create_time, limit_time, coupon_remark, coupon_color) values (?, ?, ?, ?, ?, ?, ?, ?, ?)', 
		[uu, name, phone_number, limit, discount, int(time.time()), date, remark, color])
	g.db.commit()
# 送优惠券2
# 参数是优惠券模板的UUID
def send_coupon(phone_number, id):
	p = query_db('select * from coupon_template where uuid = ?', [id], one=True)
	# 如果优惠券模板找不到，则直接返回。
	if p is None:
		return False
	u = query_db('select * from coupons where phone_number = ? and coupon_uuid = ?', [phone_number, id])
	if u is not None:
		return False
	g.db.execute('insert into coupons (uuid, coupon_uuid, coupon_name, phone_number, coupon_limit, coupon_discount, create_time, limit_time, coupon_remark, coupon_color) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
		[u, id, p['coupon_name'], phone_number, p['coupon_limit'], p['coupon_discount'], int(time.time()), p['limit_time']+int(time.time()), p['coupon_remark'], p['coupon_color']])
	g.db.execute('update coupon_template set coupon_stock = ? where uuid = ?', [p['coupon_stock']-1, id])
	g.db.commit()
	send_sms(phone_number, "亲，您的其乐账户中成功添加" + str(p['coupon_discount']) + "元红包噢，记得尽快使用哦！微信关注其乐，即享更多精彩活动！")
	return True
# 使用优惠券
def use_coupon(id):
	g.db.execute('update coupons set coupon_state = 1 where uuid = ?', [id])
	g.db.commit()
# 发送短信
def send_sms(phone_number, content):
	params = urllib.urlencode({'smsMob': phone_number, 'Uid': 'dingfanla', 'Key': '19c35d39ee379898d25e', 'smsText': content})
	url = 'http://utf8.sms.webchinese.cn/?' + params
	req = urllib2.Request(url)
	print ">>>send_sms: " + urllib2.urlopen(req).read()
# 获取用户的code（微信端）
def get_weixin_user_code(id):
	# debug = '127.0.0.1'
	param = urllib.urlencode({'id': id})
	debug = 'www.qilefun.com%2Fpay%3F' + param
	url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=wxfee84b23a06c2b97&redirect_uri=http%3A%2F%2Fwww.qilefun.com%2Fpay%2F' + id + '&response_type=code&scope=snsapi_base&state=' + id  + '#wechat_redirect'
	# url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx520c15f417810387&redirect_uri=https%3A%2F%2Fchong.qq.com%2Fphp%2Findex.php%3Fd%3D%26c%3DwxAdapter%26m%3DmobileDeal%26showwxpaytitle%3D1%26vb2ctag%3D4_2030_5_1194_60&response_type=code&scope=snsapi_base&state=123#wechat_redirect'
	print '>>>get first step code: ' + url
	return url
# 获取用户的openid（微信端）
def get_weixin_user_openid(code):
	url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid=wxfee84b23a06c2b97&secret=c5072c12cf5f7b0497750bc7739d7cac&code=' + str(code) + '&grant_type=authorization_code'
	req = urllib2.Request(url)
	t = urllib2.urlopen(req).read()
	print '>>>get second step open_id: ' + t
	t = eval(t)
	return t['openid']
#
#
#
#########

#########
#
# 基础组件&函数
# 
#########
def connect_db():
	return sqlite3.connect(app.config['DATABASE'])
@app.before_request
def before_request():
	g.db = connect_db()
@app.teardown_request
def teardown_request(exception):
	g.db.close()
# 简化sqlite3的查询方式。
def query_db(query, args=(), one=False):
	cur = g.db.execute(query, args)
	rv = [dict((cur.description[idx][0], value) for idx, value in enumerate(row)) for row in cur.fetchall()]
	return (rv[0] if rv else None) if one else rv
# 生成随机字符串
def random_str(randomlength=8):
    a = list(string.ascii_letters)
    random.shuffle(a)
    return ''.join(a[:randomlength])
# 生成微信所需要的签名
def sign_algorithm_one(param):
	m = md5.new()
	sign = param + "&key=ChenLiang2QiLeFun20151121ccccccc"
	m.update(sign)
	result = m.hexdigest().upper()
	print ">>>md5 sign: " + result
	return result
def sign_algorithm_multi(*params):
	m = md5.new()
	sign = ''
	for param in params:
		sign += '&' + param
	sign = sign + "&key=ChenLiang2QiLeFun20151121ccccccc"
	m.update(sign)
	return m.hexdigest().upper()
# class Scheduler(object):
# 	def __init__(self, sleep_time, function):
# 		self.sleep_time = sleep_time
# 		self.function = function
# 		self._t = None
# 	def start(self):
# 		if self._t is None:
# 			self._t = Timer(self.sleep_time, self._run)
# 			self._t.start()
# 		else:
# 			raise Exception("this timer is already running")
# 	def _run(self):
# 		self.function()
# 		self._t = Timer(self.sleep_time, self._run)
# 		self._t.start()
# 	def stop(self):
# 		if self._t is not None:
# 			self._t.cancel()
# 			self._t = None
# 检测订单是否超时。
def check_order_valid():
	orders = query_db('select * from orders where deal_state = ?', [0])
	for i in orders:
		if i['deal_time'] - int(time.time()) > 900:
			g.db.execute('update orders set deal_state = ? where uuid = ?', [4, i['uuid']])
			g.db.commit()
			user = query_db('select * from users where uuid = ?', [i['user_uuid']], one=True)
			send_sms(user['phone_number'], "抱歉，您的订单已经失效。")
# 	# print order_uuid
# 	# schedule.enter(900, 0, check_order_valid_func, (order_uuid,))  
# 	# schedule.run()
# 	print "OK"
# 	orders = query_db('select * from orders where deal_state = ?', [0])
# 	for i in orders:
# 		if i['deal_time'] - int(time.time()) > 10:
# 			g.db.execute('update orders set deal_state = ? where uuid = ?', [4, i['uuid']])
# 			g.db.commit()
# 			user = query_db('select * from users where uuid = ?', [i['user_uuid']], one=True)
# 			send_sms(user['phone_number'], "抱歉，您的订单已经失效。")
# @app.before_first_request
# def before_first_request():
# 	scheduler = Scheduler(3, check_order_valid)
# 	scheduler.start()

if __name__ == '__main__':
	app.run(debug = True)
#
#
#
#########