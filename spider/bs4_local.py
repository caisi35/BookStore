import time
import logging
from threading import Thread
import requests
from bs4 import BeautifulSoup

from models import ToMongo

HEADER = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
          "Cookie":
'__permanent_id=20200407140949670150821382601373490; MDD_channelId=70000; MDD_fromPlatform=307; producthistoryid=26918687%2C26921715%2C23761145%2C28522755%2C28529343%2C25223949%2C25066760%2C25060153%2C28507618%2C24175371; permanent_key=2020041220492885766069876648db03; dangdang.com=email=QjE3MkM3NkYyMzYxQ0M5Q0Q3RjBAcXFfdXNlci5jb20=&nickname=Q2Fpc2k=&display_id=5795980493976&customerid=wptIUOGVbX4y8FQdFsqIuA==&viptype=&show_name=134%2A%2A%2A%2A0145; ddoy=email=B172C76F2361CC9CD7F0%40qq_user.com&nickname=Caisi&validatedflag=0&agree_date=1; LOGIN_TIME=1617589198527; cto_bundle=4l9fiV9KNzdkcWRaJTJCRndHSlBMTFBCbGV6aTl2Wk1NcG9XYWg5SkphcldWSiUyQldxNVJCN2ZUUndySyUyRm9OWnoyU3FWZDExeGNsTVJSejdvUFBENlNEejF6cWVTS1I0b3RVaTRpdm5wZWp2bmdSQUtMcFI0d213d2tFMG5pNlNVaUxTb3h0TGhWZHg4QyUyQkFsenJCSzZ2d1h5N09tYTd4Y1R5ZCUyRk9uSzY4NUtRdGNTSzg0JTNE; dest_area=country_id%3D9000%26province_id%3D145%26city_id%3D14511%26district_id%3D1451101%26town_id%3D145110108; secret_key=eeb2cd770f27797682722c28f1723261; __visit_id=20210405101944233379483171559469013; __out_refer=; __trace_id=20210405102014623200832524605987673; __dd_token_id=20210405101944833026637963796510; alipay_request_from=https://login.dangdang.com/signin.aspx?returnurl=http%253A%252F%252Fproduct.dangdang.com%252F28518072.html; login.dangdang.com=.AYH=2021040510194504459319145&.ASPXAUTH=KNGa04c5vkeU+ORTFzjvmvlLFQSEz5/6KORz1tYp3d0IUcMvY00G/w==; __rpm=%7Clogin_page.login_password_div..1617589188591; sessionID=pc_dac295cd97cc42761f53fc9e1cc60dcbffae11bf58b5b174ca2fe19e84a0f266; order_follow_source=-%7C-O-123%7C%2311%7C%23login_third_qq%7C%230%7C%23; ddscreen=2; pos_6_start=1617589198715; pos_6_end=1617589198737'          }
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
                print(result)

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
        try:
            print(second_type_name)
            t = Thread(target=get_a_page_book, args=(second_type_url,))
            # t.daemon = True
            # t.start()
            # t.join()
            t.run()
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
