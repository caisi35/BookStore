import logging
from werkzeug.exceptions import abort

from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    url_for,
    redirect,
)

from models import (
    get_users_total,
    search_users,
    add_user_trach,
    delete_user_trach,
    restores_user_model,
    reset_user_pad,
    freezing_user_model,
    user_activate_model,
    get_admin_account,
    auth_admin_model,
    admin_search_model,
)
from views_admin.signIn import admin_auth
from utils import Logger

Logger('userAdmin.log')

bp = Blueprint('userAdmin', __name__, url_prefix='/admin/userAdmin')


@bp.route('/admin_search')
@admin_auth(['admin'])
def admin_search():
    page = request.args.get('page', 0, int)
    page_size = 20
    page_view = 5
    word = request.args.get('word', '')
    try:
        result = admin_search_model(page, page_size, word).get('data')
    except Exception as e:
        logging.exception('admin userAdmin [Exception]: %s', e)
        return abort(404) + str(e)
    return render_template('admin/admin_account.html',
                           page_active="admin_account",
                           users=result.get('user'),
                           role=result.get('role'),
                           active_page=page,
                           total=result.get('total'),
                           page_size=page_size,
                           page_count=page_view,
                           )


@bp.route('/admin_account', methods=['GET', 'POST'])
@admin_auth(['admin'])
def admin_account():
    """管理员帐号管理"""
    if request.method == 'POST':
        role = request.form.get('role', '')
        email =request.form.get('email', '')
        status = request.form.get('status', '')
        result = auth_admin_model(role, email, status)
        logging.info('USER ADMIN admin_account RESULT:%s', result)
        return jsonify(result)
    page = request.args.get('page', 0, int)
    page_size = 20
    page_view = 5
    try:
        result = get_admin_account(page, page_size).get('data')
    except Exception as e:
        logging.exception('admin userAdmin [Exception]: %s', e)
        return abort(404) + str(e)
    return render_template('admin/admin_account.html',
                           page_active="admin_account",
                           users=result.get('user'),
                           role=result.get('role'),
                           active_page=page,
                           total=result.get('total'),
                           page_size=page_size,
                           page_count=page_view,
                           )


@bp.route('/', methods=('GET', 'POST'))
@admin_auth(['user_admin'])
def userAdmin():
    """加载用户管理页"""
    page = request.args.get('page', 1, int)
    page_size = 20
    page_view = 5
    try:
        users, total = get_users_total(page, page_size)
    except Exception as e:
        logging.exception('admin userAdmin [Exception]: %s', e)
        return abort(404) + str(e)
    return render_template('admin/userAdmin.html',
                           page_active="userAdmin",
                           users=users,
                           active_page=page,
                           total=total,
                           page_size=page_size,
                           page_count=page_view,
                           )


@bp.route('/search')
@admin_auth(['user_admin'])
def search():
    """搜索模糊匹配users表中的name、tel、email字段"""
    word = request.args.get('kw')
    try:
        users = search_users(word)
    except Exception as e:
        logging.exception('admin search userinfo [Exception]:%s', e)
        return abort(404)
    return render_template('admin/userAdmin.html',
                           page_active="userAdmin",
                           users=users)


@bp.route('/add_trash', methods=('GET', 'POST'))
@admin_auth(['user_admin'])
def add_trash():
    """将账户加入回收站"""
    id = request.form.get('id', '')
    try:
        rel = add_user_trach(id)
    except Exception as e:
        logging.exception('admin add_trash [Exception]:%s', e)
        return 'Error:' + str(e)
    return jsonify(rel)


@bp.route('/delete_user', methods=('GET', 'POST'))
@admin_auth(['user_admin'])
def delete_user():
    """删除账户"""
    id = request.form.get('id', '')
    try:
        rel = delete_user_trach(id)
    except Exception as e:
        logging.exception('admin delete_user [Exception]:%s', e)
        return 'Error:' + str(e)
    return jsonify(rel)


@bp.route('/user_trash', methods=('GET', 'POST'))
@admin_auth(['user_admin'])
def user_trash():
    """已删除用户"""
    page = request.args.get('page', 1, int)
    page_size = 20
    page_count = 5
    try:
        users, total = get_users_total(page, page_size, is_delete=1)
    except Exception as e:
        logging.exception('admin get user_trash [Exception]:%s', e)
        return 'Error:' + str(e)
    return render_template('admin/trash.html',
                           page_active="user_trash",
                           users=users,
                           page_size=page_size,
                           page_count=page_count,
                           total=total,
                           active_page=page,
                           trash_type='/admin/userAdmin/user_trash?page=',
                           )


@bp.route('/restores_user', methods=('GET', 'POST'))
@admin_auth(['user_admin'])
def restores_user():
    """还原被冻结-用户"""
    user_id = request.args.get('user_id')
    try:
        rel = restores_user_model(user_id)
    except Exception as e:
        logging.exception('admin restores_user [Exception]:%s', e)
        return abort(404)
    return redirect(url_for(rel))


@bp.route('/reset_pwd', methods=('GET', 'POST'))
@admin_auth(['user_admin'])
def reset_pwd():
    """重置用户密码"""
    id = request.form.get('id', '')
    try:
        rel = reset_user_pad(id)
    except Exception as e:
        logging.exception('admin reset_pwd [Exception]:%s', e)
        return 'Error:' + str(e)
    return jsonify(rel)


@bp.route('/freezing', methods=('GET', 'POST'))
@admin_auth(['user_admin'])
def freezing():
    """冻结账户"""
    id = request.form.get('id', '')
    try:
        rel = freezing_user_model(id)
    except Exception as e:
        logging.exception('admin freezing [Exception]:%s', e)
        return 'Error:' + str(e)
    return jsonify(rel)


@bp.route('/activate_user', methods=('GET', 'POST'))
@admin_auth(['user_admin'])
def activate_user():
    """激活冻结的账户"""
    id = request.form.get('id', '')
    try:
        rel = user_activate_model(id)
    except Exception as e:
        logging.exception('admin activate_user [Exception]:%s', e)
        return 'Error:' + str(e)
    return jsonify(rel)
