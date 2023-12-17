import gradio as gr
import os
import yaml
from chat.chat import predict

API_URL = "https://api.openai.com/v1/chat/completions"
key_file = open('key.yml', 'r', encoding='utf-8')
keys = yaml.safe_load(key_file)
open_ai_key = keys.get('openai_key')

def delete_last_conversation(chatbot, history):
    chatbot.pop()
    history.pop()
    history.pop()
    return chatbot, history


def get_file_names(dir, plain=False, filetype=".json"):
    try:
        files = [f for f in os.listdir(dir) if f.endswith(filetype)]
    except FileNotFoundError:
        files = []
    if plain:
        return files
    else:
        return gr.Dropdown.update(choices=files)


def reset_state():
    return [], []



def reset_textbox():
    return gr.update(value='')


def get_web_ui():
    title = """<h1 align="center">大语言模型知识库问答系统</h1>"""
    with gr.Blocks() as web_ui:
        gr.HTML(title)
        keyTxt = gr.Textbox(show_label=True, placeholder=f"在这里输入你的OpenAI API-key...", value=open_ai_key, label="API Key", type="password", visible=False).style(container=True)
        chatbot = gr.Chatbot() 
        history = gr.State([])
        TRUECOMSTANT = gr.State(True)

        with gr.Row():
            with gr.Column(scale=12):
                txt = gr.Textbox(show_label=False, placeholder="在这里输入").style(
                    container=False)
            with gr.Column(min_width=50, scale=1):
                submitBtn = gr.Button("🚀", variant="primary")
        with gr.Row():
            emptyBtn = gr.Button("🧹 新的对话")
            retryBtn = gr.Button("🔄 重新生成")
            delLastBtn = gr.Button("🗑️ 删除上条对话")
        with gr.Accordion("问答模式", open=True):
            qa_type = gr.inputs.Radio(["常规问答", "文档问答"], type="value", default="常规问答", label='选择大模型问答的模式', optional=False)
        with gr.Accordion("参数", open=True):
            top_p = gr.Slider(minimum=-0, maximum=1.0, value=1.0, step=0.05,
                          interactive=True, label="Top-p (nucleus sampling)",)
            temperature = gr.Slider(minimum=-0, maximum=5.0, value=1.0,
                                step=0.1, interactive=True, label="Temperature",)

        txt.submit(predict, [txt, top_p, temperature, keyTxt, qa_type, chatbot, history], [chatbot, history])
        txt.submit(reset_textbox, [], [txt])
        submitBtn.click(predict, [txt, top_p, temperature, keyTxt, qa_type, chatbot, history], [chatbot, history], show_progress=True)
        submitBtn.click(reset_textbox, [], [txt])
        emptyBtn.click(reset_state, outputs=[chatbot, history])
        retryBtn.click(predict, [txt, top_p, temperature, keyTxt, qa_type, chatbot, history, TRUECOMSTANT], [chatbot, history], show_progress=True)
        delLastBtn.click(delete_last_conversation, [chatbot, history], [chatbot, history], show_progress=True)
        return web_ui
