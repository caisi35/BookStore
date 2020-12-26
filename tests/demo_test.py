import pymongo
from models import ToMongo

ToMongo().get_col('books')
print(pymongo.DESCENDING)