import os
import logging

import PyPDF2
from tqdm import tqdm
from vector_index.pdf_func import parse_pdf
from common.utils import get_file_hash
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader
from langchain.text_splitter import _split_text_with_regex
from langchain.vectorstores import FAISS
from typing import List
import re


class customTextSplitter(RecursiveCharacterTextSplitter):
    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        """Split incoming text and return chunks."""
        final_chunks = []
        # Get appropriate separator to use
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
    text_splitter = customTextSplitter(
        separators = ['\n\n', '\n',' ', '\t', ".", "!", "?", ";", "。", "！", "？", "；"]
    )

    documents = []
    logging.debug("Loading documents...")
    logging.debug(f"file_src: {file_src}")
    for file in file_src:
        filepath = file
        filename = os.path.basename(filepath)
        file_type = os.path.splitext(filename)[1]
        logging.info(f"loading file: {filename}")
        texts = None
        try:
            if file_type == ".pdf":
                logging.debug("Loading PDF...")
                try:
                    pdftext = parse_pdf(filepath, False).text
                except:
                    pdftext = ""
                    with open(filepath, "rb") as pdfFileObj:
                        pdfReader = PyPDF2.PdfReader(pdfFileObj)
                        for page in tqdm(pdfReader.pages):
                            pdftext += page.extract_text()
                texts = [Document(page_content=pdftext,
                                  metadata={"source": filepath})]
            elif file_type == ".docx":
                logging.debug("Loading Word...")
                from langchain.document_loaders import UnstructuredWordDocumentLoader
                loader = UnstructuredWordDocumentLoader(filepath)
                texts = loader.load()
            elif file_type == ".txt":
                logging.debug("Loading text file...")
                loader = TextLoader(filepath, "utf8")
                texts = loader.load()
        except Exception as e:
            import traceback
            logging.error(f"Error loading file: {filename}")
            traceback.print_exc()

        if texts is not None:
            texts = text_splitter.split_documents(texts)
            documents.extend(texts)
    logging.debug("Documents loaded.")
    return documents


def init_vector_index(
    vector_index_path,
    file_src,
    load_from_cache_if_possible=True,
):
    index_name = get_file_hash(file_paths=file_src)
    index_path = f"{vector_index_path}/{index_name}"

    embeddings = OpenAIEmbeddings()
    if os.path.exists(index_path) and load_from_cache_if_possible:
        logging.info("找到了缓存的索引文件，加载中……")
        return FAISS.load_local(index_path, embeddings)
    else:
        try:
            documents = get_documents(file_src)
            logging.info("构建索引中……")
            index = FAISS.from_documents(documents, embeddings)
            logging.debug("索引构建完成！")
            os.makedirs(f"{vector_index_path}", exist_ok=True)
            index.save_local(index_path)
            logging.debug("索引已保存至本地!")
            return index
        except Exception as e:
            import traceback
            logging.error("索引构建失败！%s", e)
            traceback.print_exc()
            return None