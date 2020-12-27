import functools

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
    jsonify
)
from models.front_models import (
    user_register_model,
    user_login_model,
    add_visits,
    get_user
)

bp = Blueprint('user_login_register', __name__, url_prefix='/user_login_register')


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
        error = user_register_model(username, password, password_again)
        if error is None:
            return redirect(url_for('user_login_register.login'))
        flash(error)
        redirect(url_for('user_login_register.register'))
    return render_template('front/user_login_register/register.html')


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
        user, error = user_login_model(username, password)
        if error is None:
            # 登录成功
            session.clear()
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            # 访问量加1
            add_visits(user_id=user['id'])
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
            return redirect(url_for('user_login_register.login'))
    # get请求加载渲染login页面,传跳转过来的url链接
    return render_template('front/user_login_register/login.html', next=request.referrer)


@bp.route('/index_login', methods=('POST',))
def index_login():
    username = request.form.get('username')
    password = request.form.get('password')
    user, error = user_login_model(username, password)
    if error is None:
        session.clear()
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        # 访问量加1
        add_visits(user_id=user['id'])
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
        g.user = get_user(user_id)


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
            return redirect(url_for('user_login_register.login'))
        return view(**kwargs)

    return wrapped_view
