from search.search_engine import inverted_index_search
from search.vector_index import vector_index_search
from common.utils import get_sentence_inverted_result, get_sentence_vector_result, parse_text
from search import inverted_index, vector_index
from template.prompt import doc_qa_prompt
from http import HTTPStatus
import dashscope
from dashscope import Generation
from dashscope.api_entities.dashscope_response import Role
import yaml
key_file = open('key.yml', 'r', encoding='utf-8')
keys = yaml.safe_load(key_file)
dashscope.api_key  = keys['dashscope_key']


def complete_doc_human_input(inverted_index, vector_index, human_input):
    inverted_index_results = inverted_index_search(inverted_index, human_input, k=10)
    vector_index_results = vector_index_search(vector_index, human_input, k=10)
    inverted_index_results = get_sentence_inverted_result(inverted_index_results)
    vector_index_results = get_sentence_vector_result(vector_index_results)

    results = []
    for x in inverted_index_results:
        if x not in results:
            results.append(x)

    for x in vector_index_results:
        if x not in results:
            results.append(x)

    print(results)
    results = '\n'.join(results)

    return doc_qa_prompt.format(document=results, question=human_input)
    

def compose_system(system_prompt):
    return {"role": "system", "content": system_prompt}


def compose_user(user_input):
    return {"role": "user", "content": user_input}


def predict(inputs, top_p, top_k, temperature, qa_type = '常规问答', chatbot=[], history=[], retry=False):
    print(f"chatbot 1: {chatbot}")
    chat_counter = len(history) // 2
    print(f"chat_counter - {chat_counter}")
    system_prompt = '你是一个智能答疑助手。'
    messages = [compose_system(system_prompt)]
    if chat_counter:
        for data in chatbot:
            temp1 = {}
            temp1["role"] = "user"
            temp1["content"] = data[0]
            temp2 = {}
            temp2["role"] = "assistant"
            temp2["content"] = data[1]
            if temp1["content"] != "":
                messages.append(temp1)
                messages.append(temp2)
            else:
                messages[-1]['content'] = temp2['content']
    if retry and chat_counter:
        chatbot = chatbot[:-1]
        messages.pop()
        inputs = messages[-1]['content']
    else:
        content = inputs
        if qa_type == '文档问答':
            content = complete_doc_human_input(inverted_index, vector_index, inputs)
        temp3 = {}
        temp3["role"] = "user"
        temp3["content"] = content
        messages.append(temp3)
        chat_counter += 1


    history.append(inputs)
    responses = Generation.call(
        Generation.Models.qwen_max,
        messages=messages,
        result_format='message',  
        stream=True,
        top_p=top_p,
        top_k=top_k,
        temperature=temperature
    )

    full_content = ""
    token_counter = 0
    chatbot.append((history[-1], ""))
    for response in responses:
        if response.status_code == HTTPStatus.OK:
            full_content = response.output.choices[0]['message']['content']
            if token_counter == 0:
                history.append(" " + full_content)
            else:
                history[-1] = parse_text(full_content)
            chatbot[-1] = (history[-2], history[-1])
            token_counter += 1
            yield chatbot, history
        else:
            print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                response.request_id, response.status_code,
                response.code, response.message
            ))
            chatbot.pop()
            chatbot.append((history[-1], f"☹️发生了错误<br>返回值：{response.code}<br>异常：{response.message}"))
            history.pop()
            yield chatbot, history
            break