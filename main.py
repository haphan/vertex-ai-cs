import os
from dotenv import load_dotenv
from datetime import datetime
import streamlit as st
# from streamlit_chat import message
from utils import *
from langchain.chat_models import ChatVertexAI
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)
from settings import Settings
from persist import insert_bq

settings = Settings()

#Page Config
st.set_page_config(
     layout="wide",
     page_title=settings.streamlit_page_title,
)

#Sidebar
# st.sidebar.header("OnPoint Cu")
# st.sidebar.markdown(
#     "A place for me to experiment different LLM use cases, models, application frameworks and etc."
# )

#Main Page and Chatbot components
st.title(settings.streamlit_page_title)

if 'responses' not in st.session_state:
    st.session_state['responses'] = [settings.streamlit_welcome_msg]
    print(streamlit_session())

if 'requests' not in st.session_state:
    st.session_state['requests'] = []

llm = ChatVertexAI(model_name=settings.llm_model_chat, 
        max_output_tokens=settings.llm_max_output_tokens, 
        temperature=settings.llm_temperature, 
        top_p=settings.llm_top_p,
        top_k=settings.llm_top_k
        )

if 'buffer_memory' not in st.session_state:
            st.session_state.buffer_memory=ConversationBufferWindowMemory(k=3,return_messages=True)

system_msg_template = SystemMessagePromptTemplate.from_template(template=settings.prompt_template.system)
human_msg_template = HumanMessagePromptTemplate.from_template(template="{input}")
prompt_template = ChatPromptTemplate.from_messages([system_msg_template, MessagesPlaceholder(variable_name="history"), human_msg_template])
conversation = ConversationChain(memory=st.session_state.buffer_memory, prompt=prompt_template, llm=llm, verbose=True)

response_container = st.container()
textcontainer = st.container()

if 'something' not in st.session_state:
    st.session_state.something = ''

def submit():
    st.session_state.something = st.session_state.input
    st.session_state.input = ''

with textcontainer:
    query = st.text_input("Câu hỏi: ", key="input", on_change=submit)
    submitted_query = st.session_state.something

    if submitted_query:
        st.session_state.requests.append(submitted_query)

        with st.spinner("Đang trả lời..."):
            conversation_history = get_conversation_history()
            refined_query = query_refiner(conversation_history, submitted_query)

            print(f'Submitted query: {submitted_query}')
            print(f'Refined query: {refined_query}')

            context, source, score = find_match(refined_query)
            if score < settings.trust_score_min:
                response = settings.prompt_template.default_no_answer
            else:                
        
                response = conversation.predict(
                                        input=f""
                                          f"Ngữ cảnh:\n"
                                          f"================\n"
                                          f"{context}\n"
                                          f"================\n"
                                          f"Câu hỏi:\n"
                                          f"================\n"
                                          f"{submitted_query} \n"
                                          f"================\n"
                                          f"Trả lời:\n")
                response += f"\n\n\nNguồn: {source}"
        
        
        st.session_state.responses.append(response) 

        # Persist message after sending to client
        if settings.store_chat_msg:
            insert_bq(
                session_id=streamlit_session(), 
                dt=datetime.now(),
                ask=submitted_query,
                response=response,
                ref=source
            )

with response_container:
    if st.session_state['responses']:

        for i in range(len(st.session_state['responses'])):
            with st.chat_message(name='ai', avatar='https://i.imgur.com/rxCLBMJ.png'):
                st.write(st.session_state['responses'][i])
            if i < len(st.session_state['requests']):
                # message(st.session_state["requests"][i], is_user=True,key=str(i)+ '_user')
                with st.chat_message(name='human'):
                    st.write(st.session_state["requests"][i])
