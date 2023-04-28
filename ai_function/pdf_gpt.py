import streamlit as st
from langchain.document_loaders import UnstructuredPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
import pinecone
import os 
# from dotenv import load_dotenv
import tempfile

# load_dotenv()

# OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_API_ENV = os.environ.get("PINECONE_API_ENV")

def process_pdf(pdf_file,openai_api_key):
    # Load PDF file
    loader = UnstructuredPDFLoader(pdf_file)
    data = loader.load()
    # st.write(f'You have {len(data)} document(s) in your data')
    st.write(f'There are {len(data[0].page_content)} characters in your document')

    # Chunk the data up into smaller documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(data)
    st.write(f'We split you PDF to {len(texts)} documents as ChatGPT input.')

    # Create embeddings of your documents to get ready for semantic search
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    # Initialize Pinecone
    pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_API_ENV)
    index_name = "langchain1"
    docsearch = Pinecone.from_texts([t.page_content for t in texts], embeddings, index_name=index_name)
    
    return docsearch

def get_answer(docsearch, question, openai_api_key):
    # Query the documents to get the most similar ones
    docs = docsearch.similarity_search(question, include_metadata=True)

    # Use OpenAI to generate an answer to the question
    llm = OpenAI(temperature=0, openai_api_key=openai_api_key)
    chain = load_qa_chain(llm, chain_type="stuff")
    result = chain.run(input_documents=docs, question=question)

    # Return the answer
    return result

def pdf_gpt(openai_api_key):
    st.markdown("## :mag_right: :green[PDF Question Answering ]")

    # File upload
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
    
    if uploaded_file is not None:
        # Save uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
            tmpfile.write(uploaded_file.read())
            tmpfile_path = tmpfile.name

        if "docsearch" not in st.session_state:
            # Process PDF
            st.session_state.docsearch = process_pdf(tmpfile_path, openai_api_key)
            st.success("PDF file processed successfully.")

    else:
        st.warning("Please upload a PDF file.")
        return

    # Initialize the history
    if "history" not in st.session_state:
        st.session_state.history = []

    # User input
    question = st.text_input("Question", label_visibility="collapsed")

    submit_button = st.button("Submit question")

    if submit_button and question:
        # Get answer
        answer = get_answer(st.session_state.docsearch, question, openai_api_key)

        # Add the question and answer to the history
        st.session_state.history.append((question, answer))

    # Display the history of questions and answers
    for i, (q, a) in enumerate(st.session_state.history):
        st.write(f"Q{i + 1}: {q}")
        st.write(f"A{i + 1}: {a}")

    # Remove the temporary file after processing
    if uploaded_file is not None:
        os.remove(tmpfile_path)
