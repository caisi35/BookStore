import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash
from db import ToConn
from views import signIn


bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/', methods=('GET', 'POST'))
def admin():
    try:
        users = ToConn().get_db('select * from users').fetchall()
        return render_template('admin/userAdmin.html', users=users)
    except Exception as e:
        print('==============Admin login=================', e)
        return 'Error:'+str(e)


@bp.route('delete_user', methods=('GET', 'POST'))
def delete_user():
    try:
        conn = ToConn().to_execute()
        cur = conn.cursor()
        id = request.form.get('id', '')

        result = cur.execute('delete from users where id=%s', (id, ))
        if result:
            conn.commit()
            return True
        else:
            conn.rollback()
            return False
    except Exception as e:
        print('==============Admin delete_user=================', e)
        return 'Error:' + str(e)


def admin_login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get('admin_id') is None:
            return redirect(url_for('admin.login'))
        return view(**kwargs)
    return wrapped_view
