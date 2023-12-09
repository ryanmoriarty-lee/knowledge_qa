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
def preprocess_documents(document_path, separator='[.!?;。！？；]'):
    sentences = []

    for root, dirs, files in os.walk(document_path):
        for file in files:
            file_path = os.path.join(root, file)

            try:
                if file_path.endswith('.txt'):
                    sentences.extend(re.split(separator, read_txt(file_path)))

                elif file_path.endswith('.pdf'):
                    sentences.extend(re.split(separator, read_pdf(file_path)))

                elif file_path.endswith('.docx') or file_path.endswith('.doc'):
                    sentences.extend(re.split(separator, read_docx(file_path)))

            except Exception as e:
                logging.error(f"处理文件时发生错误：{file_path} - {e}")

    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    return sentences
