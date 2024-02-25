from .inverted_index import init_inverted_index
from .vector_index import init_vector_index
import yaml
from common.utils import get_all_files_in_directory

yaml_file =  open('config.yml', 'r', encoding='utf-8')
config = yaml.safe_load(yaml_file)
document_path = config.get('Paths', {}).get('document_path', '.')
inverted_index_path = config.get('Paths', {}).get('inverted_index_path', '.')
vector_index_path = config.get('Paths', {}).get('vector_index_path', '.')

inverted_index = init_inverted_index(inverted_index_path, document_path)
vector_index = init_vector_index(vector_index_path, get_all_files_in_directory(document_path))