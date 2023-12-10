from langchain.memory import ConversationBufferWindowMemory
from search.search_engine import inverted_index_search
from search.vector_index import vector_index_search
from common.utils import get_sentence_inverted_result
from common.utils import get_sentence_vector_result
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate 
from langchain.chains import LLMChain
from template.prompt import doc_qa_prompt
 
template = """Assistant is a large language model trained by OpenAI.
Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.
Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.
Overall, Assistant is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.

{history}
Human: {human_input}
Assistant:"""
 
prompt = PromptTemplate(
    input_variables=["history", "human_input"], 
    template=template
)
 
def get_chatbot(temperature=0.5, k=2):
    return  LLMChain(
        llm=OpenAI(temperature=0), 
        prompt=prompt, 
        verbose=True, 
        memory=ConversationBufferWindowMemory(k=2))


def complete_human_input(inverted_index, vector_index, human_input):
    inverted_index_results = inverted_index_search(inverted_index, human_input, k=2)
    vector_index_results = vector_index_search(vector_index, human_input, k=2)
    inverted_index_results = '\n'.join(get_sentence_inverted_result(inverted_index_results))
    vector_index_results = '\n'.join(get_sentence_vector_result(vector_index_results))
    return doc_qa_prompt.format(document=inverted_index_results + '\n' + vector_index_results, question=human_input)
    