import logging
from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, session, jsonify, abort
)
from views_front.user import login_required
from views_front.products import get_user
from werkzeug.security import check_password_hash
from models.front_models import (
    edit_userinfo_model,
    upload_avatar_model,
    change_pwd_model,
    get_user_addr_info,
    get_addr_list_model,
    delete_addr_model,
    set_default_addr_model,
    edit_addr_model,
    get_addr_info,
    get_user_collections,
    to_delete_collection,
    get_history_model,
    clear_history_model,
)
from utils import Logger

Logger('userinfo.log')
bp = Blueprint('userinfo', __name__, url_prefix='/userInfo')


@bp.route('/', methods=('GET', 'POST'))
@login_required
def userinfo():
    """用户信息页"""
    user = get_user(session.get('user_id'))
    return render_template('front/user_info_manage/base_user_info.html',
                           user=user,
                           active_nav='me')


@bp.route('/get_history')
@login_required
def get_history():
    user_id = session.get('user_id')
    try:
        items = get_history_model(user_id)
    except Exception as e:
        logging.exception('[get_history]:[%s]\n[%s]' % (user_id, e))
        return abort(500)
    return render_template('front/user_info_manage/history.html',
                           items=items,
                           active_nav='history')


@bp.route('/clear_history')
@login_required
def clear_history():
    user_id = session.get('user_id')
    try:
        result = clear_history_model(user_id)
    except Exception as e:
        logging.exception('[clear_history]:[%s]\n[%s]' % (user_id, e))
        flash('出错了，请稍后再试～')
        return abort(500)
    if not result:
        flash('出错了，请稍后再试～')
    return redirect(url_for('userinfo.get_history'))


@bp.route('/collection')
@login_required
def collection():
    user_id = session.get('user_id')

    try:
        collections = get_user_collections(user_id)
    except Exception as e:
        logging.exception('[collection exception][%s]:\n[%s]' % (user_id, e))
        return abort(500)
    return render_template('front/user_info_manage/collection.html',
                           collections=collections,
                           active_nav='collection',)


@bp.route('/delete_collection', methods=['POST'])
@login_required
def delete_collection():
    ids = request.form.getlist('collection_ids[]')
    user_id = session.get('user_id')
    rel = False
    try:
        rel = to_delete_collection(user_id, ids)
    except Exception as e:
        logging.exception('[delete_collection]:[%s]\n[%s]' % (user_id, e))
    return jsonify(rel)


@bp.route('/info', methods=('GET', 'POST'))
@login_required
def info():
    """用户信息页"""
    try:
        user_id = session.get('user_id')
        if request.method == 'POST':
            result = edit_userinfo_model(user_id, request)
            if result:
                # 更新成功返回更新后的用户信息
                return render_template('front/user_info_manage/info.html', user=get_user(user_id))
            else:
                flash('修改错误！')
        user_info = get_user(user_id)
        logging.info('%s info:[%s]', user_id, user_info)
        return render_template('front/user_info_manage/info.html',
                               user=user_info,
                               active_nav='info')
    except Exception as e:
        logging.exception('info:[%s]', str(e))
        return redirect(url_for('userinfo.userinfo'))


@bp.route('/inputAvatar', methods=('POST',))
@login_required
def inputAvatar():
    """上传头像"""
    try:
        img = request.files['avatar']
        user_id = session.get('user_id')
        result = upload_avatar_model(user_id, img)
        if not result:
            flash("提交失败，请重试！")
        return render_template('front/user_info_manage/info.html',
                               user=get_user(user_id),
                               active_nav='info')
    except Exception as e:
        logging.exception('inputAcatar:[%s]', str(e))
        # 出错，重定向到userinfo页
        return redirect(url_for('userinfo.userinfo'))


@bp.route('/changePW', methods=('GET', 'POST'))
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
        return render_template('front/user_login_register/login.html',
                               next=request.referrer)
    except Exception as e:
        logging.exception('change_pw:[%s]', str(e))
        flash("修改失败，请重试！")
        return redirect(url_for('userinfo.userinfo'))


@bp.route('/address', methods=('GET', 'POST'))
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
        return render_template('front/user_info_manage/address.html',
                               addr=list(result),
                               address_default=address_default,
                               active_nav='address')
    except Exception as e:
        logging.exception('address:[%s]', str(e))
        return redirect(request.referrer)


@bp.route('/addressDelete', methods=('POST',))
@login_required
def addressDelete():
    """删除收货地址"""
    try:
        _id = request.form.get('_id')
        user_id = session.get('user_id')
        rel = delete_addr_model(user_id, _id)
        return jsonify(rel)
    except Exception as e:
        logging.exception('addressDelete:[%s]', str(e))
        return jsonify(result=False)


@bp.route('/addressDefault', methods=('POST',))
@login_required
def addressDefault():
    """设为默认地址"""
    try:
        _id = request.form.get('_id')
        user_id = session.get('user_id')
        rel = set_default_addr_model(user_id, _id)
        logging.info('%s set default address is:%s-[set result:%s]', user_id, _id, rel)
        return jsonify(rel)
    except Exception as e:
        logging.exception('addressDefault:[%s]', str(e))
    return jsonify(result=False)


@bp.route('/address_change', methods=('POST', 'GET'))
@login_required
def address_change():
    """编辑更改收货人地址"""
    try:
        user_id = session.get('user_id')
        if request.method == 'POST':
            rel, result = edit_addr_model(user_id, request)
            if rel:
                return redirect(url_for('userinfo.address'))
            else:
                flash('修改失败，请重试！')
                return redirect(request.url)

        _id = request.args.get('_id')
        result = get_addr_info(_id)
        return render_template('front/user_info_manage/address_change.html',
                               addr=result,
                               active_nav='address')
    except IndexError as e:
        logging.exception('address_change:[%s]', str(e))
        flash("修改失败，请正确选择地址！")
        return redirect(request.url)
