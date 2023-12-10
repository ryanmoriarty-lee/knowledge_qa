from whoosh.index import create_in, open_dir
from jieba.analyse import ChineseAnalyzer
from data.document_processor import preprocess_documents
from whoosh.fields import *
import pickle
import logging
import os

def add_document_to_index(index, documents):
    try:
        writer = index.writer()
        for doc in documents:
            writer.add_document(**doc)
        writer.commit()
    except Exception as e:
        logging.error(f"添加文档到索引时发生错误: {e}")

def load_index(index_path, document_path, schema):
    if not os.path.exists(index_path):
        os.mkdir(index_path)
        index = create_in(index_path, schema)
        sentences = preprocess_documents(document_path)
        documents = [{"content": sentence} for sentence in sentences]
        add_document_to_index(index, documents)
    else:
        index = open_dir(index_path)
    return index


def save_file_list(file_list, file_path):
    with open(file_path, 'wb') as f:
        pickle.dump(file_list, f)

def load_file_list(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            return pickle.load(f)
    else:
        return []

def update_index(index, documents, file_list):
    for file in file_list:
        if file not in documents:
            sentences = preprocess_documents(file)
            add_document_to_index([{"content": sentence} for sentence in sentences])

def init_inverted_index(index_path, document_path):
    schema = Schema(extra_info=TEXT(stored=True, analyzer=ChineseAnalyzer()),
                content=TEXT(stored=True, analyzer=ChineseAnalyzer()))
    index = load_index(index_path, document_path, schema)
    return index

