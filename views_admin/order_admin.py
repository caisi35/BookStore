import inspect
from werkzeug.exceptions import abort

from flask import (
    Blueprint,
    render_template,
    request,
)

from views_admin.signIn import admin_login_required
from models import (
    orders_query_model,
)

bp = Blueprint('orderAdmin', __name__, url_prefix='/admin/orderAdmin')


@bp.route('/', methods=("GET",))
@admin_login_required
def process():
    try:
        page = request.args.get('page', 1, int)
        page_size = 15
        order, total = orders_query_model(page, page_size, 'process')
        return render_template('admin/order_admin.html',
                               def_url='/admin/orderAdmin',
                               page_active="process",
                               data=list(order),
                               active_page=page,
                               page_count=5,
                               page_size=page_size,
                               total=total,
                               )
    except Exception as e:
        print('==============Admin order process=================', e)
        return abort(404) + str(e)


@bp.route('/invalid_orders')
@admin_login_required
def invalid_orders():
    try:
        page = request.args.get('page', 1, int)
        page_size = 15
        order, total = orders_query_model(page, page_size, 'invalid')
        return render_template('admin/order_admin.html',
                               def_url='admin/orderAdmin/'+str(inspect.stack()[0][3]),
                               page_active="invalid",
                               data=list(order),
                               active_page=page,
                               page_count=5,
                               page_size=page_size,
                               total=total,
                               )
    except Exception as e:
        print('==============Admin order process=================', e)
        return abort(404) + str(e)


@bp.route('/search_order', methods=["GET"])
@admin_login_required
def search_order():
    return 's'


@bp.route('/order_handle', methods=["GET", "POST"])
@admin_login_required
def order_handle():
    order_no = request.args.get('order_no')
    return order_no
