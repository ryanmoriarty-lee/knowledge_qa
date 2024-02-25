import os
import logging
import PyPDF2
from tqdm import tqdm
from common.pdf_func import parse_pdf
from common.utils import get_file_hash
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader
from langchain.text_splitter import _split_text_with_regex
from langchain.vectorstores import FAISS
from langchain.embeddings import DashScopeEmbeddings
from typing import List
import re

import yaml
key_file = open('key.yml', 'r', encoding='utf-8')
keys = yaml.safe_load(key_file)
dashscope_key  = keys['dashscope_key']

class CustomTextSplitter(RecursiveCharacterTextSplitter):
    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        final_chunks = []
        separator = separators[-1]
        new_separators = []

        for i, _s in enumerate(separators):
            _separator = _s if self._is_separator_regex else re.escape(_s)
            if _s == "":
                separator = _s
                break
            if re.search(_separator, text):
                separator = _s
                new_separators = separators[i + 1 :]
                break

        _separator = separator if self._is_separator_regex else re.escape(separator)
        splits = _split_text_with_regex(text, _separator, self._keep_separator)

        _good_splits = []
        _separator = "" if self._keep_separator else separator

        for s in splits:
            s = s.strip()
            if self._length_function(s) < self._chunk_size:
                _good_splits.append(s)
            else:
                if _good_splits:
                    final_chunks.extend(_good_splits)
                    _good_splits = []

                if not new_separators:
                    final_chunks.append(s)
                else:
                    other_info = self._split_text(s, new_separators)
                    final_chunks.extend(other_info)

        if _good_splits:
            final_chunks.extend(_good_splits)

        return final_chunks

def get_documents(file_src):
    text_splitter = CustomTextSplitter(
        separators=[".", "!", "?", "。", "！", "？"]
    )

    documents = []
    logging.debug("正在加载文档...")

    for file in file_src:
        filepath = file
        filename = os.path.basename(filepath)
        file_type = os.path.splitext(filename)[1]

        logging.info(f"正在加载文件: {filename}")
        texts = None

        try:
            if file_type == ".pdf":
                logging.debug("加载 PDF...")
                try:
                    pdftext = parse_pdf(filepath, False).text
                except:
                    pdftext = ""
                    with open(filepath, "rb") as pdfFileObj:
                        pdfReader = PyPDF2.PdfReader(pdfFileObj)
                        for page in tqdm(pdfReader.pages):
                            pdftext += page.extract_text()
                texts = [Document(page_content=pdftext, metadata={"source": filepath})]
            elif file_type == ".docx":
                logging.debug("加载 Word...")
                from langchain.document_loaders import UnstructuredWordDocumentLoader
                loader = UnstructuredWordDocumentLoader(filepath)
                texts = loader.load()
            elif file_type == ".txt":
                logging.debug("加载文本文件...")
                loader = TextLoader(filepath, "utf8")
                texts = loader.load()
        except Exception as e:
            logging.error(f"加载文件时发生错误: {filename}\n{e}")

        if texts is not None:
            texts = text_splitter.split_documents(texts)
            documents.extend(texts)

    logging.debug("文档加载完成.")
    return documents

def init_vector_index(
    vector_index_path,
    file_src,
    load_from_cache_if_possible=True,
):
    index_name = get_file_hash(file_paths=file_src)
    index_path = os.path.join(vector_index_path, index_name)

    embeddings = DashScopeEmbeddings(
        model="text-embedding-v2", dashscope_api_key=dashscope_key
    )

    if os.path.exists(index_path) and load_from_cache_if_possible:
        logging.info("找到缓存的索引文件，正在加载...")
        return FAISS.load_local(index_path, embeddings)
    else:
        try:
            documents = get_documents(file_src)
            logging.info("正在构建索引...")
            index = FAISS.from_documents(documents, embeddings)
            logging.debug("索引构建成功!")
            os.makedirs(f"{vector_index_path}", exist_ok=True)
            index.save_local(index_path)
            logging.debug("索引已本地保存!")
            return index
        except Exception as e:
            logging.error(f"索引构建失败! {e}")
            return None

def vector_index_search(index, query_string, k=-1):
    results = index.similarity_search_with_score(query_string)
    results = sorted(results, key=lambda x: x[1])
    if k != -1:
        results = results[:k]
    return results

