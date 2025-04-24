import requests
import os
import easyquotation
# os.environ['NO_PROXY'] = 'hq.sinajs.cn'

class Price_Grabber(object):
    def __init__(self):
        self.interface_name = 'tencent'
        self.quotation = easyquotation.use(self.interface_name)  # 新浪 ['sina'] 腾讯 ['tencent', 'qq', 'hkquote']
        # self.interface_url = 'http://hq.sinajs.cn/list='

    def grab(self, stocks_code):
        stocks_dict = self.quotation.real(stocks_code)
        # url = self.interface_url + stock_code
        # r = requests.get(url)
        return self.parse_dict(stocks_dict)

    def parse_dict(self, stocks_dict):
        # print(stocks_dict)
        res_dicts = []
        for code in stocks_dict:
            single_stock_dict = stocks_dict[code]
            stock_name = single_stock_dict['name']
            if code[0] in ['5', '1']:
                price_s = '%.3f' % single_stock_dict['now']
            else:
                price_s = '%.2f' % single_stock_dict['now']
            if self.interface_name == 'tencent':
                ratio_s = '%.2f%%' % single_stock_dict['涨跌(%)']
            else:
                ratio_f = (single_stock_dict['now'] - single_stock_dict['close']) / single_stock_dict['close'] * 100.0
                ratio_s = '%.2f%%' % ratio_f
            high_ratio = (single_stock_dict['high'] - single_stock_dict['close']) / single_stock_dict['close'] * 100.0
            high_ratio_s = '%.2f%%' % high_ratio
            low_ratio = (single_stock_dict['low'] - single_stock_dict['close']) / single_stock_dict['close'] * 100.0
            low_ratio_s = '%.2f%%' % low_ratio
            if self.interface_name == 'tencent':
                current_date = str(single_stock_dict['datetime'].date())
                current_time = str(single_stock_dict['datetime'].time())
            else:
                current_date = single_stock_dict['date']
                current_time = single_stock_dict['time']
            res_dict = dict(stock_name=stock_name, ratio=ratio_s, current_price=price_s,
                            today_high=high_ratio_s, today_low=low_ratio_s,
                            current_date=current_date, current_time=current_time)
            res_dicts.append(res_dict)
        return res_dicts

    def parse_text(self, text: str):
        try:
            left_start_idx = text.index('="') + 2
            ts_code_idx = left_start_idx - 8
            ts_code = text[ts_code_idx:ts_code_idx+6]
            info_text = text[left_start_idx:]
            s_texts = info_text.split(',')
            last_day_price_f = float(s_texts[2])
            current_price_f = float(s_texts[3])
            if ts_code[0] in ['5', '1']:
                price_s = '%.3f' % current_price_f
            else:
                price_s = '%.2f' % current_price_f
            ratio = (current_price_f - last_day_price_f) / last_day_price_f * 100
            ratio_s = '%.2f%%' % ratio
            today_high_ratio = (float(s_texts[4]) - last_day_price_f) / last_day_price_f * 100
            high_ratio_s = '%.2f%%' % today_high_ratio
            today_low_ratio = (float(s_texts[5]) - last_day_price_f) / last_day_price_f * 100
            low_ratio_s = '%.2f%%' % today_low_ratio
            res_dict = dict(stock_name=s_texts[0], ratio=ratio_s, current_price=price_s,
                    today_high=high_ratio_s, today_low=low_ratio_s,
                    current_date=s_texts[30], current_time=s_texts[31])
        except:
            print(text)
            res_dict = dict(stock_name='Error', ratio="No", current_price='data',
                            today_high='returned', today_low='Check',
                            current_date='request', current_time='text')
        return res_dict


if __name__ == '__main__':
    pg = Price_Grabber()
    dict = pg.grab(['832522'])
    print(dict)
