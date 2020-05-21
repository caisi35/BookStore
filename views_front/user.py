import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash
from models.db import ToConn

bp = Blueprint('user', __name__, url_prefix='/user')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    渲染用户注册页面，处理用户注册信息
    :return:
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_again = request.form['password_again']
        db = ToConn()
        error = None
        if not username:
            error = 'Username or Password is Required'
        elif not password:
            error = 'Username or Password is Required'
        elif password != password_again:
            error = 'Username or Password is Required'
        elif db.get_db(
                'select id from users where tel = %s', (username,)
        ).fetchone() is not None:
            error = 'User {} is Already Registered'.format(username)
        if error is None:
            db = ToConn()
            comm = db.to_db(
                'insert into users(tel,password) values (%s,%s)',
                (username, generate_password_hash(password))
            )
            comm.commit()
            comm.close()
            return redirect(url_for('user.login'))
        flash(error)
    return render_template('user/register.html')


@bp.route('/login', methods=('POST', 'GET'))
def login():
    """
    渲染登录页面，以及校验登录信息
    :return:
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # 获取跳转过来的next url链接，以重定向回去
        next = request.form['next']
        db = ToConn()
        error = None
        user = db.get_db(
            'select * from users where tel = %s', (username,)
        ).fetchone()
        if user is None:
            error = 'Incorrect username or password'
        elif username != str(user['tel']):
            error = 'Incorrect username or password'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect username or password'
        elif user['is_freezing']:
            error = 'The User Freezing, Please Contact Administrator'

        if error is None:
            # 登录成功
            session.clear()
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            if 'register' in next or next == 'None' or 'login' in next:
                # 如果是重注册页或者是直接从login链接过来的，重定向到主页去
                return redirect(url_for('products.index'))
            else:
                # 登录成功重定向回原页面
                return redirect(next)
        else:
            # 登录失败
            flash(error)
            print('error', '===================', next)
            return redirect(url_for('user.login'))
    # get请求加载渲染login页面,传跳转过来的url链接
    return render_template('user/login.html', next=request.referrer)


@bp.route('/index_login', methods=('POST',))
def index_login():
    username = request.form.get('username')
    password = request.form.get('password')
    db = ToConn()
    error = None
    user = db.get_db(
        'select * from users where tel = %s', (username,)
    ).fetchone()
    if user is None:
        error = 'Incorrect username or password'
    elif username != str(user['tel']):
        error = 'Incorrect username or password'
    elif not check_password_hash(user['password'], password):
        error = 'Incorrect username or password'
    elif user['is_freezing']:
        error = 'The User Freezing, Please Contact Administrator'

    if error is None:
        session.clear()
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        return jsonify(result='True')
    else:
        flash(error)
        return jsonify(result='False', error=error)


@bp.before_app_first_request
def load_logged_in_user():
    """
    注册用户session
    :return:
    """
    user_id = session.get('id')
    if user_id is None:
        g.user = None
    else:
        g.user = ToConn().get_db(' select * from users where id = %s ', (user_id,)).fetchone()


@bp.route('/logout')
def logout():
    """
    注销用户登录信息
    :return:
    """
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get('user_id') is None:
            return redirect(url_for('user.login'))
        return view(**kwargs)

    return wrapped_view
