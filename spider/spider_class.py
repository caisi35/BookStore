from bs4 import BeautifulSoup
from bs4 import UnicodeDammit
import urllib.request

from models import ToMongo


class Spider:
    headers = {"User-Agent":
                   "Mozilla/5.0 (Windows; U; Windows NT 6.0 "
                   "x64; en-US; rv:1.9pre)Gecko / 2008072421 Minefield / 3.0.2pre"}
    count = 0

    def load_img(self, start_url):
        try:
            urls = []
            req = urllib.request.Request(start_url, headers=self.headers)
            data = urllib.request.urlopen(req)
            data = data.read()
            dammit = UnicodeDammit(data, ['utf-8', 'gbk'])
            data = dammit.unicode_markup
            soup = BeautifulSoup(data, 'lxml')
            images = soup.select('img')
            for image in images:
                try:
                    src = image['src']
                    url = urllib.request.urljoin(start_url, src)
                    if url not in urls:
                        urls.append(url)
                        print(url)
                        self.download(url)
                except Exception as e:
                    print('============load_img1==========', e)
        except Exception as e:
            print('============load_img2==========', e)

    def download(self, url):
        try:
            self.count += 1
            if url[len(url) - 4] == '.':
                ext = url[len(url) - 4:]
            else:
                ext = ''
            req = urllib.request.Request(url, headers=self.headers)
            data = urllib.request.urlopen(req, timeout=100)
            data = data.read()
            fobj = open('./static/images/spider/' + str(self.count) + ext, 'wb')
            fobj.write(data)
            fobj.close()
            print('download' + str(self.count) + ext)
        except Exception as e:
            print('============download==========', e)

    def get_province(self, url):
        try:
            req = urllib.request.Request(url, headers=self.headers)
            data = urllib.request.urlopen(req)
            data = data.read()
            dammit = UnicodeDammit(data, ['utf-8', 'gbk'])
            data = dammit.unicode_markup
            soup = BeautifulSoup(data, 'lxml')
            province_navi = soup.find('div', attrs={'class': 'navi'})
            province_a = province_navi.find_all('a')
            province_dict = {}
            for a in province_a:
                if a.text:
                    province_dict[a.text] = urllib.request.urljoin('https://www.xzqy.net', a['href'])
            return province_dict
        except Exception as e:
            print('=========get_province========', e)

    def get_city(self, url):
        try:
            req = urllib.request.Request(url, headers=self.headers)
            data = urllib.request.urlopen(req)
            data = data.read()
            dammit = UnicodeDammit(data, ['utf-8', 'gbk'])
            data = dammit.unicode_markup
            soup = BeautifulSoup(data, 'lxml')
            table = soup.find('table')
            city = {}
            for i in table:
                i.find('td', attrs={'class': 'parent'})
                a = i.find('a')
                if a:
                    city[a.text] = urllib.request.urljoin('https://www.xzqy.net', a['href'])
            return city
        except Exception as e:
            print('==========get_city=======', e)

    def get_village(self, url):
        try:
            village = {}
            village_list = []
            req = urllib.request.Request(url, headers=self.headers)
            data = urllib.request.urlopen(req)
            data = data.read()
            dammit = UnicodeDammit(data, ['utf-8', 'gbk'])
            data = dammit.unicode_markup
            soup = BeautifulSoup(data, 'lxml')
            table = soup.find('table')
            tr = table.find('td', attrs={'class': 'parent'}).find('a')
            tr_child = table.find('td', attrs={'class': ''})
            a = tr_child.find_all('a')
            for i in a:
                village_list.append(i.text)
            village[tr.text] = village_list
            return village
        except Exception as e:
            print('==========get_village=======', e)

    def get_address(self):
        url = 'https://www.xzqy.net/451102000000.htm'
        province = self.get_province(url)
        address = {}
        for key, value in province.items():
            province_key = key
            city = self.get_city(value)
            for key, value in city.items():
                city_key = key
                district = self.get_city(value)
                for key, value in district.items():
                    district_key = key
                    address[province_key] = city_key
                    address[city_key] = district_key
                    address[district_key] = self.get_village(value)
        ToMongo().insert('address', address)
        return address
