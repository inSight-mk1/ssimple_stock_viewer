from price_grabber import Price_Grabber
from prettytable import PrettyTable
import time
import json
from time_domain_list import TimeDomainList
from stock_alert_parser import StockAlertParser, Alert

import signal
import sys


KEEP = True
NOT_KEEP = False
ALERT = True
NO_ALERT = False

# , "000338", "002745", "603897", "000568", "002690"


# def check_alerts(stock_code, current_value, alerts):
#     for alert in alerts:
#         value, alert_type = alert
#         threshold = int(value[1:])
#         print(current_value, threshold, alert_type)
#         if (value.startswith('+') and current_value >= threshold) or (
#                 value.startswith('-') and current_value <= threshold):
#             if alert_type == 'once':
#                 notification.notify(
#                     title='ALERT ONCE',
#                     message=f'{stock_code} has reached the threshold {threshold}.',
#                     app_name='ssviewer',
#                     timeout=10  # 通知显示时间，单位是秒
#                 )
#                 print(f"ALERT ONCE: {stock_code} has reached the threshold {threshold}.")
#                 return ALERT, NOT_KEEP  # Remove this alert after triggering
#             elif alert_type == 'minute':
#                 print(f"ALERT MINUTE: {stock_code} is above the threshold {threshold}.")
#                 return ALERT, KEEP
#             elif alert_type == 'every':
#                 print(f"ALERT EVERY: {stock_code} is above the threshold {threshold}.")
#                 return ALERT, KEEP
#     return NO_ALERT, KEEP  # Keep this alert active


if __name__ == '__main__':
    # 定义信号处理函数
    def signal_handler(sig, frame):
        print('You pressed Ctrl+C!')
        sys.exit(0)


    # 注册信号处理函数以捕捉 SIGINT
    signal.signal(signal.SIGINT, signal_handler)

    pg = Price_Grabber()

    # 解析 stock_list.txt 文件
    stock_parser = StockAlertParser('stock_list.txt')
    stock_parser.parse()
    stock_list, stock_alerts = stock_parser.get_results()

    # 解析 index_list.txt 文件
    index_parser = StockAlertParser('index_list_alert.txt')
    index_parser.parse()
    index_list, index_alerts = index_parser.get_results()

    with open('portfolio.json', 'r') as f:
        portfolio = json.load(f)

    # 使用 TimeDomainList 存储股价
    stock_tdl = [TimeDomainList(element_cnt=20) for _ in stock_list]
    index_tdl = [TimeDomainList(element_cnt=20) for _ in index_list]

    main_table = PrettyTable(
        ['volatility', 'code', 'name', 'price', 'ratio', 'today_low', 'today_high', 'time', 'ratio_f'])

    # ANSI颜色代码 (cmd不适用，windows terminal可用)
    # YELLOW_BACKGROUND = "\033[43m"
    # RESET = "\033[0m"

    while True:
        t_start = time.time()
        stock_table = main_table[:]
        index_table = main_table[:]

        # 获取股票数据
        res_list = pg.grab(stock_list)
        for i, res in enumerate(res_list):
            stock_code = stock_list[i]
            ratio = '-100.00%'
            rf = -100.0
            try:
                ratio = res['ratio']
                rf = float(ratio[:-1])
                stock_tdl[i].push(rf)  # 更新时间域列表
            except Exception as e:
                print('Wrong value:', e)

            volatility_s = ''
            if stock_tdl[i].list[0] is not None:
                volatility_ratio = stock_tdl[i].list[-1] - stock_tdl[i].list[0]
                if volatility_ratio > 0:
                    volatility_ratio = stock_tdl[i].list[-1] - min(stock_tdl[i].list)
                else:
                    volatility_ratio = stock_tdl[i].list[-1] - max(stock_tdl[i].list)
                volatility_s = "%.2f%%" % volatility_ratio

            alert_status = False
            for alert in stock_alerts[i]:
                alert_status = alert.check(float(res['current_price']))

            if alert_status:
                price_s = f"！【{res['current_price']}】"
            else:
                price_s = res['current_price']

            # 添加当前股票信息到表格
            stock_table.add_row([volatility_s, stock_code, res['stock_name'], res['current_price'], ratio,
                                 res['today_low'], res['today_high'], res['current_time'], rf])

        # 获取指数数据
        res_list = pg.grab(index_list)
        for i, res in enumerate(res_list):
            index_code = index_list[i]
            ratio = '-100.00%'
            rf = -100.0
            try:
                ratio = res['ratio']
                rf = float(ratio[:-1])
                index_tdl[i].push(rf)  # 更新时间域列表
            except Exception as e:
                print('Wrong value:', e)

            volatility_s = ''
            if index_tdl[i].list[0] is not None:
                volatility_ratio = index_tdl[i].list[-1] - index_tdl[i].list[0]
                if volatility_ratio > 0:
                    volatility_ratio = index_tdl[i].list[-1] - min(index_tdl[i].list)
                else:
                    volatility_ratio = index_tdl[i].list[-1] - max(index_tdl[i].list)
                volatility_s = "%.2f%%" % volatility_ratio

            alert_status = False
            # print(index_alerts[i])
            for alert in index_alerts[i]:
                alert_status = alert.check(float(res['current_price'])) or alert_status

            if alert_status:
                price_s = f"！【{res['current_price']}】"
            else:
                price_s = res['current_price']

            # 添加当前指数信息到表格
            index_table.add_row([volatility_s, index_code, res['stock_name'], price_s, ratio,
                                 res['today_low'], res['today_high'], res['current_time'], rf])

        for portfolio_name in portfolio.keys():
            p_stock_list = portfolio[portfolio_name]
            total_ratio = 0
            p_stock_res = pg.grab(p_stock_list)
            if len(p_stock_res) == 0:
                print("No result of pg.grab(), Check network.")
                time.sleep(1.0)
                continue
            for res in p_stock_res:
                total_ratio += float(res['ratio'][:-1])
            avg_ratio_f = total_ratio / len(p_stock_list)
            avg_ratio = '%.2f%%' % avg_ratio_f
            index_table.add_row(['', portfolio_name,
                        '', '', avg_ratio,
                        '', '', res['current_time'], rf])

        t_end = time.time()
        print(time.strftime('%H:%M:%S', time.localtime(time.time())), f'取数据时间：{t_end - t_start:.3f}s')
        stock_table.align = "r"
        index_table.align = "r"
        print(index_table.get_string(
            fields=['volatility', 'code', 'name', 'price', 'ratio', 'today_low', 'today_high', 'time']))
        print(stock_table.get_string(
            fields=['volatility', 'code', 'name', 'price', 'ratio', 'today_low', 'today_high', 'time'],
            sortby="ratio_f"))
        time.sleep(2.45)
