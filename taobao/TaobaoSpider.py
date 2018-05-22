import re

import pymongo
from pyquery import PyQuery
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from config.config import MONGO_URL, MONGO_DB, TAOBAO_SERVICE_ARGS, TAOBAO_TABLE, TAOBAO_KEYWORD

'''
    调试的时候使用
    browser = webdriver.Chrome()
'''
browser = webdriver.PhantomJS(service_args=TAOBAO_SERVICE_ARGS)
browser.set_window_size(1400, 900)
wait = WebDriverWait(browser, 5)
digit_pattern = re.compile('(\d+)', re.S)
client = pymongo.MongoClient(MONGO_URL, connect=False)
db = client[MONGO_DB]


def search():
    '''
        搜索关键字
    :return:
    '''
    try:
        browser.get("http://www.taobao.com")
        search_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#q"))
        )
        search_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button'))
        )
        search_input.send_keys(TAOBAO_KEYWORD)
        search_button.click()
        total_page = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.total')))
        parse_item()
        total_page_text = total_page.text
        if total_page_text:
            return int(digit_pattern.search(total_page_text).group(1))
    except TimeoutException:
        print('连接超时递归调用')
        return search()


def to_page(page_number):
    '''
        跳转到某一页
    :return:
    '''
    try:
        print(page_number)
        page_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > input"))
        )
        page_confirm_button = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit'))
        )
        page_input.clear()
        page_input.send_keys(page_number)
        page_confirm_button.click()

        # 判断是否跳转成功
        wait.until(EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.active > span'), str(page_number)))
        parse_item()
    except TimeoutException:
        print('连接超时递归调用')
        return to_page(page_number)


def parse_item():
    '''
        解析商品列表信息
    :return:
    '''
    # 确保商品列表加载出来
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-itemlist .items .item')))
        html = browser.page_source
        doc = PyQuery(html)
        items = doc('#mainsrp-itemlist .items .item').items()
        for item in items:
            good = {
                'image_url': item.find('.pic  .img').attr('src'),
                'price': item.find('.price').text(),
                'cnt': item.find('.deal-cnt').text()[:-3],
                'title': item.find('.title').text(),
                'location': item.find('.location').text()
            }
            save(good)
    except Exception as e:
        print('解析商品出错', e)


def save(good):
    '''
        保存商品信息到MongoDB
    :param good:
    :return:
    '''
    try:
        if db[TAOBAO_TABLE].insert(good):
            print('保存成功', good)
    except Exception:
        print('保存失败', good)


def handle():
    '''
        业务处理
    :return:
    '''
    try:
        total_page = search()
        for i in range(2, total_page + 1):
            to_page(i)
    except Exception as e:
        print('出错了', e)
    finally:
        browser.close()


if __name__ == '__main__':
    handle()
