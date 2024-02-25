import os
import re
import docx
import fitz
import logging

def read_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def read_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page_num in range(doc.page_count):
        page = doc[page_num]
        text += page.get_text()
    return text

def read_docx(file_path):
    doc = docx.Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def preprocess_documents(input_path, separator='[.!?。！？]'):
    new_documents = []

    if os.path.isdir(input_path):
        for root, dirs, files in os.walk(input_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    new_documents.extend(process_single_file(file_path, separator))
                except Exception as e:
                    logging.error(f"处理文件时发生错误：{file_path} - {e}")
    elif os.path.isfile(input_path):
        try:
            new_documents.extend(process_single_file(input_path, separator))
        except Exception as e:
            logging.error(f"处理文件时发生错误：{input_path} - {e}")
    else:
        logging.error("输入路径既不是文件夹也不是文件。")
    return new_documents

def process_single_file(file_path, separator):
    content = ""
    sentences = []
    if file_path.endswith('.txt'):
        content = read_txt(file_path)
    elif file_path.endswith('.pdf'):
        content = read_pdf(file_path)
    elif file_path.endswith('.docx') or file_path.endswith('.doc'):
        content = read_docx(file_path)

    sentences = re.split(separator, content)
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
    return sentences
