from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session, jsonify
)
from db import ToConn, ToMongo
from werkzeug.exceptions import abort
from user import login_required
from bson.objectid import ObjectId
import time, random, base64
from datetime import datetime, timedelta
from products import get_user, get_book
import products
bp = Blueprint('userinfo', __name__)


# 用户信息页
@bp.route('/userinfo', methods=('GET', 'POST'))
def userinfo():
    try:
        user = get_user(session.get('user_id'))
        return render_template('userinfo/userinfo.html', user=user)
    except Exception as e:
        print('============userinfo============', e)
        return redirect(request.referrer)


# 查询用户订单信息
def get_orders(user_id):
    result = ToMongo().get_col('order').find({'user_id': user_id, 'is_effective': 1})
    orders = []
    for order in result:
        amount = order['amount']
        order_no = order['order_no']
        create_time = order['create_time']
        books = order['books']
        book_info = []
        for book in books:
            book_num = book['book_num']
            book_info.append({'book_num':book_num,'books':get_book(ObjectId(book['book_id']))})
        orders.append({'amount':amount,'order_no':order_no,'create_time':create_time,'book_info':book_info})
    return orders


# 用户订单页
@bp.route('/userinfo/order', methods=('GET', 'POST'))
def orders():
    try:
        user_id = session.get('user_id')
        orders = get_orders(user_id)
        return render_template('userinfo/orders.html', orders=orders)
    except Exception as e:
        print('============orders============', e)
        return redirect(request.referrer)


# 用户信息页
@bp.route('/userinfo/info', methods=('GET', 'POST'))
def info():
    try:
        user = get_user(session.get('user_id'))

        return render_template('userinfo/info.html', user=user)
    except Exception as e:
        print('============info============', e)
        return redirect(request.referrer)


# 收货地址页
@bp.route('/userinfo/address', methods=('GET', 'POST'))
def address():
    try:
        user_id = session.get('user_id')
        result = ToMongo().get_col('address').find({'user_id':user_id})
        return render_template('userinfo/address.html', addr=result)
    except Exception as e:
        print('============address============', e)
        return redirect(request.referrer)