import string
import random

from werkzeug.security import generate_password_hash

from models.db import (
    ToConn,
    ToMongo,
)

ADMIN_ROLE = ['admin', 'book_admin', 'order_admin', 'user_admin']


def auth_admin_model(role, email, status):
    """
    更改管理员权限
    :param role: 管理员角色
    :param email:  管理员登录邮箱
    :param status:  提交前的状态
    :return:  更过后的状态或结果
    """
    if status == 'on' and role in ADMIN_ROLE:  # status为授权状态‘on’，其操作是撤销权限
        query = {'$pull': {'auth': role}}
        status = 'off'
    elif status == 'off' and role in ADMIN_ROLE:    # status为'off'无权限，接下来将授予权限
        query = {'$push': {'auth': role}}
        status = 'on'
    else:
        return False
    my_db = ToMongo()
    my_db.update('admin', {'email': email}, query)
    result = {'status': status}
    return result


def user_activate_model(id):
    rel = True
    conn = ToConn()
    to_exec = conn.to_execute()
    cur = to_exec.cursor()
    result = cur.execute('update users set is_freezing=0 where id=%s', (id,))
    if result:
        to_exec.commit()
    else:
        rel = False
        to_exec.rollback()
    conn.to_close()
    return rel


def freezing_user_model(id):
    rel = True
    conn = ToConn()
    to_exec = conn.to_execute()
    cur = to_exec.cursor()
    result = cur.execute('update users set is_freezing=1 where id=%s', (id,))
    if result:
        to_exec.commit()
    else:
        rel = False
        to_exec.rollback()
    conn.to_close()
    return rel


def get_pwd():
    """修改用户密码，生成随机密码"""
    src = string.ascii_letters + string.digits
    ll = random.sample(src, 8)
    pwd = ''.join(ll)
    return pwd


def reset_user_pad(id):
    rel = {'result': False}
    conn = ToConn()
    to_exec = conn.to_execute()
    cur = to_exec.cursor()
    pwd = get_pwd()
    result = cur.execute('update users set password=%s where id=%s', (generate_password_hash(pwd), id))
    if result:
        rel = {'result': True, 'password': pwd}
        to_exec.commit()
    else:
        to_exec.rollback()
    conn.to_close()
    return rel


def restores_user_model(user_id):
    rel = 'userAdmin.user_trash'
    conn = ToConn()
    to_exec = conn.to_execute()
    result = to_exec.cursor().execute('update users set is_delete=0 where id=%s', (user_id,))
    if result:
        to_exec.commit()
    else:
        to_exec.rollback()
        rel = 'userAdmin.user_trash'
    conn.to_close()
    return rel


def delete_user_trach(id):
    rel = True
    conn = ToConn()
    to_exec = conn.to_execute()
    cur = to_exec.cursor()
    result = cur.execute('delete from users where id=%s', (id,))
    if result:
        to_exec.commit()
    else:
        rel = False
        to_exec.rollback()
    conn.to_close()
    return rel


def add_user_trach(id):
    rel = True
    conn = ToConn()
    to_exec = conn.to_execute()
    cur = to_exec.cursor()
    result = cur.execute('update users set is_delete=1 where id=%s', (id,))
    if result:
        to_exec.commit()
    else:
        rel = False
        to_exec.rollback()
    conn.to_close()
    return rel


def search_users(word):
    sql = 'select * from users where position(%s in name) or position(%s in tel) or position(%s in email)'
    users = ToConn().get_db(sql, (word, word, word))
    return users


def get_users_total(page, page_size, is_delete=0):
    users = ToConn().get_db('select * from users where is_delete=%s limit %s,%s',
                            (is_delete, (page - 1) * page_size, page_size)).fetchall()
    total = ToConn().get_db('select count(*) from users where is_delete=%s', (is_delete,)).fetchone().get('count(*)')
    return users, total


def get_admin_account(page, page_size):
    my_db = ToMongo()
    result = my_db.get_col('admin').find().skip(page * page_size).limit(page_size)
    total = my_db.get_col('admin').find().count()
    return {'data': {'user': list(result), 'total': total, 'role': ADMIN_ROLE}}


def admin_search_model(page, page_size, word):
    my_db = ToMongo()
    query = [{'email': {'$regex': word}}]
    result = my_db.get_col('admin').find({'$or': query}).skip(page * page_size).limit(page_size)
    total = my_db.get_col('admin').find({'$or': query}).count()
    return {'data': {'user': list(result), 'total': total, 'role': ADMIN_ROLE}}
