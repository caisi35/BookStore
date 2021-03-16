import traceback
import logging
from flask import (
    Blueprint,
    render_template,
)

from views_admin.signIn import admin_login_required
from models import (
    keyword_wordcloud,
    visits_scatter,
    visits_pie_rose,
    inte_sales_stack,
    hits_bar,
    sales_bar,
)
from utils import Logger

bp = Blueprint('admin', __name__, url_prefix='/admin')

Logger('admin_index_DV.log')
REMOTE_HOST = "/static/js/assets/js"


@bp.route('/', methods=('GET', 'POST'))
@admin_login_required
def admin():
    """后台管理主页"""
    try:
        visitsscatter = visits_scatter()
        visits_pie = visits_pie_rose()
        bar = hits_bar()
        sales = sales_bar()
        inte_sales_bar = inte_sales_stack()
        kw_wc = keyword_wordcloud()
    except Exception as e:
        traceback.print_exc()
        logging.exception('admin index DV [Exception]:%s', e)
        return 'Error:' + str(e)
    return render_template('admin/indexBase.html',
                           page_active="index",
                           myvisitsscatter=visitsscatter.render_embed(),
                           myvisits_pie=visits_pie.render_embed(),
                           myhitsbar=bar.render_embed(),
                           script_list_bar=bar.get_js_dependencies(),
                           mysalesbar=sales.render_embed(),
                           myinte_sales=inte_sales_bar.render_embed(),
                           mykw_wc=kw_wc.render_embed(),
                           script_list_kw_wc=kw_wc.get_js_dependencies(),
                           host=REMOTE_HOST,
                           )

