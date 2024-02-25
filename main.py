from common.log import setup_logging
from webui.webui import get_web_ui
import os
import yaml

setup_logging()

web_ui = get_web_ui()
web_ui.queue().launch(share=False) 