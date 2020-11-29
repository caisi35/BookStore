from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from models.db import ToConn, ToMongo, get_trash, get_page
from views_admin.signIn import admin_login_required
from werkzeug.exceptions import abort
from bson.objectid import ObjectId
from pyecharts import Bar, Scatter, Pie, WordCloud
import pymongo
import datetime
import collections

bp = Blueprint('admin', __name__, url_prefix='/admin')
REMOTE_HOST = "/static/assets/js"


# 管理主页
@bp.route('/', methods=('GET', 'POST'))
@admin_login_required
def admin():
    try:
        visitsscatter = visits_scatter()
        visits_pie = visits_pie_rose()
        bar = hits_bar()
        sales = sales_bar()
        inte_sales_bar = inte_sales_stack()
        kw_wc = keyword_wordcloud()

        return render_template('admin/indexBase.html',
                               myvisitsscatter=visitsscatter.render_embed(),
                               myvisits_pie=visits_pie.render_embed(),

                               myhitsbar=bar.render_embed(),
                               script_list_bar=bar.get_js_dependencies(),

                               mysalesbar=sales.render_embed(),
                               myinte_sales=inte_sales_bar.render_embed(),

                               mykw_wc=kw_wc.render_embed(),
                               script_list_kw_wc=kw_wc.get_js_dependencies(),
                               host=REMOTE_HOST,
                               )
    except Exception as e:
        print('==============Admin login=================', e)
        return 'Error:' + str(e)


def get_keyword():
    """
    获取搜索关键词数据
    :return:
    """
    kw = ToMongo().get_col('keyword').find({}, {'_id': 0})
    key = []
    value = []
    for k, v in list(kw)[0].items():
        key.append(k)
        value.append(v)
    return key, value


def keyword_wordcloud():
    wc = WordCloud('关键字搜索词云图', width=600)
    name, value = get_keyword()
    wc.add(name='Key Word', attr=name, value=value)
    return wc


# 获取访问量
def get_visits():
    col = ToMongo().get_col('visits')
    # 获取30天的时间差
    date = (datetime.datetime.now() - datetime.timedelta(days=30))
    # 查询大于时间差的数据
    data = list(col.find({'date': {'$gte': date}}))
    # https://blog.csdn.net/qq_42184799/article/details/86311804
    # collections.OrderedDict()字典按插入顺序排序
    day_list = collections.OrderedDict()
    # 获取时间列表['04-25', '04-26', '04-27', '04-28']
    for i in range(0, 31):
        day = date.strftime("%m-%d")
        day_list[day] = 0
        date = date + datetime.timedelta(days=1)

    for d in data:
        d_farmat = d['date'].strftime("%m-%d")
        if d_farmat in day_list:
            day_list[d_farmat] = len(d['users_id'])
    x = []
    y = []
    for k, v in day_list.items():
        x.append(k)
        y.append(v)
    return x, y


# 访问量饼图玫瑰图
# https://blog.csdn.net/miner_zhu/article/details/81949004
def visits_pie_rose():
    pie = Pie('访问量', width='100%')
    x, y = get_visits()

    # abel_formatter -> str
    # 模板变量有
    # {a}, {b}，{c}，{d}，{e}，分别表示系列名，数据名，数据值等
    pie.add('', x, y, radius=[30, 80], rosetype='area', visual_range_size=1,
            is_legend_show=False, is_label_show=True, label_pos='inside',
            label_formatter='{c}')
    pie.add('', attr=[1], value=[1], radius=[29, 30], rosetype='area', is_legend_show=False)
    return pie


# 访问量散点图Scatter plot
def visits_scatter():
    scatter = Scatter('访问量', width='100%')
    x, y = get_visits()
    # 坐标轴默认为数值轴，通过xaxis_type='category'修改
    scatter.add('', x_axis=x, y_axis=y, xaxis_type='category',
                is_visualmap=True, visual_type='size', visual_range_size=[10, 60],
                mark_point=['max', 'min'])
    return scatter


# 获取价格区间
def get_n_avg(min, max):
    list = [min, max]

    list.insert(1, list[0] / 2 + list[1] / 2)
    list.insert(1, list[0] / 2 + list[1] / 2)
    list.insert(-1, list[-1] / 2 + list[-2] / 2)
    list.insert(1, list[0] / 2 + list[1] / 2)
    list.insert(-1, list[-1] / 2 + list[-2] / 2)
    list.insert(3, list[2] / 2 + list[3] / 2)
    list.insert(5, list[4] / 2 + list[5] / 2)

    for i in range(1, len(list) - 1):
        list[i] = int(list[i])
    area_list = []
    for i in range(len(list) - 1):
        area_list.append([list[i], list[i + 1]])
    return area_list


# https://cloud.tencent.com/developer/article/1406368
# 字符串转为数值
# https://www.jb51.net/article/98385.htm
# aggregate查询同字段的区间值
def get_price():
    pipeline = [
        {'$group': {'_id': "", 'max': {'$max': '$price'}, 'min': {'$min': '$price'}}},
    ]
    max_min = list(ToMongo().get_col('books').aggregate(pipeline))
    max = max_min[0]['max']
    min = max_min[0]['min']
    list_n = get_n_avg(min, max)
    book_num = []
    sales_num = []
    for i in list_n:
        # print(i[0],i[1])
        if i[1] != max:
            qurey = [{'$match': {'price': {'$gte': i[0], '$lt': i[1]}}}, {'$sort': {'price': -1}}]
            r = ToMongo().get_col('books').aggregate(qurey)
        else:
            qurey = [{'$match': {'price': {'$gte': i[0], '$lte': i[1]}}}, {'$sort': {'price': -1}}]
            r = ToMongo().get_col('books').aggregate(qurey)
        r = list(r)
        book_num.append(len(r))

        sales = 0
        for i in r:
            try:
                if i['sales']:
                    sales = sales + i['sales']
            except:
                pass
        sales_num.append(sales)
    return book_num, sales_num, list_n


