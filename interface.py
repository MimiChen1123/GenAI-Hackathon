import gradio as gr

op_code = 0

def update_database(paper_num):
    # call catch_paper
    gr.Info(f"Update Database Success! You added {paper_num} papers into the databases.")

def generate_trading_strategy(field):
    # output = alpha_generator
    output = f"{field} Alpha!"
    with open("strategy.txt", "w") as f:
        f.write(output)
    gr.Info("Trading Strategy Is Generated!")
    return output, "strategy.txt"

def generate_backtest_code(stragety):
    # output = code_generator
    output = "Backtest Code!"
    with open("backtest.py", "w") as f:
        f.write(output)
    gr.Info("Backtest Code Is Generated!")
    return output, "backtest.py"
    

def handle_choice(choice):
    gr.Info("Assign Operation Success!")
    if choice == "更新資料庫":
        op_code = 1
        return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)
    elif choice == "產生交易策略":
        op_code = 2
        return gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)
    elif choice == "產生回測程式碼":
        op_code = 3
        return gr.update(visible=False), gr.update(visible=False), gr.update(visible=True)
    else:
        return gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)

operations = ["更新資料庫", "產生交易策略", "產生回測程式碼"]
fileds = ["美股", "台股", "加密貨幣", "外匯", "基金"]

demo = gr.Blocks()

with demo: 
    choice = gr.Dropdown(choices=operations, label="Choose an operation.")
    with gr.Row():
        op_btn = gr.Button("Submit")
        op_clear = gr.Button("Clear")

    database_group = gr.Group(visible=False)
    generate_group = gr.Group(visible=False)
    backtest_group = gr.Group(visible=False)

    op_btn.click(handle_choice, inputs=choice, outputs=[database_group, generate_group, backtest_group])
    op_clear.click(lambda: "", None, choice)

    with database_group:
      paper_num = gr.Slider(label="The number of papers added to the database", minimum=1, maximum=50, value=5, step=5, interactive=True)
      with gr.Row():
        database_btn = gr.Button("Update Database")
        database_clear = gr.Button("Clear")

    database_btn.click(update_database, inputs=paper_num, outputs=None)
    database_clear.click(lambda: 5, None, paper_num)

    with generate_group:
      field = gr.Dropdown(choices=fileds, label="Choose an application field. Then it will generate a trading strategy.")
      with gr.Row():
        field_btn = gr.Button("Submit")
        field_clear = gr.Button("Clear")
      
      strategy_output = gr.Textbox(label="Trading Strategy")
      strategy_download = gr.File(label="Download Trading Strategy")
      field_btn.click(generate_trading_strategy, inputs=field, outputs=[strategy_output, strategy_download])
      field_clear.click(lambda: "", None, field)
      
    
    with backtest_group:
      stragety = gr.Text(label="Enter yout trending stragety. Then it will generate a backtest code.")
      with gr.Row():
        backtest_btn = gr.Button("Submit")
        backtest_clear = gr.Button("Clear")
      backtest_output = gr.Textbox(label="Backtest Code")
      backtest_download = gr.File(label="Download Backtest Code") 
      backtest_btn.click(generate_backtest_code, inputs=stragety, outputs=[backtest_output, backtest_download])
      backtest_clear.click(lambda: "", None, stragety)
      
    

demo.launch(debug=True)
