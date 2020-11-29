import requests
from lxml import html as hl
from bs4 import BeautifulSoup
import csv
import time
import pymongo

header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                            " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"}


def get_sub_url():
    """
    获取大分类
    :return: {分类名称：urll，.....，}
    """
    try:
        request = requests.get('http://book.dangdang.com/', headers=header)
        # request.encoding = 'utf-8'
        h = BeautifulSoup(request.text, features="lxml")
        # print(h)
        sub = h.find('div', {'class': 'sub'})
        a = sub.find_all('a')
        urls = {}
        for a in a:
            urls[a.text] = a['href']
        return urls
    except:
        return {}

def get_two_urls(first_url):
    """
    获取小分类的url
    :param first_url: 大分类的url
    :return: {小分类名称：urll，.....，}
    """
    request = requests.get(first_url, headers=header)
    h = BeautifulSoup(request.text, features="lxml")
    primary_dl = h.find_all('dl', {'class': 'primary_dl'})
    urls = {}
    try:
        for dl in primary_dl:
            dt = dl.find('dt')
            url = dt.find('a')['href']
            text = dt.find('a').text
            text = text.replace(' ', '')
            urls[text] = url
    except Exception as e:
        print('error%s'%e)
    return urls


def get_detail_url(url):
    """
    获取图书详情页url
    :param url: 小分类的url
    :return: {图书标题：url，.....，},下一页的url
    """
    request = requests.get(url, headers=header)
    h = BeautifulSoup(request.text, features="lxml")
    ul = h.find('ul', {'id': 'component_59'})
    lis = ul.find_all('li')
    urls = {}
    try:
        for li in lis:
            a = li.find('a')
            a_url = a['href']
            a_title = a['title']
            urls[a_title] = a_url
        next_url = h.find('li', {'class': 'next'}).find('a')['href']
        start_url = 'http://category.dangdang.com'
        next_url = start_url+next_url
    except Exception as e:
        print('Error%s'%e)
    return urls


def get_html(url):
    """
    获取html页面
    User-Agent：检查->Network->Preserve log->**.html->Headers->User-Agent
    :param url:
    :return:
    """
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                            " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"}
    response = requests.get(url, headers=header)
    return response.text if str(response.status_code).startswith("2") else None


def parse_detail_info(url):
    """
    获取详细url页面下的内容，用xpath解析
    :param url:
    :return:
    """
    html = get_html(url)
    if not html:
        print("Response not 2 start")
        return
    try:
        Etree = hl.etree.HTML(html)
        title = "".join(Etree.xpath("//div[@class='name_info']/h1/text()")).strip()
        subheading = "".join(Etree.xpath("//div[@class='name_info']/h2/span/text()")).strip()
        author = ''.join(Etree.xpath("//div[@class='messbox_info']/span[@id='author']/a/text()")).strip()
        press = ''.join(Etree.xpath("////div[@class='messbox_info']/span[@dd_name='出版社']/a/text()")).strip()
        pub_time = ''.join(Etree.xpath("////div[@class='messbox_info']/span[3]/text()")).strip()
        price = ''.join(Etree.xpath("//div[@class='price_pc']/div/div[@class='price_d']/p[@id='dd-price']/text()")).strip()
        price_m = ''.join(Etree.xpath("//div[@class='price_pc']/div/div[@class='price_m']/text()")).strip()
        img_url = ''.join(Etree.xpath("//div[@class='pic']/a/img/@src"))
        ISBN = ''.join(Etree.xpath('//*[@id="detail_describe"]/ul/li[5]/text()')).strip()

        return {'title':title, 'subheading':subheading, 'author':author, 'press':press,
                'pub_time':pub_time, 'price':float(price), 'price_m':float(price_m), 'img_url':img_url, 'ISBN': ISBN}
    except Exception as e:
        print('Error%s'%e)
        return {}


def write_csv(file_path, data):
    """
    保持为csv文件
    :param file_path:
    :param datas:
    :return:
    """
    with open(file=file_path, mode="a", encoding="utf-8") as f:
        writer = csv.writer(f)
        lis = []
        try:
            for key, value in data.items():
                lis.append(value)
            writer.writerow(lis)
        except Exception as e:
            print('Error%s'%e)


class ToMongo:
    def __init__(self):
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        self.mydb = myclient['products']

    def insert(self, col, value):
        """
        插入新数据
        :param col: 插入的集合名称
        :param value: 插入的数据值
        :return: 返回插入结果
        """
        try:
            mycol = self.mydb[col]
            if type(value) == dict:
                result = mycol.insert_one(value)
            else:
                result = mycol.insert_many(value)
            return result
        except Exception as e:
            print('==============================\n', e)


def get_books():

    db = ToMongo()
    for sub_name, sub_url in get_sub_url().items():
        print(sub_name)
        time.sleep(0.5)
        for two_name, two_url in get_two_urls(sub_url).items():
            print(two_name)
            time.sleep(1)
            for book_title, book_detail_url in get_detail_url(two_url).items():
                time.sleep(0.5)
                print(sub_name, two_name, book_title)
                try:
                    book = parse_detail_info(book_detail_url)
                    book['type'] = sub_name
                    book['category'] = two_name
                    book['is_off_shelf'] = 0
                    db.insert(col='newbooks', value=book)
                    write_csv(r'./data/books.csv', book)
                except Exception as e:
                    print('Error%s'%e)
                    continue


get_books()

