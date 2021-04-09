import time
import logging
from threading import Thread
import requests
from bs4 import BeautifulSoup

from models import ToMongo

HEADER = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
          "Cookie":
'ddscreen=2; dest_area=country_id%3D9000%26province_id%3D111%26city_id%20%3D0%26district_id%3D0%26town_id%3D0; __permanent_id=20210407093124692211914694880966486; __rpm=%7Cmix_65152.403754%2C5294.3.1617759085978; secret_key=c4133a17d798d88fefae7302c086f8c9; __visit_id=20210407102703899112755253490753220; __out_refer=; __trace_id=20210407102703900109050708490941408; pos_6_start=1617762424393; pos_6_end=1617762424404'
          }

logging.basicConfig(filename='bs4_local.log',
                    level=logging.INFO,
                    format='%(asctime)s %(filename)s %(levelname)s %(message)s',
                    datefmt='%a %d %b %Y %H:%M:%S', )
CONN = ToMongo()


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
    # time.sleep(.1)
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
    # time.sleep(.1)
    h = BeautifulSoup(request.text, features="lxml")
    product_main_div = h.find('div', {'class': 'product_main'})

    title = h.find('h1')['title']
    subheading = h.find('h2').find('span', {'class': 'head_title_name'})['title'].strip()
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
        logging.exception('\n[get_book_detail]:值缺失{}：{}'.format(book_detail_url, e))
        raise KeyError('值缺失{}：{}'.format(book_detail_url, str(e)))
    return result


def get_a_page_book(second_type_url):
    try:
        book_first_page_60_urls, next_page_url = get_category_page_url(second_type_url)
    except Exception as e:
        logging.exception(
            "\n[get_category_page_url]:{}\n{}\n---------------------------------".format(second_type_url, e))
        return
    # 循环获取图书
    if not CONN.get_col('books').find_one({'title': list(book_first_page_60_urls.items())[-1][0]}):  # 跳过已有的
        for book_60_url in book_first_page_60_urls.values():
            try:
                book_info_dict = get_book_detail(book_60_url)
            except Exception as e:
                logging.exception("\n [get_book_detail]:{}\n{}".format(book_60_url, e))
                continue
            # 数据库操作
            if not CONN.get_col('books').find_one({'title': book_info_dict['title']}):
                result = CONN.get_col('books').insert(book_info_dict)
                print(result, book_60_url)
    # 有下一页
    if next_page_url:
        print(next_page_url)
        return
        # return get_a_page_book(next_page_url)
    else:
        return


def get_all_book_to_db(url='http://category.dangdang.com'):
    # 二分类URLs:{'影视写真': 'http://category.dangdang.com/cp01.01.13.00.00.00.html',...}
    classify_kind_detail_dict = get_category_url(url)
    # 循环获取二分类
    for second_type_name, second_type_url in classify_kind_detail_dict.items():
        # 递归
        if CONN.get_col('books').find_one({'second_type': second_type_name}):
            continue
        try:
            t = Thread(target=get_a_page_book, args=(second_type_url,))
            # t.daemon = True
            t.start()
            # t.join()
            # t.run()
            # get_a_page_book(second_type_url)
        except Exception as e:
            logging.exception(
                "\n[get_all_book_to_db]:{}\n{}\n".format(second_type_url, e))
    return '运行结束'


if __name__ == '__main__':
    try:
        r = get_all_book_to_db()
        content = """
        运行结束了！快去看看有多少吧！
        """
        logging.info('运行结束了！快去看看有多少吧！')
    except Exception as e:
        logging.exception('错误：{}'.format(e))
        r = '错误'
        content = e
    print(r)
    CONN.close_conn()
