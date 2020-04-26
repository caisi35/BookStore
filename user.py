import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from db import ToConn

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
        db = ToConn()
        error = None
        if not username:
            error = 'Username or Password is Required'
        elif not password:
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


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """
    渲染登录页面，以及校验登录信息
    :return:
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
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
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            return redirect(url_for('index'))
        flash(error)
    return render_template('user/login.html')


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

