import string, random
from flask import (
    Blueprint, render_template, request, jsonify
)
from werkzeug.security import generate_password_hash
from models.db import ToConn, get_page
from views_admin.signIn import admin_login_required
from werkzeug.exceptions import abort

bp = Blueprint('userAdmin', __name__, url_prefix='/admin/userAdmin')


# 加载用户管理页
@bp.route('/', methods=('GET', 'POST'))
@admin_login_required
def userAdmin():
    try:
        page = request.args.get('page', 1, int)
        # 一页展示多少用户信息
        page_user = 3
        if page == 1:
            # 请求为默认的第一页
            users = ToConn().get_db('select * from users where is_delete=0 limit %s', (page_user,)).fetchall()
            active_page = 1
        else:
            users = ToConn().get_db('select * from users where is_delete=0 limit %s,%s',
                                    ((page - 1) * page_user, page_user)).fetchall()
            active_page = page

        pages, max_page = get_page(page_user, page)
        return render_template('admin/userAdmin.html', users=users, pages=pages, active_page=active_page,
                               max_page=max_page)
    except Exception as e:
        print('==============Admin userAdmin=================', e)
        return abort(404) + str(e)


# 搜索模糊匹配users表中的name、tel、email字段
@bp.route('/search', methods=('GET',))
@admin_login_required
def search():
    try:
        word = request.args.get('kw')
        sql = 'select * from users where position(%s in name) or position(%s in tel) or position(%s in email)'
        users = ToConn().get_db(sql, (word, word, word))
        return render_template('admin/userAdmin.html', users=users)
    except Exception as e:
        print('==============Admin search=================', e)
        return abort(404)


# 加入回收站
@bp.route('/add_trash', methods=('GET', 'POST'))
@admin_login_required
def add_trash():
    try:
        conn = ToConn().to_execute()
        cur = conn.cursor()
        id = request.form.get('id', '')

        result = cur.execute('update users set is_delete=1 where id=%s', (id,))
        if result:
            conn.commit()
            return jsonify(True)
        else:
            conn.rollback()
            return jsonify(False)
    except Exception as e:
        print('==============Admin delete_user=================', e)
        return 'Error:' + str(e)


# 删除账户
@bp.route('/delete_user', methods=('GET', 'POST'))
@admin_login_required
def delete_user():
    try:
        conn = ToConn().to_execute()
        cur = conn.cursor()
        id = request.form.get('id', '')

        result = cur.execute('delete from users where id=%s', (id,))
        if result:
            conn.commit()
            return jsonify(True)
        else:
            conn.rollback()
            return jsonify(False)
    except Exception as e:
        print('==============Admin delete_user=================', e)
        return 'Error:' + str(e)


# 修改用户密码，生成随机密码
def get_pwd():
    src = string.ascii_letters + string.digits
    ll = random.sample(src, 8)
    pwd = ''.join(ll)
    return pwd


# // 重置用户密码
@bp.route('/reset_pwd', methods=('GET', 'POST'))
@admin_login_required
def reset_pwd():
    try:
        conn = ToConn().to_execute()
        cur = conn.cursor()
        id = request.form.get('id', '')
        pwd = get_pwd()
        result = cur.execute('update users set password=%s where id=%s', (generate_password_hash(pwd), id))
        if result:
            conn.commit()
            return jsonify({'result': True, 'password': pwd})
        else:
            conn.rollback()
            return jsonify({'result': False})
    except Exception as e:
        print('==============Admin reset_pwd=================', e)
        return 'Error:' + str(e)


# 冻结账户
@bp.route('/freezing', methods=('GET', 'POST'))
@admin_login_required
def freezing():
    try:
        conn = ToConn().to_execute()
        cur = conn.cursor()
        id = request.form.get('id', '')
        result = cur.execute('update users set is_freezing=1 where id=%s', (id,))
        if result:
            conn.commit()
            return jsonify(True)
        else:
            conn.rollback()
            return jsonify(False)
    except Exception as e:
        print('==============Admin freezing=================', e)
        return 'Error:' + str(e)


# 激活账户
@bp.route('/activate_user', methods=('GET', 'POST'))
@admin_login_required
def activate_user():
    try:
        conn = ToConn().to_execute()
        cur = conn.cursor()
        id = request.form.get('id', '')
        result = cur.execute('update users set is_freezing=0 where id=%s', (id,))
        if result:
            conn.commit()
            return jsonify(True)
        else:
            conn.rollback()
            return jsonify(False)
    except Exception as e:
        print('==============Admin activate_user=================', e)
        return 'Error:' + str(e)
