import requests
from bs4 import BeautifulSoup
HEADER = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                        " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
          }


def get_ip_local(ip):
    resp = requests.get('https://api.binstd.com/ip/location?appkey=yourappkey&ip={}'.format(ip), headers=HEADER)
    print(resp.json())
    html = BeautifulSoup(resp.text, features="lxml")

    tab0_address = html.find('div', {'id': 'tab0_address'})
    result = tab0_address.text
    # 中国  浙江省 杭州市 阿里云
    # 中国  广西 来宾市 联通
    # 中国  广西 来宾市 移动
    if '市' in result:
        ret = result.strip().split(' ')[2]
        print(ret)
        return ret

if __name__ == '__main__':
    ip = '117.182.155.183'
    get_ip_local(ip)