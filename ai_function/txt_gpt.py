import streamlit as st
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain import OpenAI, VectorDBQA
from langchain.document_loaders import DirectoryLoader
import os
import tempfile
import shutil

class Document:
    def __init__(self, content, metadata=None):
        self.page_content = content
        self.metadata = metadata if metadata else {}

def load_documents_from_directory(directory_path):
    file_paths = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
    documents = []
    for file_path in file_paths:
        with open(file_path, "r") as f:
            content = f.read()
            doc = Document(content)  # Create a Document object with the content of the file
            documents.append(doc)
    return documents

def split_documents_into_chunks(documents, chunk_size, chunk_overlap):
    text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    texts = text_splitter.split_documents(documents)
    return texts

def create_openai_embeddings(openai_api_key):
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    return embeddings

def create_chroma_vector_store(texts, embeddings):
    if not texts:
        st.warning("No text files found.")
        return None
    try:
        print("Running Chroma using direct local API.")
        print("Using DuckDB in-memory for database. Data will be transient.")
        docsearch = Chroma.from_documents(texts, embeddings)
        return docsearch
    except Exception as e:
        st.error(f"Error creating vector store: {e}")
        return None

def create_vector_dbqa(llm, chain_type, vectorstore):
    qa = VectorDBQA.from_chain_type(llm=llm, chain_type=chain_type, vectorstore=vectorstore)
    return qa

def run_query(qa_object, query, num_docs):
    qa_object.vectorstore.num_results = min(4, num_docs)  # Limit the number of results to the number of documents
    result = qa_object.run(query)
    return result

def run_query_with_source_documents(qa_object, query, num_docs):
    qa_object.vectorstore.num_results = min(4, num_docs)  # Limit the number of results to the number of documents
    result = qa_object.run(query)
    if isinstance(result, dict):
        source_documents = result.get('source_documents', [])
        if source_documents:
            source_texts = [doc.page_content for doc in source_documents]
        else:
            source_texts = []
        return result['result'], source_texts
    else:
        return result, None



def folder_upload():
    uploaded_files = st.file_uploader("Upload one or more files", type=("txt", "text/plain"), accept_multiple_files=True)

    if uploaded_files:
        tmpdir = tempfile.mkdtemp()  # Create a temporary directory without a context manager
        for i, file in enumerate(uploaded_files):
            file_path = os.path.join(tmpdir, file.name)
            with open(file_path, 'wb') as f:
                f.write(file.read())
            st.write(f"File {i+1}: {file.name}")
        return tmpdir
    else:
        folder_path = st.text_input("Enter path to folder")
        print(f"Directory path: {folder_path}")
        return folder_path


def text_gpt(openai_api_key):
    st.title("Text Question Answering with GPT-3")

    # User input
    st.write("Upload a folder containing text files")
    directory_path = folder_upload()

    if directory_path:  # Add this condition
        documents = load_documents_from_directory(directory_path)
        
    st.write("Enter your question")
    query = st.text_input("Question")

    # Load documents from a directory
    if directory_path:
        # Load documents from the uploaded directory
        documents = load_documents_from_directory(directory_path)

        # Split the documents into smaller chunks
        chunk_size = 1000
        chunk_overlap = 0
        texts = split_documents_into_chunks(documents, chunk_size, chunk_overlap)
        # print("Texts:", texts)
        
        # Create embeddings using OpenAI
        api_key = openai_api_key
        embeddings = create_openai_embeddings(api_key)

        # Create vector store using Chroma
        docsearch = create_chroma_vector_store(texts, embeddings)

        # Create VectorDBQA object
        if docsearch:
            llm = OpenAI()
            chain_type = "stuff"
            qa = create_vector_dbqa(llm, chain_type, docsearch)

            # Run a query and return the result
            if query:
                num_docs = len(documents)
                result = run_query(qa, query, num_docs)
                st.write("Answer: ", result)

                # Run a query and return the source documents used to generate the result
                result, source_documents = run_query_with_source_documents(qa, query, num_docs)  # Pass num_docs here

                st.write("Source documents: ", source_documents)

                
        if directory_path.startswith(tempfile.gettempdir()):
            shutil.rmtree(directory_path)
        else:
            st.warning("No directory provided.")