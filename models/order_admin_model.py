from models.db import ToMongo
from utils.time_model import (
    get_before_day,
)


def orders_query_model(page, page_size, order_status='process'):
    query = {}
    if order_status == 'process':
        print(get_before_day())
        query = {'$and': [{'is_processed': 0},
                          {'is_effective': 1},
                          {'create_time': {'$gte': get_before_day()}}]}
    elif order_status == 'invalid':
        query = {'$and': [{'is_processed': 0},
                          {'is_effective': 1}]}
    order = ToMongo().get_col('order').find(query).skip((page - 1) * page_size).limit(page_size)
    total = ToMongo().get_col('order').find(query).count()
    order_list = list(order)
    return order_list, total


if __name__ == '__main__':
    print(orders_query_model(1, 15, 'invalid'))
