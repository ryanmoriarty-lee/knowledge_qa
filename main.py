from data.document_processor import preprocess_documents
from search.inverted_index import init_inverted_index
from search.vector_index import init_vector_index
from search.search_engine import inverted_index
from common.log import setup_logging
from common.utils import get_all_files_in_directory
import os
import yaml
                        
setup_logging()
key_file = open('key.yml', 'r', encoding='utf-8')
keys = yaml.safe_load(key_file)
os.environ['OPENAI_API_KEY'] = keys.get('openai_key')

yaml_file =  open('config.yml', 'r', encoding='utf-8')
config = yaml.safe_load(yaml_file)
document_path = config.get('Paths', {}).get('document_path', '.')
inverted_index_path = config.get('Paths', {}).get('inverted_index_path', '.')
vector_index_path = config.get('Paths', {}).get('vector_index_path', '.')


index = init_inverted_index(inverted_index_path, document_path)
vector_index = init_vector_index(vector_index_path, get_all_files_in_directory(document_path))













# print(sentences)