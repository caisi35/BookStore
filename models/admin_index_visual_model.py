from pyecharts import (
    WordCloud,
    Scatter,
    Pie,
    Bar,
)
from .admin_index_visual_data_model import (
    get_keyword,
    get_visits,
    get_price,
    get_hits_data,
    get_sales_data,
)


def keyword_wordcloud():
    wc = WordCloud('关键字搜索词云图', width=600)
    name, value = get_keyword()
    wc.add(name='Key Word', attr=name, value=value)
    return wc


def visits_pie_rose():
    """
    # 访问量饼图玫瑰图
    # https://blog.csdn.net/miner_zhu/article/details/81949004
    :return:
    """
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


def visits_scatter():
    """访问量散点图Scatter plot"""
    scatter = Scatter('访问量', width='100%')
    x, y = get_visits()
    # 坐标轴默认为数值轴，通过xaxis_type='category'修改
    scatter.add('', x_axis=x, y_axis=y, xaxis_type='category',
                is_visualmap=True, visual_type='size', visual_range_size=[10, 60],
                mark_point=['max', 'min'])
    return scatter


def inte_sales_stack():
    """绘制价格区间的图书数量和销售量堆叠图"""
    bar = Bar(title='价格与销量关系图', subtitle='x轴为图书价格区间', height=400, width=500, )
    book, sales, x = get_price()
    dic = {'xaxis_rotate': '45', 'is_toolbox_show': False, 'is_stack': True, 'legend_orient': 'vertical',
           'legend_pos': '70%', 'xaxis_name': '价格区间/元', 'xaxis_name_gap': '47'}
    bar.add('图书种类', x, book, **dic)
    bar.add('图书销量', x, sales, **dic)
    return bar


def hits_bar():
    """
    # 实例化 点击量的柱形图
    # 实例链接https://05x-docs.pyecharts.org/#/zh-cn/flask
    :return:
    """
    bar = Bar(title='点击量TOP 10', height=400, width=500)
    data_x, data_y = get_hits_data()
    bar.add('', data_x, data_y, xaxis_rotate=45, is_xaxis_show=False, is_toolbox_show=False)
    return bar


def sales_bar():
    bar = Bar(title='销售TOP 10', height=400, width=500)
    data_x, data_y = get_sales_data()
    bar.add('', data_x, data_y, xaxis_rotate=45, is_xaxis_show=False, is_toolbox_show=False)
    return bar
