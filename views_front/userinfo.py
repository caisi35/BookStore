from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, session, jsonify
)
from models.db import ToConn, ToMongo
from views_front.user import login_required
from bson.objectid import ObjectId
from views_front.products import get_user
from werkzeug.security import check_password_hash, generate_password_hash
from models.front_models import (
    get_user_orders_model,
    user_delete_order,
    delete_orders_model,
    get_order_details_model,
    edit_userinfo_model,
    upload_avatar_model,
    change_pwd_model,
    get_user_addr_info,
    get_addr_list_model,
    delete_addr_model,
    set_default_addr_model,
    edit_addr_model,
)

bp = Blueprint('userinfo', __name__)


@bp.route('/userInfo', methods=('GET', 'POST'))
@login_required
def userInfo():
    """用户信息页"""
    try:
        user = get_user(session.get('user_id'))
        return render_template('userinfo/userinfoBase.html',
                               user=user)
    except Exception as e:
        print('============userinfo============', e)
        return redirect(request.referrer)


@bp.route('/userinfo/orders', methods=('GET', 'POST'))
@login_required
def orders():
    """用户订单页"""
    try:
        user_id = session.get('user_id')
        orders_ = get_user_orders_model(user_id)
        return render_template('userinfo/orders.html',
                               orders=orders_)
    except Exception as e:
        print('============orders============', e)
        return redirect(request.referrer)


@bp.route('/userinfo/deleteOrder', methods=('GET', 'POST'))
@login_required
def deleteOrder():
    """删除订单"""
    try:
        order_no = request.form.get('order_no')
        user_id = session.get('user_id')
        rel = user_delete_order(user_id, order_no)
        return jsonify(rel)
    except Exception as e:
        print('============deleteOrder============', e)
        return redirect(url_for('userinfo.orders'))


@bp.route('/userinfo/deleteOrders', methods=('GET', 'POST'))
@login_required
def deleteOrders():
    """选中删除订单"""
    try:
        orders_no = request.values.getlist('orders_no[]')
        user_id = session.get('user_id')
        rel = delete_orders_model(user_id, orders_no)
        return jsonify(rel)
    except Exception as e:
        print('============deleteOrder============', e)
        return redirect(url_for('userinfo.orders'))


@bp.route('/userinfo/orderDetails', methods=('GET', 'POST'))
@login_required
def orderDetails():
    """订单详情"""
    try:
        order_no = request.args.get('order_no')
        user_id = session.get('user_id')
        order_details = get_order_details_model(order_no, user_id)
        return render_template('userinfo/orderDetails.html',
                               order_details=order_details)
    except Exception as e:
        print('============orderDetails============', e)
        return redirect(url_for('userinfo'))


@bp.route('/userinfo/info', methods=('GET', 'POST'))
@login_required
def info():
    """用户信息页"""
    try:
        user_id = session.get('user_id')
        if request.method == 'POST':
            result = edit_userinfo_model(user_id, request)
            if result:
                # 更新成功返回更新后的用户信息
                return render_template('userinfo/info.html', user=get_user(user_id))
            else:
                flash('修改错误！')
        return render_template('userinfo/info.html', user=get_user(user_id))
    except Exception as e:
        print('============info============', e)
        return redirect(url_for('userinfo.userinfo'))


@bp.route('/userinfo/inputAvatar', methods=('POST',))
@login_required
def inputAvatar():
    """上传头像"""
    try:
        img = request.files['avatar']
        user_id = session.get('user_id')
        result = upload_avatar_model(user_id, img)
        if not result:
            flash("提交失败，请重试！")
        return render_template('userinfo/info.html',
                               user=get_user(user_id))
    except Exception as e:
        print('============inputAcatar============', e)
        # 出错，重定向到userinfo页
        return redirect(url_for('userinfo.userinfo'))


@bp.route('/userinfo/changePW', methods=('GET', 'POST'))
@login_required
def changePW():
    """修改用户密码"""
    try:
        old_pw = request.form.get('old_pw')
        new_pw = request.form.get('new_pw')
        confirm_pw = request.form.get('confirm_pw')
        user_id = session.get('user_id')
        user = get_user(user_id)
        if new_pw != confirm_pw:
            flash("密码不一致！")
        elif not check_password_hash(user['password'], old_pw):
            flash("密码错误！")
        else:
            if not change_pwd_model(user_id, new_pw):
                flash("修改失败，请重试！")
        session.clear()
        return render_template('user/login.html', next=request.referrer)
    except Exception as e:
        print('============change_pw============', e)
        flash("修改失败，请重试！")
        return redirect(url_for('userinfo.userinfo'))


@bp.route('/userinfo/address', methods=('GET', 'POST'))
@login_required
def address():
    """收货地址页"""
    try:
        user_id = session.get('user_id')
        if request.method == 'POST':
            r = get_user_addr_info(user_id, request)
            if not r:
                flash('操作失败，请重试！')
            return redirect(request.url)
        result = get_addr_list_model(user_id)
        address_default = get_user(user_id)['address_default']
        return render_template('userinfo/address.html',
                               addr=list(result),
                               address_default=address_default)
    except Exception as e:
        print('============address============', e)
        return redirect(request.referrer)


@bp.route('/userinfo/addressDelete', methods=('POST',))
@login_required
def addressDelete():
    """删除收货地址"""
    try:
        _id = request.form.get('_id')
        user_id = session.get('user_id')
        rel = delete_addr_model(user_id, _id)
        return jsonify(rel)
    except Exception as e:
        print('============addressDelete============', e)
        return jsonify(result=False)


@bp.route('/userinfo/addressDefault', methods=('POST',))
@login_required
def addressDefault():
    """设为默认地址"""
    try:
        _id = request.form.get('_id')
        user_id = session.get('user_id')
        rel = set_default_addr_model(user_id, _id)
        return jsonify(rel)
    except Exception as e:
        print('============addressDelete============', e)
    return jsonify(result=False)


@bp.route('/userinfo/addressChange', methods=('POST', 'GET'))
@login_required
def addressChange():
    """编辑更改收货人地址"""
    try:
        user_id = session.get('user_id')
        if request.method == 'POST':
            rel, result = edit_addr_model(user_id, request)
            if rel:
                return render_template('userinfo/address.html', addr=result)
            else:
                flash('修改失败，请重试！')
                return redirect(request.url)

        _id = request.args.get('_id')
        result = get_addr_list_model(user_id)
        return render_template('userinfo/addressChange.html', addr=result)
    except IndexError as e:
        print('============addressChange IndexError============', e)
        flash("修改失败，请正确选择地址！")
        return redirect(request.url)
