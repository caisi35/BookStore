from bson.objectid import ObjectId
from models import (
    ToMongo,
    ToConn
)
from models.front_models.products_model import get_user


def edit_addr_model(user_id, request):
    rel = False
    name = request.form.get('name')
    tel = request.form.get('tel')
    address_list = request.form.get('address').strip().split(' ')
    details = request.form.get('details')
    _id = request.form.get('_id')
    db_conn = ToMongo()
    result = db_conn.update('address', {'_id': ObjectId(_id)},
                              {"$set": {'name': name,
                                        'tel': tel,
                                        'province': address_list[0],
                                        'city': address_list[1],
                                        'district': address_list[2],
                                        'details': details}})
    if result.modified_count:
        rel = True
        result = db_conn.get_col('address').find({'user_id': user_id})
    db_conn.close_conn()
    return rel, result


def set_default_addr_model(user_id, addr_id):
    rel = True
    conn = ToConn()
    to_exec = conn.to_execute()
    cur = to_exec.cursor()
    result = cur.execute('update users set address_default=%s where id=%s', (addr_id, user_id))
    if result:
        to_exec.commit()
        to_exec.close()
    else:
        rel = False
        to_exec.rollback()
        to_exec.close()
    conn.to_close()
    return rel


def delete_addr_model(user_id, _id):
    rel = True
    if _id == get_user(user_id)['address_default']:
        # 如果是默认地址，删除默认地址
        conn = ToConn()
        to_exec = conn.to_execute()
        cur = to_exec.cursor()
        result = cur.execute('update users set address_default=null where id=%s', (user_id,))
        if result:
            to_exec.commit()
            to_exec.close()
        else:
            to_exec.rollback()
            to_exec.close()
            return False
    # 如果不是默认地址，直接删除默认地址
    db = ToMongo()
    count = db.delete('address', {'_id': ObjectId(_id)}).deleted_count
    if not count:
        rel = False
    db.close_conn()
    return rel


def get_addr_list_model(user_id):
    db_conn = ToMongo()
    rel = db_conn.get_col('address').find({'user_id': user_id})
    rel_list = list(rel)
    db_conn.close_conn()
    return rel_list


def get_addr_info(id):
    db_conn = ToMongo()
    rel = db_conn.get_col('address').find({'_id': ObjectId(id)})
    rel_list = list(rel)
    db_conn.close_conn()
    return rel_list


def get_user_addr_info(user_id, request):
    name = request.form.get('name')
    tel = request.form.get('tel')
    address_list = request.form.get('address').strip().split(' ')
    details = request.form.get('details')
    _id = request.form.get('_id')
    db_conn = ToMongo()
    result = db_conn.insert('address',
                              {'name': name,
                               'tel': tel,
                               'province': address_list[0],
                               'city': address_list[1],
                               'district': address_list[2],
                               'details': details,
                               'user_id': user_id})
    if result.inserted_id:
        conn = ToConn()
        to_exec = conn.to_execute()
        cur = to_exec.cursor()
        r = cur.execute('update users set address_default=%s where id=%s', (str(result.inserted_id), user_id))
        if r:
            to_exec.commit()
            to_exec.close()
        else:
            to_exec.rollback()
            to_exec.close()
        conn.to_close()
    db_conn.close_conn()
    return r