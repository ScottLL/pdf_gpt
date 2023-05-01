from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain import OpenAI, VectorDBQA
from langchain.document_loaders import DirectoryLoader
import os


openai_api_key = os.environ.get("OPENAI_API_KEY")

class Document:
    def __init__(self, content, metadata=None):
        self.page_content = content
        self.metadata = metadata if metadata else {}

def load_documents_from_directory(directory_path):
    file_paths = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f)) and f.endswith('.txt')]
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
        return None
    try:
        docsearch = Chroma.from_documents(texts, embeddings)
        return docsearch
    except Exception as e:
        return None

def create_vector_dbqa(llm, chain_type, vectorstore):
    qa = VectorDBQA.from_chain_type(llm=llm, chain_type=chain_type, vectorstore=vectorstore)
    return qa

def run_query(texts, query, openai_api_key):
    if not texts:
        return "No text files found."
    try:
        embeddings = create_openai_embeddings(openai_api_key)
        docsearch = create_chroma_vector_store(texts, embeddings)
        if docsearch:
            llm = OpenAI()
            chain_type = "stuff"
            qa = create_vector_dbqa(llm, chain_type, docsearch)
            num_docs = len(texts)
            qa.vectorstore.num_results = min(4, num_docs)  # Limit the number of results to the number of documents
            result = qa.run(query)
            return result
        else:
            return "Error creating vector store."
    except Exception as e:
        return f"Error: {e}"

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
