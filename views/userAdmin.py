import string, random
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash
from db import ToConn
from views.signIn import admin_login_required
from werkzeug.exceptions import abort

bp = Blueprint('userAdmin', __name__, url_prefix='/admin/userAdmin')


# 加载用户管理页
@bp.route('/', methods=('GET', 'POST'))
@admin_login_required
def userAdmin():
    try:
        users = ToConn().get_db('select * from users')
        return render_template('admin/userAdmin.html', users=users)
    except Exception as e:
        print('==============Admin delete_user=================', e)
        return abort(404) + str(e)


# 搜索模糊匹配users表中的name、tel、email字段
@bp.route('/search', methods=('GET', ))
@admin_login_required
def search():
    try:
        word = request.args.get('kw')
        sql = 'select * from users where position(%s in name) or position(%s in tel) or position(%s in email)'
        users = ToConn().get_db(sql, (word, word, word))
        return render_template('admin/userAdmin.html', users=users)
    except Exception as e:
        print('==============Admin delete_user=================', e)
        return abort(404)


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


# 生成随机密码
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
        result = cur.execute('update users set is_freezing=1 where id=%s', (id, ))
        if result:
            conn.commit()
            return jsonify(True)
        else:
            conn.rollback()
            return jsonify(False)
    except Exception as e:
        print('==============Admin reset_pwd=================', e)
        return 'Error:' + str(e)


# 激活账户
@bp.route('/activate_user', methods=('GET', 'POST'))
@admin_login_required
def activate_user():
    try:
        conn = ToConn().to_execute()
        cur = conn.cursor()
        id = request.form.get('id', '')
        result = cur.execute('update users set is_freezing=0 where id=%s', (id, ))
        if result:
            conn.commit()
            return jsonify(True)
        else:
            conn.rollback()
            return jsonify(False)
    except Exception as e:
        print('==============Admin reset_pwd=================', e)
        return 'Error:' + str(e)