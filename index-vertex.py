import os
from dotenv import load_dotenv
import nltk
import pinecone
import google.auth
from langchain.document_loaders import DirectoryLoader
from langchain.document_loaders import TextLoader
from langchain.document_loaders import GCSDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import VertexAIEmbeddings
from langchain.vectorstores import Pinecone

#function to split documents into chunk size
def split_docs(documents,chunk_size=1000,chunk_overlap=20):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    docs = text_splitter.split_documents(documents)
    return docs

def index_local():
    loader = DirectoryLoader('./data', glob="**/*.txt", show_progress=True, loader_cls=TextLoader)
    documents = loader.load()
    print(f'Loaded {len(documents)} documents using TextLoader')

    docs = split_docs(documents)
    embeddings = VertexAIEmbeddings(model_name="textembedding-gecko")
    print(os.getenv('PINECONE_API_KEY'))
    pinecone.init(
        api_key=os.getenv('PINECONE_API_KEY'),
        environment=os.getenv('PINECONE_ENV') 
        )
    index_name = os.getenv('PINECONE_IDX')
    Pinecone.from_documents(docs, embeddings, index_name=index_name)    



if __name__ == "__main__":
    load_dotenv()
    index_local()