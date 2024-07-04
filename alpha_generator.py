import PyPDF2
import sqlite3
import google.generativeai as genai
import os
import time
import random


def alpha_generator(field):
    paper_num = 5
    papers = paper_selector('papers.db', field, paper_num)
    time.sleep(1)
    genai.configure(api_key=os.environ["API_KEY"])

    model = genai.GenerativeModel('gemini-1.5-flash')

    question = f"你是一個專業的alpha researcher，現在有一個客戶希望生成關於{field}的交易策略。\n"
    question += f"你現在手邊有{paper_num}篇論文\n"
    for n in range(paper_num):
        print(f'我參考的第{n+1}篇論文為{papers[n][0]}')
        question += f"第{n+1}篇論文的題目為{papers[n][0]}，內容如下：\n"
        question += extract_text_from_pdf(papers[n][2])
        question += "\n"
    question += "根據以上論文內容，請詳述你生成的交易策略，並說明哪個想法是受到哪篇論文的啟發。\n"

    response = model.generate_content(question)
    alpha = response.text
    return alpha


def paper_selector(db, field, paper_num):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT application_field FROM paper")
    fields = cursor.fetchall()
    field_list = [f[0] for f in fields]

    time.sleep(1)
    genai.configure(api_key=os.environ["API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})
    question = f"你是一個專業的alpha researcher，現在有一個客戶希望生成關於{field}的交易策略。\n"
    question += f"你現在有很多篇論文可以參考，其應用場域分別為{field_list}\n"
    question += "請你將這些場域排序，把你認為最相關的排在最前面，最不相關的排在最後面，並一樣回傳一個list。\n"
    question += "請不要把原始陣列的內容做更改，例如翻譯\n"
    response = model.generate_content(question)
    sorted_field = eval(response.text)
    ret = list()
    for f in sorted_field:
        if f not in field_list:
            continue
        if paper_num <= 0:
            break
        cursor.execute("SELECT * FROM paper WHERE application_field = ?", (f,))
        papers = cursor.fetchall()
        random.shuffle(papers)
        for i in range(min(len(papers), paper_num)):
            ret.append(papers[i])  # tuple
        paper_num -= len(papers)

    conn.close()
    return ret


def extract_text_from_pdf(pdf_path):
    pdf_reader = PyPDF2.PdfReader(pdf_path)
    num_pages = len(pdf_reader.pages)
    text = ""
    for page_num in range(num_pages):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    return text
