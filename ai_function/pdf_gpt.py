import os
from langchain.document_loaders import UnstructuredPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
import pinecone

def process_pdf(pdf_file, openai_api_key):
    loader = UnstructuredPDFLoader(pdf_file)
    data = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(data)
    PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
    PINECONE_API_ENV = os.environ.get("PINECONE_API_ENV")
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_API_ENV)
    index_name = "langchain1"
    docsearch = Pinecone.from_texts([t.page_content for t in texts], embeddings, index_name=index_name)
    
    return docsearch

def get_answer(docsearch, question, openai_api_key):
    docs = docsearch.similarity_search(question, include_metadata=True)

    llm = OpenAI(temperature=0, openai_api_key=openai_api_key)
    chain = load_qa_chain(llm, chain_type="stuff")
    result = chain.run(input_documents=docs, question=question)

    return result
