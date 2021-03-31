from models.db import ToMongo
from random import sample


def choice_book_type(num=11, all=False):
    my_conn = ToMongo()
    type_list = list(my_conn.get_col('books').distinct('first_type'))
    my_conn.close_conn()
    if all:
        return type_list
    return sample(type_list, num)


if __name__ == '__main__':
    choice_book_type()