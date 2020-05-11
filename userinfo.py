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
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import os

bp = Blueprint('userinfo', __name__)


# 用户信息页
@bp.route('/userinfo', methods=('GET', 'POST'))
@login_required
def userinfo():
    try:
        user = get_user(session.get('user_id'))
        return render_template('userinfo/userinfoBase.html', user=user)
    except Exception as e:
        print('============userinfo============', e)
        return redirect(request.referrer)


# 查询用户订单信息
def get_orders(user_id):
    result = ToMongo().get_col('order').find({'user_id': user_id, 'is_effective': 1})
    orders = []
    for order in result:
        amount = order['amount']
        order_no = order['order_no']
        create_time = order['create_time']
        effective_time = order['create_time'] + timedelta(days=1)
        books = order['books']
        book_info = []
        for book in books:
            book_num = book['book_num']
            book_info.append({'book_num': book_num, 'books': get_book(ObjectId(book['book_id']))})
        orders.append({'amount': amount, 'order_no': order_no, 'create_time': create_time, 'book_info': book_info,
                       'effective_time': effective_time})
    return orders


@bp.route('/test', methods=('GET', 'POST'))
def test():
    create_time = get_orders(5)
    return render_template('demo/endtime.html', create_time=create_time)


# 用户订单页
@bp.route('/userinfo/order', methods=('GET', 'POST'))
@login_required
def orders():
    try:
        user_id = session.get('user_id')
        orders = get_orders(user_id)
        return render_template('userinfo/orders.html', orders=orders)
    except Exception as e:
        print('============orders============', e)
        return redirect(request.referrer)


@bp.route('/userinfo/deleteOrder', methods=('GET', 'POST'))
@login_required
def deleteOrder():
    try:
        order_no = request.form.get('order_no')
        user_id = session.get('user_id')
        result = ToMongo().delete('order', {'order_no': order_no, 'user_id': user_id})
        if result.deleted_count:
            # 删除成功
            return jsonify(True)
        else:
            return jsonify(False)
    except Exception as e:
        print('============deleteOrder============', e)
        return redirect(url_for('userinfo.orders'))


@bp.route('/userinfo/deleteOrders', methods=('GET', 'POST'))
@login_required
def deleteOrders():
    try:
        orders_no = request.values.getlist('orders_no[]')
        user_id = session.get('user_id')
        db = ToMongo()
        count = 0
        for order_no in orders_no:
            result = db.delete('order', {'order_no': order_no, 'user_id': user_id}).deleted_count
            count += result
        if count == len(orders_no):
            # 删除成功
            return jsonify(True)
        else:
            return jsonify(False)
    except Exception as e:
        print('============deleteOrder============', e)
        return redirect(url_for('userinfo.orders'))


# 用户信息页
@bp.route('/userinfo/info', methods=('GET', 'POST'))
@login_required
def info():
    try:
        if request.method == 'POST':
            name = request.form.get('name')
            gender = request.form.get('gender')
            age = request.form.get('age')
            birthday = request.form.get('birthday')
            email = request.form.get('email')
            tel = request.form.get('tel')
            identity = request.form.get('identity')
            identity_select = request.form.get('identity_')
            hobbies = request.form.get('hobbies')
            introduce = request.form.get('introduce')
            user_id = session.get('user_id')
            # print('name:',name,'gender:',gender,'age:',age,'birthday:',birthday.split(' ')[0],'hobbies:',hobbies,'introduce:',introduce,
            #       'email:',email,'tel:',tel,'identity:',identity,'identity_select:',identity_select,'identity:',identity)
            conn = ToConn().to_execute()
            cur = conn.cursor()
            sql = 'update users set name=%s,gender=%s,age=%s,birthday=%s,email=%s,tel=%s,identity=%s,hobbies=%s,' \
                  'introduce=%s where id=%s'
            result = cur.execute(sql, (name, gender, age, birthday, email, tel, identity_select, hobbies,
                                       introduce, user_id))
            # print('=============result==============', result)
            if result:
                conn.commit()
                conn.close()
                # 更新成功返回更新后的用户信息
                return render_template('userinfo/info.html', user=get_user(session.get('user_id')))
            else:
                conn.rollback()
                conn.close()
                flash('修改错误！')
        # get请求
        return render_template('userinfo/info.html', user=get_user(session.get('user_id')))
    except Exception as e:
        # 出错，重定向到userinfo页
        print('============info============', e)
        return redirect(url_for('userinfo.userinfo'))


# 上传头像
@bp.route('/userinfo/inputAvatar', methods=('POST',))
@login_required
def inputAvatar():
    try:
        img = request.files['avatar']
        s_img = secure_filename(img.filename)
        img_suffix = s_img.split('.')[-1]
        user_id = session.get('user_id')
        # 随机文件名+后缀
        filepath = './static/images/avatar/' + str(user_id) + '.' + str(img_suffix)
        filename = filepath.split('/')[-1]
        img.save(filepath)
        conn = ToConn().to_execute()
        cur = conn.cursor()
        result = cur.execute('update users set avatar=%s where id=%s', (filename, user_id))
        if result:
            # 成功则提交
            conn.commit()
            conn.close()
        else:
            # 失败回滚
            flash("提交失败，请重试！")
            conn.rollback()
            conn.close()
        return render_template('userinfo/info.html', user=get_user(session.get('user_id')))
    except Exception as e:
        print('============inputAcatar============', e)
        # 出错，重定向到userinfo页
        return redirect(url_for('userinfo.userinfo'))


