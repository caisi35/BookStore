from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session, jsonify
)
from db import ToConn, ToMongo
from werkzeug.exceptions import abort
from user import login_required
from bson.objectid import ObjectId
import time, random, base64
from datetime import datetime, timedelta
from products import get_user, get_book
import products
bp = Blueprint('userinfo', __name__)


@bp.route('/userinfo', methods=('GET', 'POST'))
def userinfo():
    try:
        user = get_user(session.get('user_id'))
        print(user)
        return render_template('userinfo/userinfo.html', user=user)
    except Exception as e:
        print('============userinfo============', e)
        return redirect(request.referrer)

