import logging
import requests
from bs4 import BeautifulSoup
import time
import pymongo
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

my_sender = 'caisi-huang@139.com'  # 发件人邮箱账号
my_pass = 'Asdf17135'  # 发件人邮箱密码
my_user = 'caisi1735@163.com'  # 收件人邮箱账号，我这边发送给自己

HEADER = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                        " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"}
logging.basicConfig(filename='./dangdangbook3_bs4.log', level=logging.INFO)
CONN = pymongo.MongoClient(host='mongo', port=27017, username='root', password='root').get_database('bookstore')


def mail(title='', content=''):
    ret = True
    try:
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['From'] = formataddr(("Caisi", my_sender))  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To'] = formataddr(("To 163", my_user))  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = title  # 邮件的主题，也可以说是标题

        server = smtplib.SMTP("smtp.139.com", 25)  # 发件人邮箱中的SMTP服务器，端口是25
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(my_sender, [my_user, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
    except Exception as e:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        ret = False
        print(e)
    return ret


def get_category_url(category_url):
    """获取category_url分类页：分类URL"""
    request = requests.get(category_url, headers=HEADER)
    html = BeautifulSoup(request.text, features="lxml")
    div_floor_1 = html.find('div', {'id': 'floor_1'})
    classify_kind_div = div_floor_1.find_all('div', {'class': 'classify_kind'})
    # 获取大分类URL和text
    # classify_kind_div_dict = get_first_type(classify_kind_div)
    # 小分类URL和text
    classify_kind_detail_dict = get_second_type(classify_kind_div)
    return classify_kind_detail_dict


def get_second_type(classify_kind_divs):
    """获取二分类和大分类"""
    classify_kind_detail_dict = {}
    for classify_kind_div in classify_kind_divs:
        lis = classify_kind_div.find_all('li')
        for li in lis:
            a = li.find('a')
            if 'javascript' not in a['href']:
                a_href = a['href']
                a_text = a.text
                classify_kind_detail_dict[a_text] = a_href
    return classify_kind_detail_dict


def get_first_type(classify_kind_divs):
    """单独获取大分类"""
    classify_kind_div_dict = {}
    for classify_kind_div in classify_kind_divs:
        classify_kind_name_div = classify_kind_div.find('div', {'class': 'classify_kind_name'})
        classify_kind_name_div_a = classify_kind_name_div.find('a')
        classify_kind_name_div_a_href = classify_kind_name_div_a['href']
        classify_kind_name_div_a_text = classify_kind_name_div_a.text
        classify_kind_div_dict[classify_kind_name_div_a_text] = classify_kind_name_div_a_href
    return classify_kind_div_dict


def get_category_page_url(page_url):
    """
    获取图书首页60个的url 和 下一页的URL
    """
    request = requests.get(page_url, headers=HEADER)
    time.sleep(.1)
    h = BeautifulSoup(request.text, features="lxml")
    search_nature_rg_div = h.find('div', {'id': 'search_nature_rg'})
    lis = search_nature_rg_div.find_all('li')  # 60个
    book_detail_url_dict = {}
    for li in lis:
        a = li.find('a')
        a_url = a['href']
        a_title = a['title']
        book_detail_url_dict[a_title] = a_url

    # 下一页URL
    fy_ul = h.find('ul', {'name': 'Fy'})
    next_li = fy_ul.find('li', {'class': 'next'})
    next_a_url = next_li.find('a')
    next_url = ''
    if next_a_url.get('href'):
        index_url = page_url.rsplit('/', 1)[0]
        next_url = index_url + next_a_url.get('href')
    return book_detail_url_dict, next_url


def get_book_detail(book_detail_url):
    """获取图书信息"""
    request = requests.get(book_detail_url, headers=HEADER)
    time.sleep(.1)
    h = BeautifulSoup(request.text, features="lxml")
    product_main_div = h.find('div', {'class': 'product_main'})

    title = product_main_div.find('h1')['title']
    subheading = product_main_div.find('h2').find('span', {'class': 'head_title_name'})['title'].strip()
    messbox_info_div = product_main_div.find_all('div', {'class': 'messbox_info'})
    for t1_span in messbox_info_div:
        author = t1_span.find('span', {'id': 'author'}).find('a').text.strip()
        press = t1_span.find('span', {'dd_name': '出版社'}).find('a').text.strip()
        pub_time_3 = t1_span.find_all('span')[2].text.strip()
        pub_time = ''
        if "出版时间" in pub_time_3:
            pub_time = pub_time_3
    price = product_main_div.find('p', {'id': 'dd-price'}).text.replace('¥', '').strip()
    price_m = product_main_div.find('div', {'id': 'original-price'}).text.replace('¥', '').strip()
    # 详情
    detail_describe_div = h.find('div', {'id': 'detail_describe'})
    lis = detail_describe_div.find_all('li')
    for li in lis:
        if '开' in li.text:
            format = li.text.strip()  # 开本
        if '纸' in li.text:
            paper = li.text.strip()
        if '包' in li.text:
            packing = li.text.strip()
        if '套装' in li.text:
            suit = li.text.strip()
        if 'ISBN' in li.text:
            ISBN = li.text.strip()
        if li.find('span'):
            a_3s = li.find('span').find_all('a')
            first_type = a_3s[1].text.strip()
            second_type = a_3s[2].text.strip()
    # 图片
    main_img_slider_ul = product_main_div.find('ul', {'id': 'main-img-slider'})
    lis = main_img_slider_ul.find_all('li')
    img_urls = []
    for li in lis:
        img_url = li.find('img')['src'].strip().replace('_x_', '_w_')
        img_urls.append(img_url)

    create_time = int(time.time())
    try:
        result = {'title': title,
                  'subheading': subheading,
                  'author': author,
                  'press': press,
                  'pub_time': pub_time,
                  'price': float(price),
                  'price_m': float(price_m),
                  'img_url': img_urls[0],
                  'ISBN': ISBN,
                  'img_urls': img_urls,
                  'first_type': first_type,
                  'second_type': second_type,
                  'format': format,
                  'paper': paper,
                  'packing': packing,
                  'suit': suit,
                  'create_time': create_time,
                  'stock': 99,
                  'is_off_shelf': 0,
                  }
    except Exception as e:
        logging.exception('值缺失{}：{}'.format(book_detail_url, str(e)))
        print("\n---------------get_book_detail-------"
              "------------{}\n{}\n---------------------------------".format(book_detail_url, str(e)))
        raise KeyError('值缺失{}：{}'.format(book_detail_url, str(e)))
    return result


def get_a_page_book(second_type_url):
    try:
        book_first_page_60_urls, next_page_url = get_category_page_url(second_type_url)
    except Exception as e:
        logging.exception(
            "\n\n-----------------get_category_page_url-----"
            "------------{}\n{}\n---------------------------------".format(e, second_type_url))
        print("\n\n---------------get_category_page_url-------------------{}\n{}\n---------------------------------"
              .format(e, second_type_url))
        return
    # 循环获取图书
    for book_60_url in book_first_page_60_urls.values():
        try:
            book_info_dict = get_book_detail(book_60_url)
        except Exception as e:
            print("\n\n---------------get_book_detail-------------------{}\n{}\n\n---------------------------------"
                  .format(e, second_type_url))
            return
        # 数据库操作
        CONN.get_collection('book2').insert(book_info_dict)
        time.sleep(.1)

    # 有下一页
    if next_page_url:
        return get_a_page_book(next_page_url)


def get_all_book_to_db(url='http://category.dangdang.com'):
    # 二分类URLs:{'影视写真': 'http://category.dangdang.com/cp01.01.13.00.00.00.html',...}
    classify_kind_detail_dict = get_category_url(url)

    # 循环获取二分类
    for second_type_name, second_type_url in classify_kind_detail_dict.items():
        # 递归
        try:
            get_a_page_book(second_type_url)
        except Exception as e:
            logging.exception(
                "\n\n---------------get_all_book_to_db-------------------{}\n{}\n\n---------------------------------"
                    .format(e, second_type_url))
            print(
                "\n\n---------------get_all_book_to_db-------------------{}\n{}\n\n---------------------------------"
                    .format(e, second_type_url))
    return '运行结束'


if __name__ == '__main__':
    try:
        r = get_all_book_to_db()
    except Exception as e:
        logging.exception('错误：{}'.format(str(e)))
        mail('爬虫反馈', '错误：{}'.format(str(e)))
        r = '错误'
    mail(title=r, content=r)
