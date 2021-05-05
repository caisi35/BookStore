from werkzeug.exceptions import abort
import logging

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
)

from views_admin.signIn import admin_login_required, admin_auth
from models import (
    orders_query_model,
    order_handle_model,
    get_order,
)

from utils import Logger

Logger('order_admin.log')

bp = Blueprint('orderAdmin', __name__, url_prefix='/admin/orderAdmin')


@bp.route('/', methods=("GET",))
@admin_auth(auth_list=['order_admin', 'admin'])
def order_admin():
    page = request.args.get('page', 1, int)
    page_size = 15
    status = request.args.get('status', 1, int)
    try:
        order, total, books = orders_query_model(page, page_size, status)
    except Exception as e:
        logging.exception('order_admin orders_query_model [Exception]:%s', e)
        return abort(404) + str(e)
    return render_template('admin/order_admin.html',
                           def_url='/admin/orderAdmin',
                           page_active="order_admin",
                           data=order,
                           active_page=page,
                           page_count=5,
                           page_size=page_size,
                           total=total,
                           status=status,
                           is_order=True,
                           books=books,
                           )


@bp.route('/search_order', methods=["GET"])
@admin_auth(auth_list=['order_admin', 'admin'])
def search_order():
    return 's'


@bp.route('/order_handle', methods=["GET", "POST"])
@admin_auth(auth_list=['order_admin', 'admin'])
def order_handle():
    order_no = request.args.get('order_no')
    status = request.args.get('status', 1, int)
    if status in [2, 3, 4, 5] and order_no:
        # 现阶段不进行处理，后面可以扩展推送消息等功能
        order = get_order(order_no)
        return render_template('admin/order_details.html', order=order)
    msg = {}
    try:
        order_handle_model(order_no, status, msg)
    except Exception as e:
        logging.exception('order_admin order_handle [Exception]:%s', e)
    if msg:
        return msg
    return redirect(request.referrer)

