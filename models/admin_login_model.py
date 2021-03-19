from werkzeug.security import generate_password_hash, check_password_hash

from models import ToConn, ToMongo
from utils import Logger, get_now

FROZEN_TIME = 60*5


def clear_user_count(admin):
    conn = ToMongo()
    result = conn.update('admin', {'email': admin.get('email')}, {'$set': {'sign_count': 0}})
    conn.close_conn()
    return result.modified_count


def admin_login_model(email, password):
    result = {}
    conn = ToMongo()
    admin = conn.get_col('admin').find_one({'email': email, 'is_effective': 1})
    if admin:
        # 用户名正确
        if admin['sign_count'] >= 5 and get_now() - admin['last_signIn_time'] < FROZEN_TIME:
            result['error'] = '请 {}秒 后再重试'.format(FROZEN_TIME - (get_now() - admin['last_signIn_time']))
            conn.close_conn()
            return result
        else:
            if check_password_hash(admin['password'], password):  # 成功
                conn.update('admin',
                            {'email': admin.get('email')},
                            {'$set': {'sign_count': 0, 'last_signIn_time': get_now()}})
                result['admin'] = admin
                conn.close_conn()
                return result
            else:  # 失败
                conn.update('admin',
                            {'email': admin.get('email')},
                            {'$inc': {'sign_count': 1}})
                conn.update('admin',
                            {'email': admin.get('email')},
                            {'$set': {'last_signIn_time': get_now()}})
                error = '邮箱地址或密码错误！剩余 {} 次'.format(5 - (admin['sign_count'] + 1))
                result['error'] = error
                conn.close_conn()
                return result
    else:  # 用户名错误
        result['error'] = '邮箱地址或密码错误！'
        conn.close_conn()
        return result


def admin_register(email, password, auth_list):
    user = {
        'email': email,
        'password': generate_password_hash(password),
        'is_effective': 1,
        'last_signIn_time': 0,
        'create_time': get_now(),
        'sign_count': 0,
        'auth': auth_list
    }
    my_db = ToMongo()
    result = my_db.insert('admin', user)
    return result.inserted_id


# def clear_user_count(admin):
#     conn = ToConn()
#     conn.to_db('update admin set sign_count=0,last_signIn_time=current_date() where id=%s',
#                    (admin['id'],)).commit()
#     conn.to_close()


# def admin_login_model(email, password):
#     error = None
#     admin = ToConn().get_db('select * from admin where email=%s', (email,)).fetchone()
#     conn = ToConn()
#     if admin:
#         # 用户名正确
#
#         # 获取时间差：今天日期-最近登录日期
#         time_result = datetime.date.today() - admin['last_signIn_time']
#
#         if time_result >= datetime.timedelta(days=1):
#             # 上次登录时间大于一天，更新登录次数为0，并且更新最近登录时间为今天
#             conn.to_db('update admin set sign_count=0,last_signIn_time=current_date() where id=%s',
#                            (admin['id'],)).commit()
#             if password != admin['password']:
#                 # 密码错误,登录错误次数加1
#                 conn.to_db('update admin set sign_count=sign_count+1 where id=%s', (admin['id'],)).commit()
#                 error = '邮箱地址或密码错误！今日剩余 4 次'
#         elif admin['sign_count'] >= 5:
#             # 上次登录时间小于一天, 登录次数已到5次
#             error = '今日登录错误次数超限'
#
#         if password != admin['password'] and int(admin['sign_count']) < 5:
#             # 密码错误,登录错误次数加1，登录次数小于5还可以继续登录
#             conn.to_db('update admin set sign_count=sign_count+1 where id=%s', (admin['id'],)).commit()
#             sign_count = conn.get_db('select sign_count from admin where email=%s and id=%s',
#                                          (email, admin['id'])).fetchone()
#             # fetchone 查询结果为字典，需要解包
#             count = 5 - int(sign_count['sign_count'])
#             error = '邮箱地址或密码错误！今日剩余' + str(count) + '次'
#
#         if not admin['is_effective']:
#             # 账户已失效(not 1, 1为有效，0为无效，默认1有效)
#             error = '账户已失效'
#     else:
#         # 用户名错误
#         error = '邮箱地址或密码错误！'
#     conn.to_close()
#     return error, admin
