import csv
import logging
import os
import time

from lagou.Http import Http
from lagou.Parse import Parse
from lagou.setting import headers, cookies, cities, key_word, url

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s Process%(process)d:%(thread)d %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='lagou.log',
                    filemode='a')


def parse_info_detail(parser):
    info = parser.parse_info()
    return info


def save_to_csv(info, param):
    '''
        保存信息到csv文件
    :param info:
    :param param:
    :return:
    '''
    data = []
    filename = 'job_information.csv'
    if not os.path.exists(filename):
        title = ['公司名称', '公司类型', '融资阶段', '标签', '公司规模', '公司所在地', '职位类型', '学历要求', '福利', '薪资', '工作经验']
        data.append(title)
    with open(filename, 'a', encoding='utf-8') as out:
        csv_write = csv.writer(out)
        for p in info:
            line = [str(p['companyName']), str(p['companyType']), str(p['companyStage']), str(p['companyLabel']),
                    str(p['companySize']), str(p['companyDistrict']), str(p['positionType']),
                    str(p['positionEducation']), str(p['positionAdvantage']), str(p['positionSalary']),
                    str(p['positionWorkYear'])]
            data.append(line)

        logging.info("save %s records to csv" % str(len(data)))
        csv_write.writerows(data)


def post(url, param):
    request = Http()
    respone = request.post(url=url, param=param, headers=headers, cookies=cookies)
    parser = Parse(respone)
    page_num = parser.parse_page()
    info = []
    for i in range(1, page_num + 1):
        print('第%s页,共%s页' % (i, page_num))
        logging.info('current page is %s ,total page is %s' % (i, page_num))
        param['pn'] = str(i)
        html = request.post(url, param=param, headers=headers, cookies=cookies)
        html_parser = Parse(html)
        info += parse_info_detail(html_parser)
        if not i % 2:
            save_to_csv(info, param=param)
            info = []
        time.sleep(2)


def handle():
    '''
        处理业务逻辑
    :return:
    '''
    for city in cities:
        param = {'first': 'true', 'pn': '1', 'kd': key_word, 'city': city}
        post(url, param)


if __name__ == '__main__':
    handle()
