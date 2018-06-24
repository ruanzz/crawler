import logging

import demjson

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s Process%(process)d:%(thread)d %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='lagou.log',
                    filemode='a')


class Parse:
    '''
    解析网页信息
    '''

    def __init__(self, html):
        self.html = html
        self.json = demjson.decode(html)
        pass

    def parse_page(self):
        '''
        解析并计算页面数量
        :return: 页面数量
        '''
        total = self.json['content']['positionResult']['totalCount']  # 职位总数量
        page_size = self.json['content']['positionResult']['resultSize']  # 每一页显示的数量
        page_num = int(total) // int(page_size) + 1  # 页面数量
        return page_num

    def parse_info(self):
        '''
        解析信息
        '''
        info = []
        try:
            for position in self.json['content']['positionResult']['result']:
                i = {}
                i['companyName'] = position['companyFullName']
                i['companyDistrict'] = position['district']
                i['companyLabel'] = position['companyLabelList']
                i['companySize'] = position['companySize']
                i['companyStage'] = position['financeStage']
                i['companyType'] = position['industryField']
                i['positionType'] = position['firstType']
                i['positionEducation'] = position['education']
                i['positionAdvantage'] = position['positionAdvantage']
                i['positionSalary'] = position['salary']
                i['positionWorkYear'] = position['workYear']
                info.append(i)
        except Exception as e:
            logging.error('parse error : %s' % str(e))
        return info
