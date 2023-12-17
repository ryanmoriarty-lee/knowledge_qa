from common.log import setup_logging
from webui.webui import get_web_ui
import os
import yaml

key_file = open('key.yml', 'r', encoding='utf-8')
keys = yaml.safe_load(key_file)
os.environ['OPENAI_API_KEY'] = keys.get('openai_key')         
setup_logging()


web_ui = get_web_ui()
web_ui.queue().launch(share=False) 