from data.document_processor import preprocess_documents
from search.index import init_index
from common.log import setup_logging

import yaml
                        
setup_logging()
with open('config.yml', 'r', encoding='utf-8') as yaml_file:
    config = yaml.safe_load(yaml_file)
    document_path = config.get('Paths', {}).get('document_path', '.')
    index_path = config.get('Paths', {}).get('index_path', 'inverted_index')
    index = init_index(index_path, document_path)


    from search.search_engine import search

    query_string = "你好，我是神里绫华，我喜欢中文和english"
    print(search(index, query_string))













# print(sentences)