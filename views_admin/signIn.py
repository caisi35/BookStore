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
)
from utils import Logger

Logger('signIn.log')

bp = Blueprint('signIn', __name__, url_prefix='/admin')


@bp.route('/admin_login', methods=('GET', 'POST'))
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        try:
            error, admin = admin_login_model(email, password)
        except Exception as e:
            logging.exception('signIn admin_login admin_log_model [Exception]:%s', e)
            return abort(404)
        if error is None and password == admin['password'] and int(admin['sign_count']) < 5:
            # 登录成功，清除登陆次数，注册session，重定向到管理主页
            try:
                clear_user_count(admin)
            except Exception as e:
                logging.exception('signIn admin_login clear_user_count [Exception]:%s', e)
                return abort(404)
            session.clear()
            session['admin_id'] = admin['id']
            session['admin_email'] = admin['email']
            return redirect(url_for('admin.admin'))
        else:
            # 登录失败，快闪显示错误，重定向回原页面
            flash(error)
            return redirect(url_for('signIn.admin_login'))
    # GET method
    return render_template('admin/signin.html')


@bp.route('/admin_logout')
def admin_logout():
    session.clear()
    return redirect(url_for('signIn.admin_login'))


def admin_login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get('admin_id') is None:
            return redirect(url_for('signIn.admin_login'))
        return view(**kwargs)
    return wrapped_view


