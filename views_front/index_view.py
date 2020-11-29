from flask import (
    Blueprint, redirect, render_template, request, url_for, session, jsonify
)
from models.db import ToConn, ToMongo, get_like_books
from werkzeug.exceptions import abort
from views_front.user import login_required
from bson.objectid import ObjectId
import time, random, base64
from datetime import datetime, timedelta

bp = Blueprint('indexView', __name__)


@bp.route('')
def banner_img():
    pass