import  pymysql
import time
import tushare as ts
import pandas as pd
db = pymysql.connect(host='localhost', user='root', password='123456', port=3306, db='stock_data')
# 创建数据库的游标
cursor = db.cursor()
ts.set_token('3f3c696116d8dbb7f9dbd53e598198e41c142216da03a9fc7ad56f89')
pro = ts.pro_api()

class Saver:
    def __init__(self):
        pass

    def daily_basic_saver(self, one_date, ts_list):
        i = 0
        t1 = time.time()
        for code in ts_list:
            max_retries = 5  # 最大重试次数
            retry_count = 0
            while retry_count < max_retries:
                try:
                    df3 = pro.query('daily_basic', ts_code=code, trade_date=one_date,
                                    fields='trade_date, ts_code, circ_mv, pb')
                    df4 = pro.daily(ts_code=code, start_date=one_date, end_date=one_date)
                    if df3.empty or df4.empty:
                        i += 1
                        print('{} no data'.format(code))
                        break
                    sql = '''
                            insert ignore into daily_basic values(%s, %s, %s, %s, %s)
                            '''
                    # replace into`user` ( `id`,`name`,`age` ) values ( 1, '张三', 30) 覆盖替换
                    # insert ignore into `user` ( `id`, `name`, `age` ) values ( 1, '张三', 30) 去重，需要设置唯一约束

                    cursor.execute(sql, (
                        df3['trade_date'].loc[0], df3['ts_code'].loc[0], df3['circ_mv'].loc[0], df3['pb'].loc[0],
                        df4['pct_chg'].loc[0]))
                    db.commit()

                except Exception as e:
                    retry_count += 0
                    print(f'出现异常：{e}，尝试第{retry_count}次重试，睡眠60秒')
                    time.sleep(60)
                break  # 直到程序正常运行
        '''i += 1
        if i % 249 == 0:
            t2 = time.time()
            t3 = t2 - t1
            if t3 < 60.0:
                time.sleep(60 - t3)
            t1 = time.time()'''

    def three_factors_saver(self, Rmt, smb_hml):
        factors_on = pd.concat([Rmt, smb_hml], axis=1)
        factors_on = factors_on.reset_index()
        for factor in range(len(factors_on)):
            date = factors_on.loc[factor][0]
            Rm_Rf = factors_on.loc[factor][1]
            SMB = factors_on.loc[factor][2]
            HML = factors_on.loc[factor][3]

            sql = '''
                        insert ignore into factors_value(trade_date, Rm_Rf, SMB, HML) values(%s, %s, %s, %s)
                        '''
            cursor.execute(sql, (date, Rm_Rf, SMB, HML))
            db.commit()


