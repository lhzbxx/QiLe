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
from qiniu import Auth

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
	return render_template("index.html", signal = s)
# 搜索结果
@app.route('/search')
def search_page():
	s = signal()
	rooms = query_db('select * from rooms')
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
	return render_template("order_list.html", signal = s)
@app.route('/order_detail')
def order_detail_page():
	s = signal()
	return render_template("order_detail.html", signal = s)
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
@app.route('/result/<sign>/<title>/<content>')
def result_page(sign, title, content):
	return render_template("result.html", sign = sign, title = title, content = content)
# 下单页面
@app.route('/order/<id>')
def order_page(id):
	s = signal()
	user = query_db('select * from users where uuid = ?', [s.login], one=True)
	room = query_db('select * from rooms where uuid = ?', [id], one=True)
	checkins = query_db('select * from user_checkin where user_uuid = ?', [s.login])
	coupons = query_db('select * from coupons where phone_number = ?', [user['phone_number']])
	for coupon in coupons:
		coupon['limit_time'] = time.strftime("%Y-%m-%d", time.localtime(coupon['limit_time'])) 
	return render_template("order.html", signal = s, room = room, user = user, checkins = checkins, coupons = coupons, current = int(time.time()))
# 支付页面
@app.route('/pay')
def pay_page():
	s = signal()
	return render_template("pay.html", signal = s)
# 登录页面
@app.route('/login')
def login_page():
	return render_template("login.html")
# 发放优惠券页面
@app.route('/distribute_coupon/<limit>/<discount>/<date>')
def distribute_coupon_shanghai_ver1_page(limit, discount, date):
	new_user_coupon = {'limit': limit, 'discount': discount, 'date': date}
	session['coupon'] = new_user_coupon
	return render_template("distribute_coupon.html")
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
	return render_template("admin/1.html")
@app.route('/admin/test')
def admin_test_page():
	return render_template("admin/1-test.html")
# 订单列表
@app.route('/admin/order_list')
def admin_order_list_page():
	orders = query_db('select * from orders')
	return render_template("admin/2.1.html", orders = orders)
# 商家列表
@app.route('/admin/merchant_list')
def admin_merchant_list_page():
	merchants = query_db('select * from merchants')
	return render_template("admin/3.1.html", merchants = merchants)
# 添加商家
@app.route('/admin/add_merchant')
def admin_add_merchant_page():
	return render_template("admin/3.2.html")
# 修改商家
@app.route('/admin/modify_merchant/<id>')
def admin_modify_merchant_page(id):
	if len(id) != 36:
		return redirect(url_for('admin_add_merchant_page'))
	merchant = query_db('select * from merchants where uuid = ?', [id], one=True)
	return render_template("admin/3.2_m.html", merchant = merchant)
# 房源列表
@app.route('/admin/room_list')
def admin_room_list_page():
	rooms = query_db('select * from rooms')
	return render_template("admin/3.3.html", rooms = rooms)
# 添加房源
@app.route('/admin/add_room')
def admin_add_room_page():
	q = Auth('FCFQs6B-thjgt30-HEmCS9ZUCGQBxx2Zsg_WO1k5', 'Z8LCTm4gxo_dfX7HT0EhFnXmsFTGwZ8MyCFXmSXF')
	# 上传策略仅指定空间名和上传后的文件名，其他参数仅为默认值
	auth = q.upload_token('qile')
	merchants = query_db('select * from merchants')
	return render_template("admin/3.4.html", merchants = merchants, auth = auth)
# 修改房源
@app.route('/admin/modify_room/<id>')
def admin_modify_room_page(id):
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
	return render_template("admin/admin_layout.html")
