from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from db import ToConn
from werkzeug.exceptions import abort
from user import login_required
from db import ToMongo

bp = Blueprint('products', __name__)


@bp.route('/')
def index():
    db = ToConn()
    user = db.get_db('select * from users').fetchone()
    mydb = ToMongo()
    books = mydb.get_col('books').find().limit(15)
    new_books = mydb.get_col('books').find().skip(15).limit(12)
    book_top = mydb.get_col('books').find().sort("price", -1).limit(5)
    book_top2 = mydb.get_col('books').find().sort("price_m", -1).limit(5)
    return render_template('products/index.html', user = user, books=books, new_books = new_books,
                           book_top = book_top, book_top2 = book_top2)


