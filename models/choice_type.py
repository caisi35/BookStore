from models.db import ToMongo
from random import sample


def choice_book_type(num=5):
    type_list = list(ToMongo().get_col('books').distinct('type'))
    return sample(type_list, num)


if __name__ == '__main__':
    choice_book_type()