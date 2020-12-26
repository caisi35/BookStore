import string
import random

from werkzeug.security import generate_password_hash

from models.db import (
    ToConn,
)


def user_activate_model(id):
    rel = True
    conn = ToConn().to_execute()
    cur = conn.cursor()
    result = cur.execute('update users set is_freezing=0 where id=%s', (id,))
    if result:
        conn.commit()
    else:
        rel = False
        conn.rollback()
    return rel


def freezing_user_model(id):
    rel = True
    conn = ToConn().to_execute()
    cur = conn.cursor()
    result = cur.execute('update users set is_freezing=1 where id=%s', (id,))
    if result:
        conn.commit()
    else:
        rel = False
        conn.rollback()
    return rel


def get_pwd():
    """修改用户密码，生成随机密码"""
    src = string.ascii_letters + string.digits
    ll = random.sample(src, 8)
    pwd = ''.join(ll)
    return pwd


def reset_user_pad(id):
    rel = {'result': False}
    conn = ToConn().to_execute()
    cur = conn.cursor()
    pwd = get_pwd()
    result = cur.execute('update users set password=%s where id=%s', (generate_password_hash(pwd), id))
    if result:
        rel = {'result': True, 'password': pwd}
        conn.commit()
    else:
        conn.rollback()
    return rel


def restores_user_model(user_id):
    rel = 'admin.user_trash'
    conn = ToConn().to_execute()
    result = conn.cursor().execute('update users set is_delete=0 where id=%s', (user_id,))
    if result:
        conn.commit()
    else:
        conn.rollback()
        rel = 'admin.user_trash'
    return rel


def delete_user_trach(id):
    rel = True
    conn = ToConn().to_execute()
    cur = conn.cursor()
    result = cur.execute('delete from users where id=%s', (id,))
    if result:
        conn.commit()
    else:
        rel = False
        conn.rollback()
    return rel


def add_user_trach(id):
    rel = True
    conn = ToConn().to_execute()
    cur = conn.cursor()
    result = cur.execute('update users set is_delete=1 where id=%s', (id,))
    if result:
        conn.commit()
    else:
        rel = False
        conn.rollback()
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
