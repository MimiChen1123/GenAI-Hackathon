import gradio as gr
from arxiv_catcher import catch_paper
from alpha_generator import alpha_generator
from code_generator import code_generator


def update_database(paper_num):
    output = catch_paper(paper_num)
    gr.Info(f"Update Database Success! You added {paper_num} papers into the databases.")
    return output

def generate_trading_strategy(field, paper_num):
    # output = alpha_generator
    output = alpha_generator(field, paper_num)
    gr.Info("Trading Strategy Is Generated!")
    return output

def generate_backtest_code(field, strategy):
    # output = code_generator
    output = code_generator(field, strategy)
    gr.Info("Backtest Code Is Generated!")
    return output


def handle_choice(choice):
    if choice == "更新資料庫":
        return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)
    elif choice == "產生交易策略":
        return gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)
    elif choice == "產生回測程式碼":
        return gr.update(visible=False), gr.update(visible=False), gr.update(visible=True)
    else:
        return gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)


if __name__ == '__main__':
    operations = ["更新資料庫", "產生交易策略", "產生回測程式碼"]

    theme = gr.themes.Soft(spacing_size="md")
    demo = gr.Blocks(theme=theme)

    with demo:
        radio = gr.Radio(choices=operations, label="Choose an operation: ", interactive=True)
        database_group = gr.Group(visible=False)
        generate_group = gr.Group(visible=False)
        backtest_group = gr.Group(visible=False)

        radio.change(handle_choice, inputs=radio, outputs=[database_group, generate_group, backtest_group])

        with database_group:
            paper_num = gr.Slider(label="The number of papers added to the database: ", minimum=1, maximum=50, value=5, step=1, interactive=True)
            with gr.Row():
                database_btn = gr.Button("Update Database")
                database_clear = gr.Button("Clear")

            status_output = gr.Textbox("", label="Status")
            database_btn.click(update_database, inputs=paper_num, outputs=status_output)
            database_clear.click(lambda: [5, ""], None, [paper_num, status_output])

        with generate_group:
            field = gr.Textbox(lines=1, visible=True, value="美股", label="Choose an application field. Then it will generate a trading strategy: ")
            paper_num = gr.Slider(label="The number of papers reference", minimum=1, maximum=10, value=3, step=1, interactive=True)
            with gr.Row():
                field_btn = gr.Button("Submit")
                field_clear = gr.Button("Clear")

            # strategy_output = gr.Textbox(label="Trading Strategy", lines=2, interactive=True, show_copy_button=True)
            strategy_output = gr.Markdown("", line_breaks=True, label="Trading Strategy: ")
            field_btn.click(generate_trading_strategy, inputs=[field, paper_num], outputs=strategy_output)
            field_clear.click(lambda: ["美股", 3, ""], None, [field, paper_num, strategy_output])

        with backtest_group:
            field = gr.Textbox(lines=1, visible=True, value="美股", label="Choose your application field: ")
            strategy = gr.Text(label="Enter yout trading strategy. Then it will generate a backtest code.", value="只要5MA大於今天的股價就買入")
            with gr.Row():
                backtest_btn = gr.Button("Submit")
                backtest_clear = gr.Button("Clear")
            # backtest_output = gr.Textbox(label="Backtest Code")
            backtest_output = gr.Markdown("", line_breaks=True, label="Backtest Code")
            backtest_btn.click(generate_backtest_code, inputs=[field, strategy], outputs=backtest_output)
            backtest_clear.click(lambda: ["美股", "只要5MA大於今天的股價就買入", ""], None, [field, strategy, backtest_output])

    # demo.launch(debug=True, server_name='140.112.30.188', server_port=14828)
    demo.launch(debug=True, server_port=14828)
