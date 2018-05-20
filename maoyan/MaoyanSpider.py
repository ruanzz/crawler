import json
import re
import time
from multiprocessing.pool import Pool

import requests
from requests import RequestException


def get_one_page(url):
    '''
        请求单个页面
    :return: 请求HTML返回的内容
    '''
    cookie = {
        "uuid": "1A6E888B4A4B29B16FBA1299108DBE9CD560960E0F404849BAAA5AF18C61519A",
        "_csrf": "a1594da34f4adc254a8324f07d73290a7956becef98b7a4a9acd0c539d9095d2",
        "_lxsdk_cuid": "1637d809548c8-0c8dbd954e2342-336d7705-fa000-1637d809549c8",
        "_lxsdk": "1A6E888B4A4B29B16FBA1299108DBE9CD560960E0F404849BAAA5AF18C61519A",
        "__mta": "209490605.1526818969061.1526820063611.1526820069124.6",
        "_lxsdk_s": "1637d80954b-cc3-ffd-4e%7C%7C18"
    }
    header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"
    }
    try:
        respone = requests.get(url=url, cookies=cookie, headers=header)
        if respone.status_code == 200:
            return respone.text
        return None
    except RequestException:
        return None


def parse_one_page(html):
    '''
        解析HTML内容
    :param html:
    :return: 电影名称，主演，上映时间，评分，排名
    '''
    pattern = re.compile(
        '<dd>.*?board-index.*?>(\d+)</i>.*?name">.*?title="(.*?)".*?star">(.*?)</p>.*?releasetime">(.*?)</p>.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>',
        re.S)
    items = re.findall(pattern, html)
    # print(items)
    for item in items:
        yield {
            'name': item[1],
            'star': item[2].strip()[3:],
            'release_time': item[3].strip()[5:],
            'score': item[4] + item[5],
            'rank': item[0]
        }


def write_to_file(item):
    '''
        写入文件
    :param item:
    :return:
    '''
    with open("result.txt", 'a', encoding='utf-8') as f:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")
        f.close()


def excute(start_page):
    '''
        逻辑业务执行入口
    :param start_page:
    :return:
    '''
    url = "http://maoyan.com/board/4?" + str(start_page)
    html = get_one_page(url=url)
    # print(html)
    for item in parse_one_page(html):
        write_to_file(item)


if __name__ == '__main__':
    start_time_serial = time.time()
    '''
        take time:1.749547004699707
    '''
    for i in range(10):
        excute(i * 10)
    end_time_serial = time.time()
    print('serial excute takes time: ' + str(end_time_serial - start_time_serial))

    '''
        take time:0.5420360565185547
    '''
    pool = Pool()
    pool.map(excute, [i * 10 for i in range(10)])
    end_time = time.time()
    print('mutilprocess excute takes time: ' + str(end_time - end_time_serial))
