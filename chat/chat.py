from langchain.memory import ConversationBufferWindowMemory
from search.search_engine import inverted_index_search
from search.vector_index import vector_index_search
from common.utils import get_sentence_inverted_result, get_sentence_vector_result, parse_text
from search import inverted_index, vector_index
from template.prompt import doc_qa_prompt
import json, requests
 
system_prompt = """你是一名大语言模型助手，用户回答用户的各种问题。""" 
API_URL = "https://api.openai.com/v1/chat/completions"


def complete_doc_human_input(inverted_index, vector_index, human_input):
    inverted_index_results = inverted_index_search(inverted_index, human_input, k=2)
    vector_index_results = vector_index_search(vector_index, human_input, k=2)
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


def predict(inputs, top_p, temperature, openai_api_key, qa_type = '常规问答', chatbot=[], history=[], retry=False):
    print(f"chatbot 1: {chatbot}")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }

    chat_counter = len(history) // 2
    print(f"chat_counter - {chat_counter}")

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
        messages.pop()
    else:
        content = inputs
        if qa_type == '文档问答':
            content = complete_doc_human_input(inverted_index, vector_index, inputs)
        temp3 = {}
        temp3["role"] = "user"
        temp3["content"] = content
        messages.append(temp3)
        chat_counter += 1

    payload = {
        "model": "gpt-3.5-turbo-1106",
        "messages": messages,  
        "temperature": temperature, 
        "top_p": top_p,
        "n": 1,
        "stream": True,
        "presence_penalty": 0,
        "frequency_penalty": 0,
    }

    history.append(inputs)
    print(f"payload is - {payload}")
    response = requests.post(API_URL, headers=headers,
                             json=payload, stream=True)

    token_counter = 0
    partial_words = ""

    counter = 0
    chatbot.append((history[-1], ""))
    for chunk in response.iter_lines():
        if counter == 0:
            counter += 1
            continue
        counter += 1
        if chunk:
            try:
                if len(json.loads(chunk.decode()[6:])['choices'][0]["delta"]) == 0:
                    break
            except Exception as e:
                chatbot.pop()
                chatbot.append((history[-1], f"☹️发生了错误<br>返回值：{response.text}<br>异常：{e}"))
                history.pop()
                yield chatbot, history
                break
            partial_words = partial_words + \
                json.loads(chunk.decode()[6:])[
                    'choices'][0]["delta"]["content"]
            if token_counter == 0:
                history.append(" " + partial_words)
            else:
                history[-1] = parse_text(partial_words)
            chatbot[-1] = (history[-2], history[-1])
            token_counter += 1
            yield chatbot, history
