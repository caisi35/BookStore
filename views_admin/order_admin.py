from werkzeug.exceptions import abort
import logging

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
)

from views_admin.signIn import admin_login_required
from models import (
    orders_query_model,
    order_handle_model,
)

from utils import Logger

Logger('order_admin.log')

bp = Blueprint('orderAdmin', __name__, url_prefix='/admin/orderAdmin')


@bp.route('/', methods=("GET",))
@admin_login_required
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
@admin_login_required
def search_order():
    return 's'


@bp.route('/order_handle', methods=["GET", "POST"])
@admin_login_required
def order_handle():
    order_no = request.args.get('order_no')
    status = request.args.get('status', 1, int)
    msg = {}
    try:
        order_handle_model(order_no, status, msg)
    except Exception as e:
        logging.exception('order_admin order_handle [Exception]:%s', e)
    if msg:
        return msg
    return redirect(request.referrer)
