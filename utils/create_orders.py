import time
import random


def create_orders():
    first = str(time.strftime('%Y%m%d%H%M', time.localtime(time.time())))
    last = str(random.randint(100001, 999999))
    order_no = first + last
    return order_no