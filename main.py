import os
from dotenv import load_dotenv
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
load_dotenv()

#Page Config
st.set_page_config(
     layout="wide",
     page_title="JS Lab",
     page_icon="https://api.dicebear.com/5.x/bottts-neutral/svg?seed=gptLAb"
)

#Sidebar
# st.sidebar.header("OnPoint Cu")
# st.sidebar.markdown(
#     "A place for me to experiment different LLM use cases, models, application frameworks and etc."
# )

#Main Page and Chatbot components
st.title("OnPoint Avenger CS team 🦸‍♀️")

if 'responses' not in st.session_state:
    st.session_state['responses'] = ["Xin chào! Em là Linh - nhân viên hỗ trợ của OnPoint. Em giúp được gì cho anh/chị?"]

if 'requests' not in st.session_state:
    st.session_state['requests'] = []

llm = ChatVertexAI(model_name="chat-bison-32k")
if 'buffer_memory' not in st.session_state:
            st.session_state.buffer_memory=ConversationBufferWindowMemory(k=3,return_messages=True)

system_msg_template = SystemMessagePromptTemplate.from_template(template="""
Bạn tên là Linh và là nhân viên chăm sóc hỗ trợ khách hàng của nhãn hàng OnPoint hỗ trợ các nhãn hàng như Johnson & Johnson, Obagi, Listerine. 

Không được nói mình là trợ lý ảo.

Trả lời trung thực nhất về thông tin của sản phẩm. Không tư vấn cho khách hàng về thông tin sản phẩm không có trong danh mục sản phẩm. Không đưa đường dẫn tới web website nào trong câu trả lời. 

Câu trả lời của bạn phải luôn lịch sự, bắt đầu câu trả lời bằng "dạ". Kết thúc câu trả lời bằng cám ơn. Gọi người hỏi bằng anh/chị.
Sử dụng emoji trong câu trả lời.

Câu trả lời nên ngắn gọn và không nên dài quá 200 chữ.
'""")
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
            # st.subheader("Refined Query:")
            # st.write(refined_query)
            context = find_match(refined_query)
            response = conversation.predict(input=f"Context:\n {context} \n\n Query:\n{submitted_query}")
        
        st.session_state.responses.append(response) 

with response_container:
    if st.session_state['responses']:

        for i in range(len(st.session_state['responses'])):
            with st.chat_message(name='ai', avatar='https://i.imgur.com/O7jZFEx.jpg'):
                st.write(st.session_state['responses'][i])
            if i < len(st.session_state['requests']):
                # message(st.session_state["requests"][i], is_user=True,key=str(i)+ '_user')
                with st.chat_message(name='human'):
                    st.write(st.session_state["requests"][i])
