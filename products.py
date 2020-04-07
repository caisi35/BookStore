from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from db import ToConn
from werkzeug.exceptions import abort
from user import login_required


bp = Blueprint('products', __name__)


@bp.route('/')
def index():
    db = ToConn()
    return render_template('products/index.html', posts='Hello My Book Store!')