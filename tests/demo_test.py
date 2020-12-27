import pymongo
from models import ToMongo
import datetime, time

day_time=int(time.mktime(datetime.date.today().timetuple()))
print(day_time, (day_time-int(time.time()))/60/60)