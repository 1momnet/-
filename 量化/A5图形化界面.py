from tkinter import *
from A1条件管理 import *
from A2股票选取 import *
from A3数据本地化saver import *
from A4量化择时策略 import *
from B2在险价值类 import *


class Application2(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master =  master
        self.pack()
        self.create_widget()

    def create_widget(self):
        # 要求输入（后续更改成用户要求输入页面的时候，需要在确定按钮那里增加一个输入判断合理性的程序，避免报错）
        # 1.创建指数栏目
        self.Label_index = Label(self, text='指数')
        self.Label_index.grid(row=0, column=0) # 第一行第一列，pack()按照行数，一行一个
        user_input1 = StringVar()
        self.entry_index = Entry(self, textvariable=user_input1) # entry1：指数
        self.entry_index.grid(row=0, column=1)
        # 确定是否一致
        print(user_input1.get())
        print(self.entry_index.get())

        # 2.创建日期栏目
        self.Label_date1 = Label(self, text='选股开始日期')
        self.Label_date1.grid(row=1, column=0)
        user_input2 = StringVar()
        self.entry_star_date = Entry(self, textvariable=user_input2) # entry2：开始日期
        self.entry_star_date.grid(row=1, column=1)

        self.Label_date2 = Label(self, text='选股结束日期')
        self.Label_date2.grid(row=1, column=2)
        user_input3 = StringVar()
        self.entry_end_date = Entry(self, textvariable=user_input3) # entry3：结束日期
        self.entry_end_date.grid(row=1, column=3)

        # 3.创建策略栏目
        self.Label_s_strategy = Label(self, text='选股策略')
        self.Label_s_strategy.grid(row=2, column=0)

        user_input4 = StringVar()
        self.entry_s_startegy = Entry(self, textvariable=user_input4)
        self.entry_s_startegy.grid(row=2, column=1) # entry4：选股策略

        self.Label_q_strategy = Label(self, text='择时策略')
        self.Label_q_strategy.grid(row=2, column=2)

        user_input5 = StringVar()
        self.entry_q_startegy = Entry(self, textvariable=user_input5)
        self.entry_q_startegy.grid(row=2, column=3) # entry5：择时策略

        # 5.创建回测时间栏目
        self.Label_q_date = Label(self, text='回测开始日期')
        self.Label_q_date.grid(row=3, column=0)
        user_input_q_start = StringVar()
        self.entry_q_star_date = Entry(self, textvariable=user_input_q_start) # entry6：开始日期
        self.entry_q_star_date.grid(row=3, column=1)

        self.Label_q_date2 = Label(self, text='回测结束日期')
        self.Label_q_date2.grid(row=3, column=2)
        user_input_q_end = StringVar()
        self.entry_q_end_date = Entry(self, textvariable=user_input_q_end)  # entry7：结束日期
        self.entry_q_end_date.grid(row=3, column=3)

        # 6.创建确定按钮
        self.Btn_login = Button(self, text='确定', command=self.event_confirm)
        self.Btn_login.grid(row=4)

        self.Label_result1 = Label(self, text='选股结果')
        self.Label_result1.grid(row=5, column=0)

        self.Label_result2 = Label(self, text='回测结果')
        self.Label_result2.grid(row=5, column=1)

    # 5.为确定按钮创建一个点击事件login
    def event_confirm(self):
        start_date = self.entry_star_date.get()
        end_date = self.entry_end_date.get()
        index = self.entry_index.get()
        s_strategy = self.entry_s_startegy.get()
        q_strategy = self.entry_q_startegy.get()
        trade_back_start_date = self.entry_q_star_date.get()
        trade_back_end_date = self.entry_q_end_date.get()

        Sa1 = Saver()
        A1 = ConditionArrangement(start_date=start_date, end_date=end_date, index=index, s_strategy=s_strategy,
                                  q_strategy=q_strategy, Sa1=Sa1)

        S1 = StockChoice(index=A1.index, trade_date=A1.trade_date, s_strategy=A1.s_strategy, q_strategy=A1.q_strategy, A1=A1, Sa1=Sa1)
        ts_list = S1.ts_list
        A1.into_daily_basic(ts_list=ts_list)
        S1.s_strategy_choice()

        # 在险价值部分
        var_instance = Var(S1.top_stocks)
        var_instance.historical_simulation()

        # 回测部分
        Qd1 = QuantifyData()
        q_strategy = q_strategy_choice(q_strategy=A1.q_strategy)
        stock_profit_ratios = main_backtrade(S1.top_stocks, q_strategy=q_strategy, qd_object=Qd1, trade_back_start_date=trade_back_start_date, tb_end_date=trade_back_end_date)

        self.Label_result3 = Label(self, text='\n'.join(map(str, stock_profit_ratios.keys())), borderwidth=1, relief='solid')
        self.Label_result3.grid(row=6, column=0)

        self.Label_result4 = Label(self, text='\n'.join(map(str, stock_profit_ratios.values())), borderwidth=1, relief='solid')
        self.Label_result4.grid(row=6, column=1)


if __name__ == '__main__':
    root = Tk()
    root.title("股票分析工具")
    root.geometry('600x400')
    app = Application2(master=root)
    app.mainloop()
