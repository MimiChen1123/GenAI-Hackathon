from arxiv_catcher import catch_paper
from alpha_generator import alpha_generator
from code_generator import code_generator
from datetime import datetime
import importlib
import os
import yfinance as yf
import shutil


terminal_width = shutil.get_terminal_size().columns


"""
def isHoldingStock(today_price):
    # 讓GPT生的function，Input可以隨便(甚至可以是完整的價格的dataset)，但Output一定要是1或0
    threshold = 100
    if today_price > threshold:
        return 1
    else:
        return 0
"""


def trade_stock(today_price, funds, stocks):
    # 模擬交易的函式，從isHoldingStock的輸出可以實際操作買賣
    hold_stock = isHoldingStock(today_price)

    if hold_stock == 1:
        stocks_to_buy = funds // today_price
        funds -= stocks_to_buy * today_price
        stocks += stocks_to_buy
    else:
        if stocks > 0:
            funds += stocks * today_price
            stocks = 0

    return funds, stocks


"""
# 直接給定想要實測的時間範圍的股價，計算投資報酬率
initial_funds = 10000
funds, stocks = initial_funds, 0
price_list = [105, 95, 102, 99, 101]

for p in price_list:
    funds, stocks = trade_stock(p, funds, stocks)

rr = (funds + stocks * price_list[-1]) / initial_funds
print("Return Rate = ", rr)


# catch_paper(50)
for i in range(100):
    field = 'stock market'
    strategy = alpha_generator(field, 10)
    try:
        code = code_generator(field, strategy, code_only=True)
    except Exception as e:
        print(e)
        continue

    now = datetime.now()
    filename = f"./trading_strategy/{now.strftime('%Y-%m-%d-%H:%M:%S')}_strategy.py"

    with open(filename, 'w', encoding='utf-8') as file:
        file.write(code)

    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()

    start_marker = "```python"
    end_marker = "```"

    start_index = content.find(start_marker)
    end_index = content.find(end_marker, start_index + len(start_marker))

    if start_index != -1 and end_index != -1:
        start_index += len(start_marker)
        extracted_content = content[start_index:end_index].strip()
    else:
        extracted_content = ''

    with open(filename, 'w', encoding='utf-8') as file:
        file.write(extracted_content)

"""

# 文件名列表
directory = './trading_strategy'
file_list = []
for root, dirs, files in os.walk(directory):
    for file in files:
        file_path = os.path.join(root, file)
        file_list.append(file_path)

data = yf.download('2330.TW', start='2024-01-01', end='2024-08-31')
price_list = data['Adj Close'].tolist()
initial_funds = 10000

for file_name in file_list:
    print('=' * terminal_width)
    print(file_name)
    module = importlib.import_module(file_name)
    StrategyClass = getattr(module, 'TradingStrategy')
    strategy_instance = StrategyClass()
    funds = initial_funds
    stocks = 0

    for today_price in price_list:
        hold_stock = strategy_instance.isHoldingStock(today_price)

        if hold_stock == 1:
            stocks_to_buy = funds // today_price
            funds -= stocks_to_buy * today_price
            stocks += stocks_to_buy
        else:
            if stocks > 0:
                funds += stocks * today_price
                stocks = 0

    rr = (funds + stocks * price_list[-1]) / initial_funds
    print("Return Rate = ", rr)
