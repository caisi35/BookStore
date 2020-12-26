import functools
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

bp = Blueprint('signIn', __name__, url_prefix='/admin')


@bp.route('/admin_login', methods=('GET', 'POST'))
def admin_login():
    try:
        if request.method == 'POST':
            email = request.form.get('email', '')
            password = request.form.get('password', '')
            error, admin = admin_login_model(email, password)

            if error is None and password == admin['password'] and int(admin['sign_count']) < 5:
                # 登录成功，清除登陆次数，注册session，重定向到管理主页
                clear_user_count(admin)
                session.clear()
                session['admin_id'] = admin['id']
                session['admin_email'] = admin['email']
                return redirect(url_for('admin.admin'))
            else:
                # 登录失败，快闪显示错误，重定向回原页面
                flash(error)
                return redirect(url_for('signIn.admin_login'))
        # GET 请求
        return render_template('admin/signin.html')
    except Exception as e:
        print('===============admin_login===============', e)
        return abort(404)


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


