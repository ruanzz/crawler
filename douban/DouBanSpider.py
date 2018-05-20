import requests
import re
from bs4 import BeautifulSoup
from pyquery import PyQuery as pq


def douban_spider_re():
    '''
      正则表达式爬取豆瓣图书信息
    :return:
    '''
    url = "http://book.douban.com/"
    html = requests.get(url=url).text

    pattern = re._compile(
        'li.*?cover.*?href="(.*?)".*?info.*?author">(.*?)(</span>|</div>|</p>).*?</li>', re.S)

    results = re.findall(pattern=pattern, string=html)

    for result in results:
        href, author, temp = result
        author = re.sub("\s", "", author)
        author = re.sub("作者：", "", author)
        print(href, author)


def douban_spider_bs():
    '''
    BeautifulSoup 爬取豆瓣图书
    :return:
    '''

    url = "http://book.douban.com/"
    html = requests.get(url=url).text

    soup = BeautifulSoup(html, 'lxml')
    infos = soup.select(".info")
    for info in infos:
        # print(info)
        href = info.find("a").attrs['href']
        book_name = info.find(class_='title').get_text()
        book_name = re.sub("\s", "", book_name)
        author = info.find(class_='author').get_text()
        author = re.sub("\s", "", author)
        print(href, book_name, author)


def douban_spider_pq():
    '''
    PyQuery 爬去豆瓣信息
    :return:
    '''
    url = "http://book.douban.com/"
    html = requests.get(url=url).text

    doc = pq(html)
    infos = doc('.info')
    # print(infos)
    for info in infos.items():
        href = info.find("a").attr('href')
        book_name = info.find(".title").text()
        author = info.find(".author").text()
        print(href, book_name, author)


if __name__ == '__main__':
    # douban_spider_re()

    # douban_spider_bs()

    douban_spider_pq()
