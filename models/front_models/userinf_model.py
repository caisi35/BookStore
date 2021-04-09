from bson import ObjectId
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from models import ToConn, ToMongo

from utils import (
    format_time_second,
    check_img_suffix,
)

HISTORY = 20  # 展示记录数


def clear_history_model(user_id):
    """清除浏览记录"""
    conn = ToMongo()
    result = False
    query = {'_id': str(user_id)}
    ret = conn.update('history',
                      query,
                      {'$set': {'book_ids': []}})
    if ret.modified_count:
        result = True
    conn.close_conn()
    return result


def get_history_model(user_id):
    """获取浏览记录"""
    conn = ToMongo()
    ret = conn.get_col('history').find_one({'_id': str(user_id)})
    book_ids = ret.get('book_ids')
    result = []
    for id in book_ids[-HISTORY:]:
        book = conn.get_col('books').find_one({'_id': ObjectId(id)})
        result.append(book)
    conn.close_conn()
    return result


def to_delete_collection(user_id, ids):
    conn = ToMongo()
    result = False
    query = {'_id': str(user_id)}
    ret = conn.update('collection',
                      query,
                      {'$pull': {'book_ids': {'book_id': {'$in': ids}}}})
    if ret.modified_count:
        result = True
    conn.close_conn()
    return result


def get_user_collections(user_id):
    conn = ToMongo()
    ret = conn.get_col('collection').find_one({'_id': str(user_id)})
    result = []
    for info in ret.get('book_ids'):
        id = info.get('book_id')
        book = conn.get_col('books').find_one({'_id': ObjectId(id)})
        collection_time = info.get('create_time')
        book.update({'collection_time': format_time_second(collection_time)})
        result.append(book)
    conn.close_conn()
    return result


def change_pwd_model(user_id, new_pw):
    rel = True
    conn = ToConn()
    to_exec = conn.to_execute()
    cur = to_exec.cursor()
    sql = 'update users set password=%s where id=%s'
    result = cur.execute(sql, (generate_password_hash(new_pw), user_id))
    if result:
        # 修改成功，提交
        to_exec.commit()
        to_exec.close()
    else:
        # 失败，回滚
        rel = False
        to_exec.rollback()
        to_exec.close()
    conn.to_close()
    return rel


def upload_avatar_model(user_id, img):
    rel = True
    s_img = secure_filename(img.filename)
    img_suffix = s_img.split('.')[-1]
    # 随机文件名+后缀
    if check_img_suffix(img_suffix):
        filepath = './static/images/avatar/' + str(user_id) + '.' + str(img_suffix)
        filename = filepath.split('/')[-1]
        img.save(filepath)
        conn = ToConn()
        to_exec = conn.to_execute()
        cur = to_exec.cursor()
        result = cur.execute('update users set avatar=%s where id=%s', (filename, user_id))
        if result:
            to_exec.commit()
            to_exec.close()
        else:
            rel = False
            to_exec.rollback()
            to_exec.close()
        conn.to_close()
        return rel
    else:
        return False


def edit_userinfo_model(user_id, request):
    rel = True
    name = request.form.get('name')
    gender = request.form.get('gender')
    age = request.form.get('age')
    birthday = request.form.get('birthday')
    email = request.form.get('email')
    tel = request.form.get('tel')
    identity_select = request.form.get('identity_')
    hobbies = request.form.get('hobbies')
    introduce = request.form.get('introduce')
    conn = ToConn()
    to_exec = conn.to_execute()
    cur = to_exec.cursor()
    sql = 'update users set name=%s,gender=%s,age=%s,birthday=%s,email=%s,tel=%s,identity=%s,hobbies=%s,' \
          'introduce=%s where id=%s'
    result = cur.execute(sql, (name, gender, age, birthday, email, tel, identity_select, hobbies,
                               introduce, user_id))
    if result:
        to_exec.commit()
        to_exec.close()
    else:
        rel = False
        to_exec.rollback()
        to_exec.close()
    conn.to_close()
    return rel
