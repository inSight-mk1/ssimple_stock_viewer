import requests


class Price_Grabber(object):
    def __init__(self):
        self.interface_url = 'http://hq.sinajs.cn/list='

    def grab(self, stock_code):
        url = self.interface_url + stock_code
        r = requests.get(url)
        return self.parse_text(r.text)

    def parse_text(self, text: str):
        try:
            left_start_idx = text.index('="') + 2
            info_text = text[left_start_idx:]
            s_texts = info_text.split(',')
            last_day_price_f = float(s_texts[2])
            current_price_f = float(s_texts[3])
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
    print(pg.grab('sz300059'))
