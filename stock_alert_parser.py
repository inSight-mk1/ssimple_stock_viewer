import platform
import subprocess


def send_notification(title, message, app_name='ssviewer', timeout=10):
    """跨平台通知函数，支持 macOS 和 Windows"""
    system = platform.system()
    
    if system == 'Darwin':  # macOS
        # 使用 terminal-notifier 发送通知（需要 brew install terminal-notifier）
        try:
            subprocess.run([
                'terminal-notifier',
                '-title', title,
                '-message', message,
                '-sound', 'default'
            ], check=False)
        except FileNotFoundError:
            # 回退到 osascript
            script = f'display notification "{message}" with title "{title}"'
            subprocess.run(['osascript', '-e', script], check=False)
    elif system == 'Windows':
        # Windows 使用 plyer
        try:
            from plyer import notification
            notification.notify(
                title=title,
                message=message,
                app_name=app_name,
                timeout=timeout
            )
        except Exception as e:
            print(f"Windows notification failed: {e}")
    else:  # Linux 或其他系统
        try:
            # 尝试使用 notify-send (Linux)
            subprocess.run(['notify-send', title, message], check=False)
        except FileNotFoundError:
            print(f"Notification: {title} - {message}")


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
                send_notification(
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
