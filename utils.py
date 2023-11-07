import pprint
import os
from dotenv import load_dotenv
import pinecone
import vertexai
import streamlit as st
from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx
from vertexai.language_models import TextGenerationModel
from vertexai.language_models import TextEmbeddingModel
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.memory.chat_memory import BaseChatMemory

load_dotenv()
pp = pprint.PrettyPrinter(indent=4)

model= TextEmbeddingModel.from_pretrained("textembedding-gecko-multilingual@latest")
pinecone.init(api_key=os.getenv('PINECONE_API_KEY'), environment=os.getenv('PINECONE_ENV'))
index = pinecone.Index(os.getenv('PINECONE_IDX'))

def text_embedding(input) -> list:
    embeddings = model.get_embeddings([input])
    for embedding in embeddings:
        vector = embedding.values
        print(f"Length of Embedding Vector: {len(vector)}")
    return vector

def find_match(input: str) -> list[str, str, float]:
    input_em = text_embedding(input)
    result = index.query(input_em, top_k=2, includeMetadata=True)
    pp.pprint(result['matches'])
    
    context = result['matches'][0]['metadata']['text']+"\n"+result['matches'][1]['metadata']['text']
    score = max(result['matches'][0]['score'], result['matches'][1]['score'])
    source = result['matches'][0]['metadata']['source']
    return (context, source, score)

def query_refiner(conversation: str, query: str):
    model = TextGenerationModel.from_pretrained("text-bison@001")
    response = model.predict(
    prompt=f"Dưới đây là lịch sử nói chuyện giữa khách hàng và nhân viên chăm sóc khách hàng, "
            f"tóm tắt câu hỏi của khách hàng, bổ sung tên sản phẩm đang được tư vấn nếu có.\n\n"
            f"Lịch sử nói chuyện: \n=============\n{conversation}\n=============\n\nKhách hàng: \n=============\n{query}\n=============\n\nTóm tắt:",
    temperature=0.7,
    top_p=0.95,
    top_k=40
    )

    return response.text

def get_conversation_history():
    conversation_string = ""
    for i in range(len(st.session_state['responses'])-1):
        
        conversation_string += "Khách hàng: "+st.session_state['requests'][i] + "\n"
        conversation_string += "Nhân viên chăm sóc khách hàng: "+ st.session_state['responses'][i+1] + "\n"
    return conversation_string

def streamlit_session():
    return get_script_run_ctx().session_id    