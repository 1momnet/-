import time
import tushare as ts
import pymysql
import pandas as pd
from dateutil import parser
from datetime import datetime

db = pymysql.connect(host='localhost', user='root', password='123456', port=3306, db='stock_data')
# 创建数据库的游标
cursor = db.cursor()
ts.set_token('3f3c696116d8dbb7f9dbd53e598198e41c142216da03a9fc7ad56f89')
pro = ts.pro_api()

class ConditionArrangement:
    def __init__(self, start_date, end_date, index, s_strategy, q_strategy, Sa1):
        self.Sa1 = Sa1
        self.start_date = start_date
        self.end_date = end_date
        self.index = index
        self.s_strategy = s_strategy # stock
        self.q_strategy = q_strategy # quantify
        self.trade_date = self.date_translate(self.start_date, self.end_date) # 这个变量的是数据类型是list


    # 把正常的时间范围转化成交易日
    def date_translate(self, start_date, end_date):
        df = pro.query('trade_cal', start_date=start_date, end_date=end_date, is_open=1)
        trade_date = df['cal_date'].tolist()
        trade_date.sort()
        return  trade_date


    # 判断数据库daily_basic表是否存储给定日期的数据
    def into_daily_basic(self, ts_list):
        sql = '''
                select trade_date from daily_basic order by trade_date asc
                '''
        cursor.execute(sql)
        db_date = cursor.fetchall()
        # 空数据表处理
        if not db_date:
            for date in self.trade_date:
                one_date = date
                self.Sa1.daily_basic_saver(one_date, ts_list=ts_list)
            return
        df_date = pd.DataFrame(db_date, columns=['trade_date'])
        date = df_date['trade_date'].to_list()
        min_date = min(parser.parse(d) for d in date)
        min_date = min_date.strftime('%Y%m%d')

        max_date = max(parser.parse(d) for d in date)
        max_date = max_date.strftime('%Y%m%d')

        # 另一种选取最大日期方法，在下面的is_in_factors_value中有使用。需要在数据库中按日期升序排序order by trade_date asc
        # max_date = db_date[-1][0]
        print(f"数据库中最小的日期是：{min_date}")
        print(f'数据库中最大的日期是：{max_date}')

        if int(self.start_date) < int(min_date):
            trade_date = self.date_translate(self.start_date, min_date)
            print(f'股票数据进行本地化数据，缺少起始日期数据。数据库最小日期为：{min_date}')
            for date in trade_date:
                one_date = date
                self.Sa1.daily_basic_saver(one_date, ts_list=ts_list)

        elif int(self.end_date) > int(max_date):
            print(f'股票数据进行本地化数据，缺少结束日期数据。数据库最大日期为：{max_date}')
            trade_date = self.date_translate(max_date, self.end_date)
            for date in trade_date:
                one_date = date
                self.Sa1.daily_basic_saver(one_date, ts_list=ts_list)
            return

        else:
            return


    def is_in_factors_value(self):
        sql = '''
                        select trade_date from factors_value order by trade_date asc
                        '''
        cursor.execute(sql)
        db_data = cursor.fetchall()

        if not db_data:
            print('因子值数据进行本地化')
            return False

        min_date =  db_data[0][0]
        max_date = db_data[-1][0]

        if self.start_date < min_date:
            print(f'因子值数据进行本地化。数据库最小日期为：{min_date}')
            return False

        elif self.end_date > max_date:
            print(f'因子值数据进行本地化。 数据库最大日期为：{max_date}')
            return False
        else:
            return True

