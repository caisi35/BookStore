import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash
from db import ToConn
from views.signIn import admin_login_required


bp = Blueprint('admin', __name__, url_prefix='/admin')


# 管理主页
@bp.route('/', methods=('GET', 'POST'))
@admin_login_required
def admin():
    try:
        return render_template('admin/indexBase.html')
    except Exception as e:
        print('==============Admin login=================', e)
        return 'Error:'+str(e)




