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

app = Flask(__name__)
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
	return render_template("list.html", signal = s)
# 订单详情
@app.route('/detail')
def detail_page():
	s = signal()
	return render_template("detail.html", signal = s)
# 优惠券列表
@app.route('/coupon_list')
def coupon_list_page():
	s = signal()
	return render_template("coupon_list.html", signal = s)
# 订单中心
@app.route('/order_list')
def order_list_page():
	s = signal()
	return render_template("order_list.html", signal = s)
# 个人设置
@app.route('/user_setting')
def user_setting_page():
	s = signal()
	return render_template("user_setting.html", signal = s)
# 操作成功
@app.route('/success')
def success_page():
	return render_template("success.html")
# 下单页面
@app.route('/order')
def order_page():
	return render_template("order.html")
# 支付页面
@app.route('/pay')
def pay_page():
	return redirect(url_for('pay_page'))
# 登录页面
@app.route('/login')
def login_page():
	return render_template("login.html")

#########
#
# 管理页面
# 
#########
@app.route('/admin')
def admin_index_page():
	return render_template("admin/1.html")
@app.route('/admin/test')
def admin_test_page():
	return render_template("admin/1-test.html")
@app.route('/admin/order_list')
def admin_order_list_page():
	return render_template("admin/2.1.html")
@app.route('/admin/layout')
def admin_layout_page():
	return render_template("admin/admin_layout.html")
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
	session.clear()
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
	if session.get('vcode') or int(t3) != session['vcode']:
		# 验证码错误。
		return jsonify({"data": 102})
	user = query_db('select * from users where user_name = ?', [t1], one=True)
	if user is not None:
		# 用户名已存在。
		return jsonify({"data": 101})
	g.db.execute('insert into users (uuid, user_name, user_passwd, phone_number, register_time) values (?, ?, ?, ?, ?)', [str(uuid.uuid4()), t1, t2, t1, int(time.time())])
	g.db.commit()
	# 注册成功。
	session['user'] = 'login'
	return jsonify({"data": 100})
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
#
#
#
#########

#########
#
# 基础组件&函数
# 
#########
app.config.update(dict(
	DATABASE=os.path.join(app.root_path, 'db/main.db'),
	DEBUG=True,
	# 生成秘钥
	SECRET_KEY=os.urandom(24),
	USERNAME='admin',
	PASSWORD='default'
))
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
	return signal

if __name__ == '__main__':
	app.run(debug = True)
#
#
#
#########