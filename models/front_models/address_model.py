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
    result = ToMongo().update('address', {'_id': ObjectId(_id)},
                              {"$set": {'name': name,
                                        'tel': tel,
                                        'province': address_list[0],
                                        'city': address_list[1],
                                        'district': address_list[2],
                                        'details': details}})
    if result.modified_count:
        rel = True
        result = ToMongo().get_col('address').find({'user_id': user_id})
    return rel, result


def set_default_addr_model(user_id, addr_id):
    rel = True
    conn = ToConn().to_execute()
    cur = conn.cursor()
    result = cur.execute('update users set address_default=%s where id=%s', (addr_id, user_id))
    if result:
        conn.commit()
        conn.close()
    else:
        rel = False
        conn.rollback()
        conn.close()
    return rel


def delete_addr_model(user_id, _id):
    rel = True
    if _id == get_user(user_id)['address_default']:
        # 如果是默认地址，删除默认地址
        conn = ToConn().to_execute()
        cur = conn.cursor()
        result = cur.execute('update users set address_default=null where id=%s', (user_id,))
        if result:
            conn.commit()
            conn.close()
        else:
            conn.rollback()
            conn.close()
            return False
    # 如果不是默认地址，直接删除默认地址
    db = ToMongo()
    count = db.delete('address', {'_id': ObjectId(_id)}).deleted_count
    if not count:
        rel = False
    return rel


def get_addr_list_model(user_id):
    rel = ToMongo().get_col('address').find({'user_id': user_id})
    rel_list = list(rel)
    return rel_list


def get_addr_info(id):
    rel = ToMongo().get_col('address').find({'_id': ObjectId(id)})
    rel_list = list(rel)
    return rel_list


def get_user_addr_info(user_id, request):
    name = request.form.get('name')
    tel = request.form.get('tel')
    address_list = request.form.get('address').strip().split(' ')
    details = request.form.get('details')
    _id = request.form.get('_id')
    result = ToMongo().insert('address',
                              {'name': name,
                               'tel': tel,
                               'province': address_list[0],
                               'city': address_list[1],
                               'district': address_list[2],
                               'details': details,
                               'user_id': user_id})
    if result.inserted_id:
        conn = ToConn().to_execute()
        cur = conn.cursor()
        r = cur.execute('update users set address_default=%s where id=%s', (str(result.inserted_id), user_id))
        if r:
            conn.commit()
            conn.close()
        else:
            conn.rollback()
            conn.close()
    return r