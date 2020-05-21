import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import abort
from db import ToConn
import datetime

bp = Blueprint('signIn', __name__, url_prefix='/admin')


# 管理员登录
@bp.route('/admin_login', methods=('GET', 'POST'))
def admin_login():
    try:
        if request.method == 'POST':
            email = request.form.get('email', '')
            password = request.form.get('password', '')
            admin = ToConn().get_db('select * from admin where email=%s', (email,)).fetchone()
            error = None

            if admin:
                # 用户名正确

                # 获取时间差：今天日期-最近登录日期
                time_result = datetime.date.today() - admin['last_signIn_time']

                if time_result >= datetime.timedelta(days=1):
                    # 上次登录时间大于一天，更新登录次数为0，并且更新最近登录时间为今天
                    ToConn().to_db('update admin set sign_count=0,last_signIn_time=current_date() where id=%s',
                                   (admin['id'],)).commit()
                    if password != admin['password']:
                        # 密码错误,登录错误次数加1
                        ToConn().to_db('update admin set sign_count=sign_count+1 where id=%s', (admin['id'],)).commit()
                        error = '邮箱地址或密码错误！今日剩余 4 次'
                elif admin['sign_count'] >= 5:
                    # 上次登录时间小于一天, 登录次数已到5次
                    error = '今日登录错误次数超限'

                if password != admin['password'] and int(admin['sign_count']) < 5:
                    # 密码错误,登录错误次数加1，登录次数小于5还可以继续登录
                    ToConn().to_db('update admin set sign_count=sign_count+1 where id=%s', (admin['id'],)).commit()
                    sign_count = ToConn().get_db('select sign_count from admin where email=%s and id=%s',
                                                 (email, admin['id'])).fetchone()
                    # fetchone 查询结果为字典，需要解包
                    count = 5 - int(sign_count['sign_count'])
                    error = '邮箱地址或密码错误！今日剩余' + str(count) + '次'

                if not admin['is_effective']:
                    # 账户已失效(not 1, 1为有效，0为无效，默认1有效)
                    error = '账户已失效'

            else:
                # 用户名错误
                error = '邮箱地址或密码错误！'

            if error is None and password == admin['password'] and int(admin['sign_count']) < 5:
                # 登录成功，清除登陆次数，注册session，重定向到管理主页
                ToConn().to_db('update admin set sign_count=0,last_signIn_time=current_date() where id=%s',
                               (admin['id'],)).commit()
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


# 退出
@bp.route('/admin_logout')
def admin_logout():
    """
    注销用户登录信息
    :return:
    """
    session.clear()
    return redirect(url_for('signIn.admin_login'))


# 过滤视图，拦截非用户访问路由视图
def admin_login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get('admin_id') is None:
            return redirect(url_for('signIn.admin_login'))
        return view(**kwargs)

    return wrapped_view