# 修改用户密码
@bp.route('/userinfo/changePW', methods=('GET', 'POST'))
@login_required
def changePW():
    try:
        old_pw = request.form.get('old_pw')
        new_pw = request.form.get('new_pw')
        confirm_pw = request.form.get('confirm_pw')
        user = get_user(session.get('user_id'))

        if new_pw != confirm_pw:
            flash("密码不一致！")
        elif not check_password_hash(user['password'], old_pw):
            flash("密码错误！")
        else:
            conn = ToConn().to_execute()
            cur = conn.cursor()
            sql = 'update users set password=%s where id=%s'
            result = cur.execute(sql, (generate_password_hash(new_pw), session.get('user_id')))
            if result:
                # 修改成功，提交
                conn.commit()
                conn.close()
            else:
                # 失败，回滚
                conn.rollback()
                conn.close()
                flash("修改失败，请重试！")
        session.clear()
        # print('========request.referrer=========', request.referrer)
        return render_template('user/login.html', next=request.referrer)
    except Exception as e:
        print('============change_pw============', e)
        # 出错，重定向到userinfo页
        flash("修改失败，请重试！")
        return redirect(url_for('userinfo.userinfo'))


# 收货地址页
@bp.route('/userinfo/address', methods=('GET', 'POST'))
@login_required
def address():
    try:
        # post请求
        if request.method == 'POST':
            user_id = session.get('user_id')
            name = request.form.get('name')
            tel = request.form.get('tel')
            province = request.form.get('province')
            city = request.form.get('city')
            details = request.form.get('details')
            _id = request.form.get('_id')
            result = ToMongo().insert('address',
                                      {'name': name, 'tel': tel, 'province': province, 'city': city, 'details': details,
                                       'user_id': user_id})
            if result.inserted_id:
                conn = ToConn().to_execute()
                cur = conn.cursor()
                r = cur.execute('update users set address_default=%s where id=%s', (str(result.inserted_id), user_id))
                if r:
                    conn.commit()
                    conn.close()
                    # render_template使用返回原来页面，form表单会重复提交，request.url=http://0.0.0.0:5000/userinfo/address
                    return redirect(request.url)
                else:
                    conn.rollback()
                    conn.close()
                    flash('操作失败，请重试！')
                    return redirect(request.url)
            else:
                flash('操作失败，请重试！')
                return redirect(request.url)
        # get请求
        user_id = session.get('user_id')
        result = ToMongo().get_col('address').find({'user_id': user_id})
        address_default = get_user(user_id)['address_default']
        return render_template('userinfo/address.html', addr=result, address_default=address_default)
    except Exception as e:
        print('============address============', e)
        return redirect(request.referrer)


# 删除收货地址
@bp.route('/userinfo/addressDelete', methods=('POST',))
@login_required
def addressDelete():
    try:
        _id = request.form.get('_id')
        user_id = session.get('user_id')
        if _id == get_user(user_id)['address_default']:
            # 如果是默认地址，删除默认地址
            conn = ToConn().to_execute()
            cur = conn.cursor()
            result = cur.execute('update users set address_default=null where id=%s', (user_id,))
            if result:
                conn.commit()
                conn.close()
            else:
                conn.rollback()
                conn.close()
                return jsonify(False)
        # 如果不是默认地址，直接删除默认地址
        db = ToMongo()
        count = db.delete('address', {'_id': ObjectId(_id)}).deleted_count
        if count:
            return jsonify(True)
        else:
            return jsonify(False)

    except Exception as e:
        print('============addressDelete============', e)
        return jsonify(result=False)


# 设为默认地址
@bp.route('/userinfo/addressDefault', methods=('POST',))
@login_required
def addressDefault():
    try:
        _id = request.form.get('_id')
        user_id = session.get('user_id')

        conn = ToConn().to_execute()
        cur = conn.cursor()
        result = cur.execute('update users set address_default=%s where id=%s', (_id, user_id))
        if result:
            conn.commit()
            conn.close()
            return jsonify(True)
        else:
            conn.rollback()
            conn.close()
            return jsonify(False)

    except Exception as e:
        print('============addressDelete============', e)
        return jsonify(result=False)


# 编辑更改收货人地址
@bp.route('/userinfo/addressChange', methods=('POST', 'GET'))
@login_required
def addressChange():
    try:
        # post请求
        if request.method == 'POST':
            name = request.form.get('name')
            tel = request.form.get('tel')
            province = request.form.get('province')
            city = request.form.get('city')
            details = request.form.get('details')
            _id = request.form.get('_id')
            result = ToMongo().update('address', {'_id': ObjectId(_id)},
                                      {"$set": {'name': name, 'tel': tel, 'province': province, 'city': city,
                                                'details': details}})
            if result.modified_count:
                user_id = session.get('user_id')
                result = ToMongo().get_col('address').find({'user_id': user_id})
                return render_template('userinfo/address.html', addr=result)
            else:
                flash('修改失败，请重试！')
                return redirect(request.url)

        # get请求
        _id = request.args.get('_id')
        user_id = session.get('user_id')
        result = ToMongo().get_col('address').find({'user_id': user_id, '_id': ObjectId(_id)})
        return render_template('userinfo/addressChange.html', addr=result)
    except Exception as e:
        print('============addressChange============', e)
        # 出错，重定向到userinfo页
        flash("修改失败，请重试！")
        return redirect(request.url)