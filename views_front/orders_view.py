import logging
from flask import (
    Blueprint, redirect, render_template, request, url_for, session, jsonify, flash
)
from views_front.user import login_required
from models.front_models import (
    get_user_orders_model,
    user_delete_order,
    get_order_details_model,
    get_badge_model,
    cancel_model,
    refund_model,
    evaluate_model,
    update_status,
    update_status_user_id,
)
from utils import (
    Logger,
    allow_cross_domain,
)

Logger('orders_view.log')

bp = Blueprint('orders', __name__, url_prefix='/orders')


@bp.route('/', methods=('GET', 'POST'))
@login_required
def get_orders():
    """用户订单页"""
    try:
        user_id = session.get('user_id')
        orders_status = request.args.get('orders_status', -1, int)
        orders_, active = get_user_orders_model(user_id, orders_status)
        logging.info('%s get %s total:[%s]', user_id, orders_status, len(orders_))
        return render_template('front/user_info_manage/user_orders_list.html',
                               orders=orders_,
                               active=active,
                               active_nav='order')
    except Exception as e:
        logging.exception(e)
        return redirect(request.referrer)


@bp.route('/get_order_badge')
@login_required
@allow_cross_domain
def get_order_badge():
    user_id = session.get('user_id')
    badge = get_badge_model(user_id)
    return jsonify(badge)


@bp.route('/orderDetails', methods=('GET', 'POST'))
@login_required
def orderDetails():
    """订单详情"""
    try:
        order_no = request.args.get('order_no')
        user_id = session.get('user_id')
        order_details = get_order_details_model(order_no, user_id)
        return render_template('front/orders_list/orderDetails.html',
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


@bp.route('/cancel')
@login_required
def cancel():
    """取消订单"""
    order_no = request.args.get('order_no')
    user_id = session.get('user_id')
    result = cancel_model(order_no, user_id)
    if result:
        flash('错误，请重试！')
    return redirect(request.referrer)


@bp.route('/refund')
@login_required
def refund():
    """退款申请"""
    order_no = request.args.get('order_no')
    user_id = session.get('user_id')
    result = refund_model(order_no, user_id)
    if result:
        flash('错误，请重试！')
    return redirect(request.referrer)


@bp.route('/evaluate', methods=['GET', 'POST'])
@login_required
def evaluate():
    """评论"""
    if request.method == 'GET':
        order_no = request.args.get('order_no')
        return render_template('front/orders_list/evaluate.html',
                               order_no=order_no)

    user_name = session.get('user_name')
    user_id = session.get('user_id')
    order_no = request.form.get('order_no')
    try:
        result = evaluate_model(user_id, user_name, request)
    except ValueError as e:
        logging.exception('user:%s evaluate exception:%s', user_id, str(e))
        result = {'error': '评论星级不能为空，请重试！'}
    except AttributeError as e:
        logging.exception('user:%s evaluate exception:%s', user_id, str(e))
        result = {'error': '评论失败，请重试！'}
        if 'NoneType' in str(e):
            result = {'error': '已评论！'}
    logging.info('user:%s evaluate result:%s', user_id, result)
    if result:
        flash(result.get('error'))
        return redirect(request.referrer)
    rel = update_status(order_no)
    return redirect(url_for('orders.orderDetails', order_no=order_no))


@bp.route('/receive', methods=['GET', 'POST'])
@login_required
def receive():
    """确认收货"""
    user_id = session.get('user_id')
    order_no = request.args.get('order_no')
    try:
        result = update_status_user_id(order_no, user_id)
    except Exception as e:
        logging.exception('user:%s receiving goods exception:[%s]', user_id, str(e))
        result = False
    if not result:
        flash('操作失败，请重试！')
    return redirect(request.referrer)