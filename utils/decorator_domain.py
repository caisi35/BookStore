from functools import wraps
from flask import make_response


def allow_cross_domain(fun):
    """
    添加跨域功能
    https://segmentfault.com/a/1990000000753690
    :param fun:
    :return:
    """
    @wraps(fun)
    def wrapper_fun(*args, **kwargs):
        rst = make_response(fun(*args, **kwargs))
        rst.headers['Access-Control-Allow-Origin'] = '*'
        rst.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE'
        allow_headers = "Referer,Accept,Origin,User-Agent"
        rst.headers['Access-Control-Allow-Headers'] = allow_headers
        return rst
    return wrapper_fun
