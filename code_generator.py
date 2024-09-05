import google.generativeai as genai
import os
import time


def code_generator(field, strategy, code_only=False):
    time.sleep(1)
    genai.configure(api_key=os.environ["API_KEY"])

    model = genai.GenerativeModel('gemini-1.5-flash')

    if not code_only:
        question = f"你是一個專業的程式設計師，有客戶提供了關於{field}的交易策略，交易策略如下：\n"
        question += strategy
        question += "請你幫他寫出一份python code，並且詳細說明程式碼的哪一段對應到交易策略的哪個部份\n"
        question += "並詳細說明需要額外收集哪些資訊（例如某公司一年的歷史股價）\n"
        question += "請用markdown格式輸出。\n"

    if code_only:
        question = f"你是一個專業的程式設計師，有客戶提供了關於{field}的交易策略，交易策略如下：\n"
        question += strategy
        question += "請你幫他寫出一份python code。\n"
        question += "你的程式碼一定要包含一個名為isHoldingStock的函式，該函式的輸入為當天的價格，輸出為是否持有股票。\n"
        question += "1代表持有股票，0代表不持有股票\n"
        question += "例如：如果有個交易策略為「當股價超過100時，持有股票，反之不持有股票」，你應該生成以下程式碼：\n"
        question += "def isHoldingStock(today_price): \n"
        question += "\t threshold = 100\n"
        question += "\t if today_price > threshold: \n"
        question += "\t\t return 1\n"
        question += "\t else: \n"
        question += "\t\t return 0\n"
        question += "股價請統一使用2330-TW的股價，獲取方式如下：\n"
        question += "import yfinance\n"
        question += "start_date = '2020-01-01'\n"
        question += "end_date = '2023-12-31'\n"
        question += "data = yf.download(ticker, start=start_date, end=end_date)\n"
        question += "data的格式為dataframe，裡面包含'Date', 'Open', 'High', 'Low'. 'Close', 'Adj Close', 'Volume'\n"
        question += "我想要以start_date = 2020-01-01, end_date = 2023-12-31的股價作為train data。\n"
        question += "我在回測時，會直接呼叫isHoldingStock()，如果需要訓練模型，或者做其他預處理，請額外寫一個init函式，並在isHoldingStock()中檢查是否初始化過\n"
        question += "所有程式碼可以包含在名為TradingStrategy的class裡面。例如：\n"
        question += "class TradingStrategy:\n"
        question += "\t def __init__(self):\n"
        question += "\t\t # TODO\n"
        question += "\t def train(self, start_date, end_date):\n"
        question += "\t\t # TODO\n"
        question += "\t def isHoldingStock(self, today_price):\n"
        question += "\t\t # TODO\n"
        question += "請用python的格式輸出，不要輸出其他內容。\n"

    response = model.generate_content(question)
    return response.text
