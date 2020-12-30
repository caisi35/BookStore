import logging
from flask import (
    Blueprint, redirect, render_template, request, url_for, session, jsonify
)
from views_front.user import login_required
from models.front_models import (
    get_user_orders_model,
    user_delete_order,
    delete_orders_model,
    get_order_details_model,
)
from utils import Logger

Logger('orders_view.log')

bp = Blueprint('orders', __name__, url_prefix='/orders')


@bp.route('/', methods=('GET', 'POST'))
@login_required
def get_orders():
    """用户订单页"""
    try:
        user_id = session.get('user_id')
        orders_ = get_user_orders_model(user_id)
        logging.info('%s get orders:[%s]', user_id, orders_)
        return render_template('front/orders_list/user_orders_list.html',
                               orders=orders_)
    except Exception as e:
        logging.exception(e)
        return redirect(request.referrer)


@bp.route('/orderDetails', methods=('GET', 'POST'))
@login_required
def orderDetails():
    """订单详情"""
    try:
        order_no = request.args.get('order_no')
        user_id = session.get('user_id')
        order_details = get_order_details_model(order_no, user_id)
        return render_template('../tests/demo_html/userinfo/orderDetails.html',
                               order_details=order_details)
    except Exception as e:
        print('============orderDetails============', e)
        return redirect(url_for('userinfo'))


@bp.route('/deleteOrders', methods=('GET', 'POST'))
@login_required
def deleteOrders():
    """选中删除订单"""
    try:
        orders_no = request.values.getlist('orders_no[]')
        user_id = session.get('user_id')
        rel = delete_orders_model(user_id, orders_no)
        return jsonify(rel)
    except Exception as e:
        print('============deleteOrder============', e)
        return redirect(url_for('userinfo.orders'))


@bp.route('/deleteOrder', methods=('GET', 'POST'))
@login_required
def deleteOrder():
    """删除订单"""
    try:
        order_no = request.form.get('order_no')
        user_id = session.get('user_id')
        rel = user_delete_order(user_id, order_no)
        return jsonify(rel)
    except Exception as e:
        print('============deleteOrder============', e)
        return redirect(url_for('userinfo.orders'))
