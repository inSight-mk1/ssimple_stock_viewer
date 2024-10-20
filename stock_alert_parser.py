from plyer import notification


class Alert:
    def __init__(self, stock_code, price, alert_type):
        self.stock_code = stock_code
        self.price = price  # 预警价格
        self.alert_type = alert_type  # 预警类型（once, minute, every）
        self.triggered = False  # 是否已触发预警

    def check(self, current_price):
        threshold = int(self.price[1:])
        if (self.price.startswith('+') and current_price >= threshold) or (
                self.price.startswith('-') and current_price <= threshold):
            if not self.triggered:
                self.triggered = True  # 标记为已触发
                notification.notify(
                    title='ALERT ONCE',
                    message=f'{self.stock_code} has reached the threshold {threshold}.',
                    app_name='ssviewer',
                    timeout=10  # 通知显示时间，单位是秒
                )
            return True  # 价格满足预警，返回True
        return False

    def reset(self):
        if self.alert_type != 'once' and self.triggered:
            self.triggered = False  # 重置触发状态


class StockAlertParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.stock_list = []
        self.alert_list = []

    def parse(self):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()  # 去掉行首尾空白字符
                if line:  # 确保行不为空
                    parts = line.split(',')
                    stock_code = parts[0].strip()
                    self.stock_list.append(stock_code)

                    alerts = []
                    for i in range(1, len(parts), 2):
                        if i + 1 < len(parts):  # 确保有配对的预警信息
                            alert_price = parts[i].strip()
                            alert_type = parts[i + 1].strip()
                            alerts.append(Alert(stock_code, alert_price, alert_type))

                    self.alert_list.append(alerts)

    def get_results(self):
        return self.stock_list, self.alert_list


# 测试代码
if __name__ == "__main__":
    # 输入文件路径
    file_path = 'index_list_alert.txt'  # 请确保此文件存在并包含要解析的内容

    # 处理数据并获取结果
    parser = StockAlertParser(file_path)
    parser.parse()
    stock_list, alert_list = parser.get_results()

    # 输出结果
    print("Stock List:", stock_list)
    print("Alert List:", alert_list)
