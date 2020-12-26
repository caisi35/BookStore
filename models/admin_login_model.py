import datetime

from models import ToConn


def clear_user_count(admin):
    ToConn().to_db('update admin set sign_count=0,last_signIn_time=current_date() where id=%s',
                   (admin['id'],)).commit()


def admin_login_model(email, password):
    error = None
    admin = ToConn().get_db('select * from admin where email=%s', (email,)).fetchone()
    if admin:
        # 用户名正确

        # 获取时间差：今天日期-最近登录日期
        time_result = datetime.date.today() - admin['last_signIn_time']

        if time_result >= datetime.timedelta(days=1):
            # 上次登录时间大于一天，更新登录次数为0，并且更新最近登录时间为今天
            ToConn().to_db('update admin set sign_count=0,last_signIn_time=current_date() where id=%s',
                           (admin['id'],)).commit()
            if password != admin['password']:
                # 密码错误,登录错误次数加1
                ToConn().to_db('update admin set sign_count=sign_count+1 where id=%s', (admin['id'],)).commit()
                error = '邮箱地址或密码错误！今日剩余 4 次'
        elif admin['sign_count'] >= 5:
            # 上次登录时间小于一天, 登录次数已到5次
            error = '今日登录错误次数超限'

        if password != admin['password'] and int(admin['sign_count']) < 5:
            # 密码错误,登录错误次数加1，登录次数小于5还可以继续登录
            ToConn().to_db('update admin set sign_count=sign_count+1 where id=%s', (admin['id'],)).commit()
            sign_count = ToConn().get_db('select sign_count from admin where email=%s and id=%s',
                                         (email, admin['id'])).fetchone()
            # fetchone 查询结果为字典，需要解包
            count = 5 - int(sign_count['sign_count'])
            error = '邮箱地址或密码错误！今日剩余' + str(count) + '次'

        if not admin['is_effective']:
            # 账户已失效(not 1, 1为有效，0为无效，默认1有效)
            error = '账户已失效'
    else:
        # 用户名错误
        error = '邮箱地址或密码错误！'
    return error, admin
