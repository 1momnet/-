import tushare as ts
import backtrader as bt
import pandas as pd

ts.set_token('3f3c696116d8dbb7f9dbd53e598198e41c142216da03a9fc7ad56f89')
pro = ts.pro_api()

class BollStrategy(bt.Strategy):
    # 可选，设置回测的可变参数：如移动均线的周期
    def log(self, txt):
        dt = self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        super().__init__()
        self.dataclose = self.datas[0].close
        self.order = None
        self.lines.top = bt.indicators.BollingerBands(self.dataclose, period=20).top
        self.lines.bot = bt.indicators.BollingerBands(self.dataclose, period=20).bot

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


def main_backtrade(top_stocks, qd_object, q_strategy, trade_back_start_date, tb_end_date):
    stock_profit_ratios = {}

    for i in top_stocks:
        stock = i
        # today = datetime.now().strftime('%Y%m%d')
        # end_date_f = today
        
        # 实例化
        df = qd_object.acquire_data(stock, start_date=trade_back_start_date, end_date=tb_end_date)

        # 实例化 cerebro——引擎
        cerebro = bt.Cerebro()

        # 添加数据进cerebro
        data = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(data)

        # 设置本金与佣金
        cerebro.broker.setcash(100000)
        cerebro.broker.setcommission(commission=0.001)

        # 添加交易策略——cerebro行动逻辑
        print(i)
        cerebro.addstrategy(q_strategy)

        # 添加分析器
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='annual_return')

        # 添加观察器
        cerebro.addobserver(bt.observers.DrawDown)
        cerebro.addobserver(bt.observers.TimeReturn)

        # 运行
        results = cerebro.run()
        strat = results[0]

        # 打印结果
        print('*' * 54)
        print(f'{'结果分析':-^50}')
        print('*' * 54)
        # 打印结果
        returns = strat.analyzers.returns.get_analysis()
        sharpe = strat.analyzers.sharpe.get_analysis()
        drawdown = strat.analyzers.drawdown.get_analysis()
        trades = strat.analyzers.trades.get_analysis()
        annual_return = strat.analyzers.annual_return.get_analysis()

        print(f'初始资金: {cerebro.broker.startingcash:.2f}')
        print(f'最终资金: {cerebro.broker.getvalue():.2f}')
        print(f'收益率: {returns['rtot']:.2%}')
        print(f'平均收益率: {returns['ravg']:.2%}')
        print(f'夏普比率: {sharpe['sharperatio']:.3f}')
        print(f'最大回撤: {drawdown["max"]["drawdown"]:.2%}')
        print(f'最大回撤持续: {drawdown["max"]["len"]} 天')
        print(f'总交易次数: {trades["total"]["total"]}')
        if trades["total"]["total"] > 0:
            print(f'胜率: {trades["won"]["total"] / trades["total"]["total"]:.2%}')

        print(f'年化收益: {annual_return.get("rnorm", 0):.2%}')

        profit_ratio = round(returns["rtot"] * 100, 2)
        stock_profit_ratios[i] = profit_ratio

        # 可视化回测结果
        cerebro.plot()
    print(stock_profit_ratios)
    return stock_profit_ratios

