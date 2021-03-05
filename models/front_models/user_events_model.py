from werkzeug.security import generate_password_hash, check_password_hash
from models import ToMongo, ToConn
from utils import (
    get_now,
    get_dawn_timestamp,
    get_day_time)


def user_login_model(username, password):
    db = ToConn()
    error = None
    user = db.get_db(
        'select * from users where tel = %s', (username,)
    ).fetchone()
    if user is None:
        error = 'Incorrect username or password'
    elif username != str(user['tel']):
        error = 'Incorrect username or password'
    elif not check_password_hash(user['password'], password):
        error = 'Incorrect username or password'
    elif user['is_freezing']:
        error = 'The User Freezing, Please Contact Administrator'
    return user, error


def user_register_model(username, password, password_again):
    db = ToConn()
    error = None
    if not username:
        error = 'Username or Password is Required'
    elif not password:
        error = 'Username or Password is Required'
    elif password != password_again:
        error = 'Username or Password is Required'
    elif db.get_db(
            'select id from users where tel = %s', (username,)
    ).fetchone() is not None:
        error = 'User {} is Already Registered'.format(username)
    if error is None:
        db = ToConn()
        comm = db.to_db(
            'insert into users(tel,password) values (%s,%s)',
            (username, generate_password_hash(password))
        )
        comm.commit()
        comm.close()
    return error


def add_visits(user_id):
    """访问量加1函数"""
    dawn_timestamp = get_dawn_timestamp()
    last_date = ToMongo().get_col('visits').aggregate([{'$group': {'_id': '$_id', 'day': {'$last': '$date'}}}])
    date_list = list(last_date)
    # 不为空
    if date_list:
        # 同一天加入
        if date_list[0]['day'] == get_dawn_timestamp():
            ToMongo().update('visits', {'_id': date_list[0]['_id']}, {'$addToSet': {'users_id': user_id}})
        else:
            # 不是同一天，插入新的文档
            ToMongo().insert('visits', {'date': dawn_timestamp, 'users_id': [user_id]})
    else:
        # 为空也插入
        ToMongo().insert('visits', {'date': dawn_timestamp, 'users_id': [user_id]})
