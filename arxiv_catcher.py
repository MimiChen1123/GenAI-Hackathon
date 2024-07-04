import requests
from bs4 import BeautifulSoup
import re
import shutil
import PyPDF2
import sqlite3
import google.generativeai as genai
import os
import json
import time


def clean_title(title):
    cleaned_title = title.strip()
    cleaned_title = re.sub(r'\s+', ' ', cleaned_title)  # 替換多個空白字符為單個空格
    cleaned_title = re.sub(r'[^\w\s\-.]', '', cleaned_title)  # 去除所有非字母數字、空格、連字號和點的字符

    return cleaned_title


def clean_abstract(abstract):
    cleaned_abstract = re.sub(r'\s+', ' ', abstract)  # 替換多個空白字符為單個空格
    cleaned_abstracts = cleaned_abstract.split('.')
    cleaned_abstract = ''
    for i in range(len(cleaned_abstracts) - 1):
        cleaned_abstract += cleaned_abstracts[i] + '.'
    return cleaned_abstract


def extract_text_from_pdf(pdf_path):
    pdf_reader = PyPDF2.PdfReader(pdf_path)
    num_pages = len(pdf_reader.pages)
    text = ""
    for page_num in range(num_pages):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    return text


def isCodable(title, abstract):
    time.sleep(1)
    genai.configure(api_key=os.environ["API_KEY"])

    model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})

    question = "你是一個專業的財務分析師\n"
    question += f"這篇論文的題目為{title}\n"
    question += f"這篇論文的摘要如下：\n{abstract}\n"
    question += "請問這篇論文是否與交易策略有關？（回答1或0即可，1表示有，0表示沒有）\n"
    question += "應用的場域為何（例如：美股、加密貨幣）？\n"
    question += "簡述其交易策略？（請用中文回答）\n"
    question += "如果要將其交易策略寫成一份python code的話，是否能透過單純的歷史價量做回測？（回答1或0即可，1表示可以，0表示不行）\n"
    question += "請用json格式回覆，範例如下：\n"
    question += "{'trading_strategy_ralated': 1, 'application_field': '美股', 'trading_strategy': ['1', '2', ...], 'codable': 1}\n"

    response = model.generate_content(question)
    try:
        print("Genimi 回覆：")
        print(json.dumps(json.loads(response.text), indent=4, ensure_ascii=False))
        return json.loads(response.text)
    except Exception as e:
        print(f"發生異常：{e}")
        return isCodable(title, abstract)


def init_sqlite3(db):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS paper (
        title TEXT,
        abstract TEXT,
        filename TEXT,
        related INTEGER,
        application_field TEXT,
        strategy TEXT,
        codable INTEGER
    )
    ''')
    conn.close()
    return


def add_sqlite3(db, title, abstract, filename, related, application_field, strategy, codable):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    strategy = json.dumps(strategy, ensure_ascii=False)
    cursor.execute("INSERT INTO paper (title, abstract, filename, related, application_field, strategy, codable) VALUES (?, ?, ?, ?, ?, ?, ?)", (title, abstract, filename, related, application_field, strategy, codable))
    conn.commit()
    conn.close()
    return


def is_exist_sqlite3(db, title):
    ret = 0
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM paper WHERE title = ?", (title,))
    result = cursor.fetchone()

    if result:
        ret = 1

    conn.close()
    return ret


def catch_paper(num):
    size = 50
    directory = './papers/'
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.138 Safari/537.36'
    }
    start_index = 0
    done = 0
    terminal_width = shutil.get_terminal_size().columns

    db = 'papers.db'
    init_sqlite3(db)

    while not done:
        url = f'https://arxiv.org/search/advanced?advanced=&terms-0-operator=AND&terms-0-term=&terms-0-field=all&classification-physics_archives=all&classification-q_finance=y&classification-include_cross_list=include&date-filter_by=all_dates&date-year=&date-from_date=&date-to_date=&date-date_type=submitted_date&abstracts=show&size={size}&order=-announced_date_first&start={start_index}'

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            a_tags = soup.find_all('a', href=True)
            if a_tags:
                for a_tag in a_tags:
                    pdf_url = a_tag['href']
                    pdf_availiable = 1
                    if 'https://arxiv.org/pdf/' not in pdf_url:
                        continue
                    print(f'論文連結：{pdf_url}', end=' ')

                    next_p_tag = a_tag.find_next('p', class_='title is-5 mathjax')
                    if next_p_tag:
                        title = next_p_tag.get_text()
                        title = clean_title(title)

                        pdf_filename = f'{directory}{title}.pdf'
                        if os.path.exists(pdf_filename):
                            print('（已經下載過囉）')
                        else:
                            pdf_response = requests.get(pdf_url)
                            if pdf_response.status_code == 200:
                                with open(pdf_filename, 'wb') as pdf_file:
                                    pdf_file.write(pdf_response.content)
                                print('(下載成功！)')
                            else:
                                pdf_availiable = 0
                                print('(找不到PDF檔QAQ)')

                        print(f'論文標題：{title}')

                    else:
                        print("找不到標題QAQ")

                    next_span_tag = a_tag.find_next('span', class_='abstract-full has-text-grey-dark mathjax')
                    if next_span_tag:
                        abstract = next_span_tag.get_text()
                        abstract = clean_abstract(abstract)
                        print("論文摘要：", abstract)
                    else:
                        print("找不到摘要QAQ")

                    if pdf_availiable and not is_exist_sqlite3(db, title):
                        # content = extract_text_from_pdf(pdf_filename)
                        # print("論文內容：", content)
                        info = isCodable(title, abstract)
                        if info['trading_strategy_ralated'] and info['codable']:
                            num -= 1
                            add_sqlite3(db, title, abstract, pdf_filename, info['trading_strategy_ralated'], info['application_field'], info['trading_strategy'], info['codable'])

                    if num == 0:
                        done = 1
                        break

                    print('=' * terminal_width)

            else:
                print("No matching <a> tag found.")
            start_index += size
        else:
            print("Failed to fetch the webpage.")

    return
