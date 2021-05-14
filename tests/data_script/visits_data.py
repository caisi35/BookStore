"""

用户访问量测试

"""
import random

from models import ToMongo
from utils import (
    get_dawn_timestamp,
    )


def get_users(user_id_list, total):
    lit = []
    for i in range(1, total):
        lit.append(random.choice(user_id_list))
    return lit


if __name__ == '__main__':
    # delete 'visits' collections
    # print(ToMongo().mydb['visits'].drop())

    # date timestamp list
    lit = []
    for d in range(0, 31):
        days = get_dawn_timestamp() - 60 * 60 * 24 * d
        lit.append(days)
    # user id list
    u_id_list = []
    for u in range(1, 100):
        u_id_list.append(u)

    for t in lit:
        user_id = get_users(u_id_list, random.randint(1, len(u_id_list)))
        ToMongo().insert('visits', {'date': t, 'users_id': user_id})



