import requests
import lxml.html as lh
from urllib.parse import urljoin
import time
import csv
import pymongo
from lxml import etree



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


def get_detail_url_list(url):
    """
    使用xpath获取url链接详情，返回url链接列表
    :param url:
    :return:
    """
    html = get_html(url)
    if not html:
        print("Requests Not 200 Start")
        return
    parser = lh.etree.HTML(html)
    detail_urls = [urljoin(url, i) for i in parser.xpath("//ul[contains(@class,'bigimg')]/li/a/@href")]
    return detail_urls


def parse_detail(url):
    """
    获取详细url页面下的内容，用xpath解析
    :param url:
    :return:
    """
    html = get_html(url)
    if not html:
        print("Response not 2 start")
        return
    Etree = etree.HTML(html)
    title = "".join(Etree.xpath("//div[@class='name_info']/h1/text()")).strip()
    subheading = "".join(Etree.xpath("//div[@class='name_info']/h2/span/text()")).strip()
    author = ''.join(Etree.xpath("//div[@class='messbox_info']/span[@id='author']/a/text()")).strip()
    press = ''.join(Etree.xpath("////div[@class='messbox_info']/span[@dd_name='出版社']/a/text()")).strip()
    pub_time = ''.join(Etree.xpath("////div[@class='messbox_info']/span[3]/text()")).strip()
    price = ''.join(Etree.xpath("//div[@class='price_pc']/div/div[@class='price_d']/p[@id='dd-price']/text()")).strip()
    price_m = ''.join(Etree.xpath("//div[@class='price_pc']/div/div[@class='price_m']/text()")).strip()

    ISBN = ''.join(Etree.xpath('//*[@id="detail_describe"]/ul/li[5]/text()')).strip()

    img_url = ''.join(Etree.xpath("//div[@class='pic']/a/img/@src"))

    return {'title':title, 'subheading':subheading, 'author':author, 'press':press,
            'pub_time':pub_time, 'price':price, 'price_m':price_m, 'img_url':img_url, 'ISBN':ISBN}


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


def write_csv(file_path, data):
    """
    保持为csv文件
    :param file_path:
    :param datas:
    :return:
    """
    with open(file=file_path, mode="a", encoding="utf8") as f:
        writer = csv.writer(f)
        lis = []
        for key, value in data.items():
            lis.append(value)
        writer.writerow(lis)


def spier():
    """
    循环获取所有页内容，保存到csv文件中
    :return:
    """
    url_AI = "http://category.dangdang.com/cp01.54.92.00.00.00.html"
    url_web = "http://category.dangdang.com/cp01.54.06.12.00.00.html"
    urls_AI = get_detail_url_list(url_AI)
    url_webs = get_detail_url_list(url_web)
    urls = urls_AI + url_webs
    db = ToMongo()
    for url in urls:
        data = parse_detail(url)
        print(data)
        db.insert(col='books', value=data)
        write_csv('./books.csv', data)



if __name__ == "__main__":
    start_time = time.time()
    spier()
    print("sum_time{}".format(time.time()-start_time))

