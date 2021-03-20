import functools
import logging
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for
)
from werkzeug.exceptions import abort
from models import (
    admin_login_model,
    clear_user_count,
    admin_register,
)


bp = Blueprint('signIn', __name__, url_prefix='/admin')


@bp.route('/admin_login', methods=('GET', 'POST'))
def admin_login():
    """后台管理员登录"""
    if request.method == 'POST':
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        try:
            result = admin_login_model(email, password)
            error = result.get('error')
            admin = result.get('admin')
        except Exception as e:
            logging.exception('signIn admin_login admin_log_model [Exception]:%s', e)
            return abort(404)
        if admin and int(admin['sign_count']) <= 5:
            # 登录成功，清除登陆次数，注册session，重定向到管理主页
            try:
                clear_user_count(admin)
            except Exception as e:
                logging.exception('signIn admin_login clear_user_count [Exception]:%s', e)
                return abort(404)
            session.clear()
            session['admin_id'] = str(admin['_id'])
            session['admin_email'] = admin['email']
            session['auth'] = admin['auth']
            return redirect(url_for('admin.admin'))
        else:
            # 登录失败，快闪显示错误，重定向回原页面
            flash(error)
            return redirect(url_for('signIn.admin_login'))
    # GET method
    return render_template('admin/signin.html')


def register(email, password, auth_list):
    """管理员注册函数"""
    if len(password) < 8:
        return
    admin_id = admin_register(email, password, auth_list)
    return admin_id


@bp.route('/admin_logout')
def admin_logout():
    """退出登录"""
    session.clear()
    return redirect(url_for('signIn.admin_login'))


def admin_login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get('admin_id') is None:
            return redirect(url_for('signIn.admin_login'))
        return view(**kwargs)
    return wrapped_view


def admin_auth(auth_list=list, *args, **kwargs):
    """权限管理装饰器"""
    def admin_auth_m(func):
        @functools.wraps(func)
        def wrapped_view(*args, **kwargs):
            if session.get('admin_id') is None:
                return redirect(url_for('signIn.admin_login'))
            else:
                if not set(auth_list) & set(session.get('auth')):
                    flash('此菜单 [{}] 您没有权限访问！'.format(request.path))
                    return redirect(request.referrer)
            return func(*args, **kwargs)
        return wrapped_view
    return admin_auth_m


if __name__ == '__main__':
    register('admin@163.com', '12345678', ['order_admin', 'book_admin'])