# 绘制价格区间的图书数量和销售量堆叠图
def inte_sales_stack():
    bar = Bar(title='价格与销量关系图', subtitle='x轴为图书价格区间', height=400, width=500, )
    book, sales, x = get_price()
    dic = {'xaxis_rotate': '45', 'is_toolbox_show': False, 'is_stack': True, 'legend_orient': 'vertical',
           'legend_pos': '70%', 'xaxis_name': '价格区间/元', 'xaxis_name_gap': '47'}
    bar.add('图书种类', x, book, **dic)
    bar.add('图书销量', x, sales, **dic)
    return bar


# 获取点击量hits的数据
def get_hits_data():
    data = ToMongo().get_col('books').find({'hits': {'$gt': 0}}).sort('hits', pymongo.DESCENDING).limit(10)
    data_x = []
    data_y = []
    for i in data:
        data_x.append(i['title'])
        data_y.append(i['hits'])
    return data_x, data_y


# 实例化 点击量的柱形图
# 实例链接https://05x-docs.pyecharts.org/#/zh-cn/flask
def hits_bar():
    bar = Bar(title='点击量TOP 10', height=400, width=500)
    data_x, data_y = get_hits_data()
    bar.add('', data_x, data_y, xaxis_rotate=45, is_xaxis_show=False, is_toolbox_show=False)
    return bar


def sales_bar():
    bar = Bar(title='销售TOP 10', height=400, width=500)
    data_x, data_y = get_sales_data()
    bar.add('', data_x, data_y, xaxis_rotate=45, is_xaxis_show=False, is_toolbox_show=False)
    return bar


# 获取销售量sales的数据
def get_sales_data():
    data = ToMongo().get_col('books').find({'sales': {'$gt': 0}}).sort('sales', pymongo.DESCENDING).limit(10)
    data_x = []
    data_y = []
    for i in data:
        data_x.append(i['title'])
        data_y.append(i['sales'])
    return data_x, data_y


# 回收站
@bp.route('/book_trash', methods=('GET', 'POST'))
@admin_login_required
def book_trash():
    try:
        page = request.args.get('page', 1, int)
        page_size = 20
        page_count = 5
        if page == 1:
            # 请求为默认的第一页
            books = ToMongo().get_col('trash').find().limit(page_size)
        else:
            books = ToMongo().get_col('trash').find().skip((page - 1) * page_size).limit(page_size)
        total = ToMongo().get_col('trash').find().count()
        return render_template('admin/trash.html',
                               books=list(books),
                               active_page=page,
                               page_size=page_size,
                               page_count=page_count,
                               total=total,
                               trash_type='/admin/book_trash?page='
                               )
    except Exception as e:
        print('==============Admin book_trash=================', e)
        return 'Error:' + str(e)


@bp.route('/user_trash', methods=('GET', 'POST'))
@admin_login_required
def user_trash():
    try:
        page = request.args.get('page', 1, int)
        page_size = 20
        page_count = 5
        if page == 1:
            # 请求为默认的第一页
            users = ToConn().get_db('select * from users where is_delete=1 limit %s', (page_size))
        else:
            users = ToConn().get_db('select * from users where is_delete=1 limit %s,%s',
                                    ((page - 1) * page_size, page_size))
        total = ToConn().get_db('select count(*) from users where is_delete=1').fetchone().get('count(*)')
        return render_template('admin/trash.html',
                               users=users,
                               page_size=page_size,
                               page_count=page_count,
                               total=total,
                               active_page=page,
                               trash_type='/admin/user_trash?page=',
                               )
    except Exception as e:
        print('==============Admin user_trash=================', e)
        return 'Error:' + str(e)


# 还原图书
@bp.route('/restores', methods=('GET', 'POST'))
@admin_login_required
def restores():
    try:
        book_id = request.args.get('book_id')
        book = ToMongo().get_col('trash').find_one({'_id': ObjectId(book_id)})
        result = ToMongo().insert('books', book)
        ds = ToMongo().delete('trash', {'_id': ObjectId(book_id)})
        if ds.deleted_count and result.inserted_id:
            return redirect(url_for('admin.trash'))
        else:
            flash('操作失败！')
            return redirect(url_for('admin.trash'))
    except Exception as e:
        print('=========book Admin restores=========', e)
        return abort(404)


# 还原用户
@bp.route('/restores_user', methods=('GET', 'POST'))
@admin_login_required
def restores_user():
    try:
        user_id = request.args.get('user_id')
        conn = ToConn().to_execute()
        result = conn.cursor().execute('update users set is_delete=0 where id=%s', (user_id,))
        if result:
            conn.commit()
            return redirect(url_for('admin.user_trash'))
        else:
            conn.rollback()
            flash('操作失败！')
            return redirect(url_for('admin.user_trash'))
    except Exception as e:
        print('=========book Admin restores_user=========', e)
        return abort(404)


# 删除图书
@bp.route('/trash_delete', methods=('GET', 'POST'))
@admin_login_required
def trash_delete():
    try:
        book_id = request.args.get('book_id')
        result = ToMongo().delete('trash', {'_id': ObjectId(book_id)})
        if result.modified_count:
            return redirect(url_for('admin.trash'))
        else:
            flash('操作失败！')
            return redirect(url_for('admin.trash'))
    except Exception as e:
        print('=========book Admin trash_delete=========', e)
        return abort(404)
