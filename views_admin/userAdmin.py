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
)
from views_admin.signIn import admin_login_required

bp = Blueprint('userAdmin', __name__, url_prefix='/admin/userAdmin')


@bp.route('/', methods=('GET', 'POST'))
@admin_login_required
def userAdmin():
    """加载用户管理页"""
    try:
        page = request.args.get('page', 1, int)
        page_size = 20
        page_view = 5
        users, total = get_users_total(page, page_size)
        return render_template('admin/userAdmin.html',
                               page_active="userAdmin",
                               users=users,
                               active_page=page,
                               total=total,
                               page_size=page_size,
                               page_count=page_view,
                               )
    except Exception as e:
        print('==============Admin userAdmin=================', e)
        return abort(404) + str(e)


@bp.route('/search')
@admin_login_required
def search():
    """搜索模糊匹配users表中的name、tel、email字段"""
    try:
        word = request.args.get('kw')
        users = search_users(word)
        return render_template('admin/userAdmin.html',
                               page_active="userAdmin",
                               users=users)
    except Exception as e:
        print('==============Admin search=================', e)
        return abort(404)


@bp.route('/add_trash', methods=('GET', 'POST'))
@admin_login_required
def add_trash():
    """将账户加入回收站"""
    try:
        id = request.form.get('id', '')
        rel = add_user_trach(id)
        return jsonify(rel)
    except Exception as e:
        print('==============Admin delete_user=================', e)
        return 'Error:' + str(e)


@bp.route('/delete_user', methods=('GET', 'POST'))
@admin_login_required
def delete_user():
    """删除账户"""
    try:
        id = request.form.get('id', '')
        rel = delete_user_trach(id)
        return jsonify(rel)
    except Exception as e:
        print('==============Admin delete_user=================', e)
        return 'Error:' + str(e)


@bp.route('/user_trash', methods=('GET', 'POST'))
@admin_login_required
def user_trash():
    """已删除用户"""
    try:
        page = request.args.get('page', 1, int)
        page_size = 20
        page_count = 5
        users, total = get_users_total(page, page_size, is_delete=1)
        return render_template('admin/trash.html',
                               page_active="user_trash",
                               users=users,
                               page_size=page_size,
                               page_count=page_count,
                               total=total,
                               active_page=page,
                               trash_type='/admin/userAdmin/user_trash?page=',
                               )
    except Exception as e:
        print('==============Admin user_trash=================', e)
        return 'Error:' + str(e)


@bp.route('/restores_user', methods=('GET', 'POST'))
@admin_login_required
def restores_user():
    """还原被冻结-用户"""
    try:
        user_id = request.args.get('user_id')
        rel = restores_user_model(user_id)
        return redirect(url_for(rel))
    except Exception as e:
        print('=========book Admin restores_user=========', e)
        return abort(404)


@bp.route('/reset_pwd', methods=('GET', 'POST'))
@admin_login_required
def reset_pwd():
    """重置用户密码"""
    try:
        id = request.form.get('id', '')
        rel = reset_user_pad(id)
        return jsonify(rel)
    except Exception as e:
        print('==============Admin reset_pwd=================', e)
        return 'Error:' + str(e)


@bp.route('/freezing', methods=('GET', 'POST'))
@admin_login_required
def freezing():
    """冻结账户"""
    try:
        id = request.form.get('id', '')
        rel = freezing_user_model(id)
        return jsonify(rel)
    except Exception as e:
        print('==============Admin freezing=================', e)
        return 'Error:' + str(e)


@bp.route('/activate_user', methods=('GET', 'POST'))
@admin_login_required
def activate_user():
    """激活冻结的账户"""
    try:
        id = request.form.get('id', '')
        rel = user_activate_model(id)
        return jsonify(rel)
    except Exception as e:
        print('==============Admin activate_user=================', e)
        return 'Error:' + str(e)
