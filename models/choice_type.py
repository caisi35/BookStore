from models.db import ToMongo
from random import sample


def choice_book_type(num=11):
    my_conn = ToMongo()
    type_list = list(my_conn.get_col('books').distinct('type'))
    my_conn.close_conn()
    return sample(type_list, num)


if __name__ == '__main__':
    choice_book_type()