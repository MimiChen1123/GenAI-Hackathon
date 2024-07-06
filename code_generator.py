import google.generativeai as genai
import os
import time


def code_generator(field, strategy):
    time.sleep(1)
    genai.configure(api_key=os.environ["API_KEY"])

    model = genai.GenerativeModel('gemini-1.5-flash')

    question = f"你是一個專業的程式設計師，有客戶提供了關於{field}的交易策略，交易策略如下：\n"
    question += strategy
    question += "請你幫他寫出一份python code，並且詳細說明程式碼的哪一段對應到交易策略的哪個部份\n"
    question += "並詳細說明需要額外收集哪些資訊（例如某公司一年的歷史股價）\n"
    question += "請用markdown格式輸出。\n"

    response = model.generate_content(question)
    return response.text
