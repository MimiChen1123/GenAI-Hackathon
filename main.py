from arxiv_catcher import catch_paper
from alpha_generator import alpha_generator
from code_generator import code_generator
import shutil


terminal_width = shutil.get_terminal_size().columns

stop = 0

while not stop:
    print('=' * terminal_width)
    print('請選擇想要做的操作：(輸入對應數字)')
    print('1. 更新資料庫')
    print('2. 產生交易策略')
    print('3. 產生回測程式碼')
    print('4. 離開')

    op = input("> ")
    try:
        op = int(op)
    except Exception as e:
        print('不合法的操作，請再試一次')

    if op == 1:
        print('=' * terminal_width)
        print('請輸入想要新增的論文篇數')
        paper_num = int(input("> "))
        catch_paper(paper_num)
        print('更新完成')

    elif op == 2:
        print('=' * terminal_width)
        print('請輸入想要應用的場域（例如：美股、加密貨幣等）')
        field = input("> ")
        print('請輸入想使用的論文篇數')
        paper_num = int(input("> "))
        alpha = alpha_generator(field, paper_num)
        print(alpha)

    elif op == 3:
        print('=' * terminal_width)
        print('請輸入你的交易策略')
        strategy = input("> ")
        print('請輸入想要應用的場域（例如：美股、加密貨幣等）')
        field = input("> ")
        code = code_generator(field, strategy)
        print(code)

    elif op == 4:
        print('=' * terminal_width)
        print('感謝使用')
        stop = 1

    else:
        print('不合法的操作，請再試一次')

