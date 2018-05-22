import json
import os
import re
from hashlib import md5
from multiprocessing.pool import Pool
from urllib.parse import urlencode

import pymongo
import requests
from bs4 import BeautifulSoup
from requests import RequestException

from config.config import *

client = pymongo.MongoClient(MONGO_URL, connect=False)
db = client[MONGO_DB]


def get_page_index(offset, keyword):
    '''
        获取索引页信息
    :param offset: 起始页
    :param keyword: 搜索关键字
    :return:
    '''
    data = {
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': '20',
        'cur_tab': '1',
        'from': 'search_tab'
    }

    url = 'https://www.toutiao.com/search_content/?' + urlencode(data)
    return get(url)


def get(url, resourceType='HTML'):
    '''
        请求资源
    :param url: 请求路径
    :param resourceType: 资源类型
    :return:
        请求结果
    '''
    cookie = {
        'CNZZDATA1259612802': '1709103399-1526899528-https%253A%252F%252Fwww.baidu.com%252F%7C1526904961',
        'UM_distinctid': '1638273f577506-0c474b93935793-336d7705-fa000-1638273f578308',
        'WEATHER_CITY': '%E5%8C%97%E4%BA%AC',
        '__tasessionId': '48igss5x01526906181955',
        'atpsida': 'e7a22e14a37217e916205802_1526902092_5',
        'cna': 'C5uJE2B8SSsCAd9JO30rRIqO',
        'sca': 'abca8d2c',
        'tt_webid': '6557994269901161992',
        'uuid': 'w:42b304308d934ca3a4a53851b2089e3e'

    }
    header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"
    }

    try:
        respone = requests.get(url=url, cookies=cookie, headers=header)
        if (respone.status_code == 200):
            if (resourceType == 'IMG'):
                return respone.content
            else:
                return respone.text
        return None
    except RequestException:
        return None


def parse_page_index(result):
    '''
        解析索引页
    :param result:
    :return:  详情页url
    '''
    try:
        data = json.loads(result)
        if data and 'data' in data.keys():
            for item in data.get('data'):
                yield item.get("article_url")
    except Exception:
        pass


def parse_page_detail(url):
    '''
        使用BeautifulSoup解析详情页
    :param respone:
    :return:
    '''
    respone = get(url)
    if not respone:
        return None
    try:
        soup = BeautifulSoup(respone, 'lxml')
        title = soup.select('title')[0].get_text()
        pattern = re.compile('.*?gallery: JSON.parse\("(.*?)"\)', re.S)
        result = re.search(pattern, respone)
        if result:
            json_info = result.group(1).replace('\\', '').replace('\\\\', '')
            # print(json_info)
            gallery = json.loads(json_info)
            if gallery and 'sub_images' in gallery.keys():
                sub_images = gallery.get('sub_images')
                # print('=========')
                # print(sub_images)
                image_url_list = [item.get('url') for item in sub_images]
                for image_url in image_url_list: download_image(image_url)
                yield {
                    'title': title,
                    'url': url,
                    'images': image_url_list
                }

    except Exception:
        pass


def save(record):
    '''
        保存记录到MongoDB
    :param record:
    :return:
    '''
    if db[TOUTIAO_TABLE].insert(record):
        print("保存【" + record.get('url') + "】")
        return True
    return False


def download_image(url):
    '''
        保存图片，图片名用MD5对内容加密，防止重复下载
    :param url:
    :return:
    '''
    content = get(url, 'IMG')
    img_root = os.getcwd() + os.path.sep + "img"
    if not os.path.exists(img_root):
        os.mkdir(img_root)
    path = '{0}/{1}.{2}'.format(img_root, md5(content).hexdigest(), 'JPG')
    if not os.path.exists(path):
        with open(path, 'wb') as f:
            print('下载【' + url + "】")
            f.write(content)
            f.close()


def handle(offset):
    '''
        处理业务逻辑
    :return:
    '''
    result = get_page_index(offset, TOUTIAO_KEYWORD)
    data = parse_page_index(result)
    for url in data:
        items = parse_page_detail(url)
        for item in items:
            save(item)


if __name__ == '__main__':
    groups = [x * 20 for x in range(TOUTIAO_PAGE_START, TOUTIAO_PAGE_END)]
    pool = Pool()
    pool.map(handle, groups)
