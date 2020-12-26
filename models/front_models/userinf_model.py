from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from models import ToConn


def change_pwd_model(user_id, new_pw):
    rel = True
    conn = ToConn().to_execute()
    cur = conn.cursor()
    sql = 'update users set password=%s where id=%s'
    result = cur.execute(sql, (generate_password_hash(new_pw), user_id))
    if result:
        # 修改成功，提交
        conn.commit()
        conn.close()
    else:
        # 失败，回滚
        rel =False
        conn.rollback()
        conn.close()
    return rel

def upload_avatar_model(user_id, img):
    rel = True
    s_img = secure_filename(img.filename)
    img_suffix = s_img.split('.')[-1]
    # 随机文件名+后缀
    filepath = './static/images/avatar/' + str(user_id) + '.' + str(img_suffix)
    filename = filepath.split('/')[-1]
    img.save(filepath)
    conn = ToConn().to_execute()
    cur = conn.cursor()
    result = cur.execute('update users set avatar=%s where id=%s', (filename, user_id))
    if result:
        conn.commit()
        conn.close()
    else:
        rel = False
        conn.rollback()
        conn.close()
    return rel


def edit_userinfo_model(user_id, request):
    rel = True
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
    conn = ToConn().to_execute()
    cur = conn.cursor()
    sql = 'update users set name=%s,gender=%s,age=%s,birthday=%s,email=%s,tel=%s,identity=%s,hobbies=%s,' \
          'introduce=%s where id=%s'
    result = cur.execute(sql, (name, gender, age, birthday, email, tel, identity_select, hobbies,
                               introduce, user_id))
    if result:
        conn.commit()
        conn.close()
    else:
        rel = False
        conn.rollback()
        conn.close()
    return rel