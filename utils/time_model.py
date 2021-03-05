import time
import datetime

ORDER_EFFECTIVE_TIME = 60 * 60 * 24


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


def get_30_day_before_timestamp():
    time_diff = 60 * 60 * 24 * 30
    now_time = get_now()
    return now_time - time_diff


def format_m_d(timestamp):
    first = format_time_second(timestamp)
    return first[5:10]


if __name__ == '__main__':
    print(get_now())
