import requests
import json

# Function to get stock name from code
def get_stock_name(stock_code):
    # Shanghai/Shenzhen stocks (6/0/3/2/8/9 prefix)
    if stock_code.startswith(('6', '0', '3', '2', '8', '9')):
        market = 'sh' if stock_code.startswith(('6', '5', '9')) else 'sz'
        url = f'http://qt.gtimg.cn/q={market}{stock_code}'
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                # Parse the response (format: v_pv_none="1~StockName~...")
                data = response.text.split('~')
                if len(data) > 1:
                    return data[1]
        except Exception as e:
            print(f"Error fetching {stock_code}: {e}")
    return f"Unknown ({stock_code})"

# Load portfolio data
with open('portfolio.json') as f:
    portfolios = json.load(f)

# Get and print stock names for each portfolio
for portfolio, codes in portfolios.items():
    print(f"\nPortfolio {portfolio}:")
    for code in codes:
        name = get_stock_name(code)
        print(f"{code}: {name}")
