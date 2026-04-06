import tushare as ts
import backtrader as bt
import pandas as pd

ts.set_token('用户token')
pro = ts.pro_api()

class BollStrategy(bt.Strategy):
    # 可选，设置回测的可变参数：如移动均线的周期
    def log(self, txt):
        dt = self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.lines.top = bt.indicators.BollingerBands(self.datas[0], period=20).top
        self.lines.bot = bt.indicators.BollingerBands(self.datas[0], period=20).bot

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:  # 如订单已被处理，则不用做任何事情
            return
        if order.status in [order.Completed]:  # # 检查订单是否完成
            if order.isbuy():
                self.log(
                    '买入, 价格: {:.2f}, 成本: {:.2f}, 佣金: {:.2f}'.format
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))
            else:
                self.log(
                    '卖出, 价格: {:.2f}, 成本: {:.2f}, 佣金: {:.2f}'.format
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))
            # 这里更新bar_execute的长度，意味着bar_execute为前一次交易的长度
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        self.order = None  # 订单状态处理完成，设为空

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('操作收益, 毛利润: {:.2f}, 净利润: {:.2f}'.format(trade.pnl, trade.pnlcomm))

    def next(self):
        # self.log('Close, %.2f' % self.dataclose[0]) # 记录收盘价
        if self.order:  # 是否正在下单，如果是的话不能提交第二次订单
            return
        # 检查持仓
        if not self.position:
            # 没有持仓，买入开仓
            if self.dataclose <= self.lines.bot[0]:
                print("收盘价跌破lower线，执行买入")
                self.order = self.order_target_percent(target=0.95)
        else:
            # 手里有持仓，判断卖平
            if self.dataclose >= self.lines.top[0]:
                print("收盘价超过upper线，执行卖出")
                self.order = self.order_target_percent(target=0)



class QuantifyData:
    def acquire_data(self, stock, start_date, end_date):
        df = ts.pro_bar(ts_code=stock, adj='qfq', start_date=start_date, end_date=end_date)
        dates = pd.to_datetime(df["trade_date"])
        df = df[["open", "high", "low", "close", "vol"]]
        df.columns = ['open', 'high', 'low', 'close', 'volume']
        df.index = dates
        df.sort_index(ascending=True, inplace=True)
        return df


def q_strategy_choice(q_strategy):
    q_method_map = {
        '布林线': BollStrategy,
    }
    return q_method_map.get(q_strategy)
