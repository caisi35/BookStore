from werkzeug.exceptions import abort

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

bp = Blueprint('orderAdmin', __name__, url_prefix='/admin/orderAdmin')


@bp.route('/', methods=("GET",))
@admin_login_required
def order_admin():
    try:
        page = request.args.get('page', 1, int)
        page_size = 15
        status = request.args.get('status', 1, int)
        order, total = orders_query_model(page, page_size, status)
        return render_template('admin/order_admin.html',
                               def_url='/admin/orderAdmin',
                               page_active="order_admin",
                               data=list(order),
                               active_page=page,
                               page_count=5,
                               page_size=page_size,
                               total=total,
                               status=status,
                               is_order=True,
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
    status = request.args.get('status', 1, int)
    msg = {}
    order_handle_model(order_no, status, msg)
    if msg:
        return msg
    return redirect(request.referrer)
