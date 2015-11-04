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
@app.route('/')
def index_page():
	return render_template("index.html")
@app.route('/search')
def search_page():
	return render_template("list.html")
@app.route('/detail')
def detail_page():
	return render_template("detail.html")
@app.route('/success')
def success_page():
	return render_template("success.html")
@app.route('/order')
def order_page():
	if session.get('user'):
		return render_template("order.html")
	else:
		return redirect(url_for('login_page'))
@app.route('/pay')
def pay_page():
	if session.get('user'):
		return render_template("pay.html")
	else:
		return redirect(url_for('login_page'))
@app.route('/login')
def login_page():
	session['user'] = "login"
	return render_template("login.html")
@app.route('/admin/api')
def admin_index_page():
	return render_template("admin/1.html")
#
#
#
#########

#########
#
# 后台函数
# 
#########
@app.route('/login-back')
def login():
	# 登录成功。
	return jsonify({"data": 100})
	# 用户名不存在。
	return jsonify({"data": 101})
	# 密码错误。
	return jsonify({"data": 102})
@app.route('/register-back')
def register():
	# 注册成功。
	return jsonify({"data": 100})
	# 用户名已存在。
	return jsonify({"data": 101})
	# 验证码错误。
	return jsonify({"data": 102})
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


if __name__ == '__main__':
	app.run(debug = True)
#
#
#
#########