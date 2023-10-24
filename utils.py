import pprint
import os
from dotenv import load_dotenv
import pinecone
import vertexai
import streamlit as st
from vertexai.language_models import TextGenerationModel
from vertexai.language_models import TextEmbeddingModel


load_dotenv()
pp = pprint.PrettyPrinter(indent=4)

model= TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
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

def query_refiner(conversation, query):
    model = TextGenerationModel.from_pretrained("text-bison@001")
    response = model.predict(
    prompt=f"Given the following user query and conversation log, formulate a question that would be the most relevant to provide the user with an answer from a knowledge base.\n\nCONVERSATION LOG: \n{conversation}\n\nQuery: {query}\n\nRefined Query:",
    temperature=0.2,
    top_p=0.5,
    top_k=20
    )
    return response.text


def get_conversation_history():
    conversation_string = ""
    for i in range(len(st.session_state['responses'])-1):
        
        conversation_string += "Human: "+st.session_state['requests'][i] + "\n"
        conversation_string += "Bot: "+ st.session_state['responses'][i+1] + "\n"
    return conversation_string