import time
import datetime


def get_dawn_timestamp():
    day_time = int(time.mktime(datetime.date.today().timetuple()))
    return day_time


def get_day_time():
    rel = int(time.time())
    return rel


def get_now():
    return int(time.time())


def get_before_day():
    return int(time.time()) - 60 * 60 * 24


def format_time_second(input_time):
    timeArray = time.localtime(input_time)
    out_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return out_time


if __name__ == '__main__':
    print(format_time_second(int(time.time())))
