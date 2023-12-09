from whoosh.index import create_in, open_dir
from jieba.analyse import ChineseAnalyzer
from data.document_processor import preprocess_documents
from whoosh.fields import *
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



def init_index(index_path, document_path):
    schema = Schema(extra_info=TEXT(stored=True, analyzer=ChineseAnalyzer()),
                content=TEXT(stored=True, analyzer=ChineseAnalyzer()))
    index = load_index(index_path, document_path, schema)
    return index

