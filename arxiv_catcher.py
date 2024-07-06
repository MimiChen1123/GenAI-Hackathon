import requests
from bs4 import BeautifulSoup
import re
import shutil
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
    question += "{'trading_strategy_related': 1, 'application_field': '美股', 'trading_strategy': ['1', '2', ...], 'codable': 1}\n"

    response = model.generate_content(question)
    try:
        d = json.loads(response.text)
        keys_to_check = ['trading_strategy_related', 'application_field', 'trading_strategy']
        keys_exist = [key in d for key in keys_to_check]
        if not all(keys_exist):
            d = isCodable(title, abstract)
        return d
    except Exception as e:
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

    ret = ""

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
                    is_download = 0
                    if 'https://arxiv.org/pdf/' not in pdf_url:
                        continue
                    ret += f'論文連結：{pdf_url}'

                    next_p_tag = a_tag.find_next('p', class_='title is-5 mathjax')
                    if next_p_tag:
                        title = next_p_tag.get_text()
                        title = clean_title(title)

                        pdf_filename = f'{directory}{title}.pdf'
                        if os.path.exists(pdf_filename):
                            ret += '（已經下載過囉）\n'
                            is_download = 1
                        else:
                            pdf_response = requests.get(pdf_url)
                            if pdf_response.status_code == 200:
                                with open(pdf_filename, 'wb') as pdf_file:
                                    pdf_file.write(pdf_response.content)
                                ret += '(下載成功！)\n'
                            else:
                                pdf_availiable = 0
                                ret += '(找不到PDF檔QAQ)\n'

                        ret += f'論文標題：{title}\n'

                    else:
                        ret += "找不到標題QAQ\n"

                    next_span_tag = a_tag.find_next('span', class_='abstract-full has-text-grey-dark mathjax')
                    if next_span_tag:
                        abstract = next_span_tag.get_text()
                        abstract = clean_abstract(abstract)
                    else:
                        ret += "找不到摘要QAQ\n"
                    
                    if is_download:
                        pass

                    elif pdf_availiable and not is_exist_sqlite3(db, title):
                        info = isCodable(title, abstract)
                        ret += f"應用領域：{info['application_field']}\n"

                        ret += "是否和交易策略有關："
                        if info['trading_strategy_related']:
                            ret += "是\n"
                        else:
                            ret += "否\n"
                        ret += "是否方便用python進行回測："
                        if info['codable']:
                            ret += "是\n"
                        else:
                            ret += "否\n"
                        
                        if info['trading_strategy_related'] and info['codable']:
                            add_sqlite3(db, title, abstract, pdf_filename, info['trading_strategy_related'], info['application_field'], info['trading_strategy'], info['codable'])
                            ret += "已加入資料庫\n"
                        else:
                            ret += "不加入資料庫\n"

                        num -= 1

                    if num == 0:
                        done = 1
                        break

                    ret += '=' * terminal_width
                    ret += "\n"

            else:
                ret += "No matching <a> tag found."
            start_index += size
        else:
            ret += "Failed to fetch the webpage."

    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM paper")
    total_rows = cursor.fetchone()[0]
    conn.close()

    ret += f"\n更新完成，資料庫共有{total_rows}篇論文\n"
    return ret
