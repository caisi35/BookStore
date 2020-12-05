from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from bson.objectid import ObjectId
from models.db import ToMongo, get_like_books, get_pages
from views_admin.signIn import admin_login_required
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

bp = Blueprint('orderAdmin', __name__, url_prefix='/admin/orderAdmin')


@bp.route('/', methods=("GET",))
@admin_login_required
def process():
    try:
        page = request.args.get('page', 1, int)
        page_size = 20
        if page == 1:
            # 请求为默认的第一页
            order = ToMongo().get_col('order').find().limit(page_size)
            total = ToMongo().get_col('order').find().count()
        else:
            order = ToMongo().get_col('order').find().skip((page - 1) * page_size).limit(page_size)
            total = ToMongo().get_col('order').find().count()
        return render_template('admin/order_admin.html',
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


@bp.route('/search_order', methods=["GET"])
@admin_login_required
def search_order():
    return 's'


@bp.route('/order_handle', methods=["GET", "POST"])
@admin_login_required
def order_handle():
    order_no = request.args.get('order_no')
    return order_no