# 优惠券模板列表
@app.route('/admin/coupon_template_list')
def admin_coupon_template_list_page():
	coupon_template = query_db('select * from coupon_template')
	return render_template("admin/4.3.html", coupon_template = coupon_template)
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
	send_coupon(u'新人券', t1, 100, 40, int(time.time())+2592000, u'上海地区', 2)
	send_coupon(u'红包券', t1, 100, 10, int(time.time())+604800, u'上海地区', 1)
	send_coupon(u'红包券', t1, 100, 10, int(time.time())+604800, u'上海地区', 1)
	send_coupon(u'红包券', t1, 100, 10, int(time.time())+604800, u'上海地区', 1)
	send_coupon(u'红包券', t1, 100, 10, int(time.time())+604800, u'上海地区', 1)
	# 成功后送优惠券
	session['user'] = u
	return jsonify({"data": 100})
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
	params = urllib.urlencode({'smsMob': request.form.get("t1"), 'Uid': 'dingfanla', 'Key': '19c35d39ee379898d25e', 'smsText': '验证码：' + str(vcode)})
	url = 'http://utf8.sms.webchinese.cn/?' + params
	req = urllib2.Request(url)
	print urllib2.urlopen(req).read()
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
		g.db.execute('insert into rooms (uuid, room_name, room_price, room_remark1, room_type, merchant_uuid, room_description, room_address, register_time, room_img_url) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
			[u, t1, t2, t3, t4, t5, t6, t7, int(time.time()), img[0]])
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
	img = request.form.get('img')
	if not img:
		# 缺少图片
		return jsonify({"data": 102})
	try:
		g.db.execute('update rooms set room_name = ?, room_price = ?, room_remark1 = ?, room_type = ?, merchant_uuid = ?, room_description = ?, room_address = ?, room_img_url = ?) values (?, ?, ?, ?, ?, ?, ?, ?)', 
			[t1, t2, t3, t4, t5, t6, t7, img[0]])
		g.db.commit()
	except Exception, e:
		# 插入数据失败
		return jsonify({"data": 101})
	# 修改成功。
	return jsonify({"data": 100})
# 更新真实姓名
@app.route('/add_true_name-back', methods=['POST'])
def add_true_name():
	t1 = request.form.get("t1")
	g.db.execute('update users set true_name = ? where uuid = ?', [t1, session['user']])
	g.db.commit()
	return jsonify({"data": 100})
# 添加入住人
@app.route('/add_checkin-back', methods=['POST'])
def add_checkin():
	t1 = request.form.get("t1")
	t2 = request.form.get("t2")
	t3 = request.form.get("t3")
	uu = str(uuid.uuid4())
	g.db.execute('insert into user_checkin (uuid, user_uuid, name, type, identify) values (?, ?, ?, ?, ?)', [uu, session['user'], t1, t2, t3])
	g.db.commit()
	return jsonify({"data": 100, 'uuid': uu})
# 移除入住人
@app.route('/remove_checkin-back', methods=['POST'])
def remove_checkin():
	t1 = request.form.get("t1")
	g.db.execute('delete from user_checkin where uuid = ?', [t1])
	g.db.commit()
	return jsonify({"data": 100})
# 发放优惠券
@app.route('/distribute_coupon-back', methods=['POST'])
def distribute_coupon():
	t1 = request.form.get("t1")
	p = query_db('select * from coupons where phone_number = ? and coupon_name = ?', [t1, u'新人券'], one=True)
	if p is None:
		a = session['coupon']
		send_coupon(u'新人券', t1, a['limit'], a['discount'], int(time.time())+int(a['date']), u'上海地区', 1)
		return jsonify({"data": 100})
	else:
		return jsonify({"data": 101})
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
def signal():
	if session.get('user'):
		# print session['user']
		signal.login = session['user']
	else:
		signal.login = None
	return signal
# 发放优惠券
# 参数分别是：名称，手机号，限额，折扣，截止时间，备注（例如地区）和颜色。
def send_coupon(name, phone_number, limit, discount, date, remark, color=1):
	uu = str(uuid.uuid4())
	g.db.execute('insert into coupons (uuid, coupon_name, phone_number, coupon_limit, coupon_discount, create_time, limit_time, coupon_remark, coupon_color) values (?, ?, ?, ?, ?, ?, ?, ?, ?)', 
		[uu, name, phone_number, limit, discount, int(time.time()), date, remark, color])
	g.db.commit()
# 使用优惠券
def use_coupon(uuid):
	g.db.execute('update coupons set coupon_state = 1 where uuid = ?', [uuid])
	g.db.commit()

if __name__ == '__main__':
	app.run(debug = True)
#
#
#
#########