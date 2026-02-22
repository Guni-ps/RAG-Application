# streamlit run app.py

# --------- Modules -----------

repo_path="/user_data"

import os
import streamlit as st

from ingestion import PDFsource, TXTsource, JSONsource, IngestionManager
from chunks import Chunking
from vectordb import EmbeddingManager,VectorDatabase
from retriever import RAGretriever
from llm import QwenLLM, OpenRouterLLM, GeminiLLM
from chat_history import ChatHistoryManager

@st.cache_resource
def load_models():
    embedder = EmbeddingManager()
    vector_db = VectorDatabase()
    retriver = RAGretriever(embedder, vector_db)
    # llm = QwenLLM()
    # llm = OpenRouterLLM()
    llm=GeminiLLM()
    return embedder, vector_db, retriver, llm

embedder, vector_db, retriver, llm = load_models()

#------------------

st.sidebar.title("Upload Data:")

# st.title("Chat with your RAG Agent")
st.title("RAG Agent\n")
# st.title("......................")

with st.sidebar.form("Upload Data",clear_on_submit=True):
        uploaded_files=st.file_uploader(label="",accept_multiple_files=True)
        docs_submitted=st.form_submit_button()
        
    
if not os.path.exists(repo_path):
    os.mkdir(repo_path)
        
if docs_submitted and uploaded_files:
    for uploaded_file in uploaded_files:
        save_path = os.path.join(repo_path, uploaded_file.name)
        with open(save_path,"wb") as f:
            f.write(uploaded_file.getbuffer())
            # f.write(uploaded_file)
        st.sidebar.success(f"{uploaded_file.name} Saved")

    # Collect all extensions from the uploaded files
    uploaded_extensions = {os.path.splitext(f.name)[1].lower() for f in uploaded_files}

    existing_files = vector_db.get_existing_files()

    with st.spinner("Ingesting and Indexing documents..."):
        # 1. Initialize Ingestion Manager
        ingestion = IngestionManager()
        
        # 2. Add sources conditionally based on uploaded file types
        if ".pdf" in uploaded_extensions:
            ingestion.add_source(PDFsource(repo_path, ignore_files=existing_files))
            
        if ".txt" in uploaded_extensions:
            ingestion.add_source(TXTsource(repo_path, ignore_files=existing_files))
            
        if ".json" in uploaded_extensions or ".jsonl" in uploaded_extensions:
            ingestion.add_source(JSONsource(repo_path, ignore_files=existing_files))
        
        # 3. Run extraction
        documents = ingestion.run()
        
        if documents:
            # 4. Chunking
            chunker = Chunking()
            chunks = chunker.TextSplitting(documents)
            
            # 5. Embedding & Vector Storage
            embeddings = embedder.generate_embeddings(chunks)
            
            vector_db.add_documents(chunks, embeddings)
            
            st.success(f"Ingestion Complete! Processed {len(documents)} documents.")
        else:
            st.warning("No content extracted from the uploaded files.")

# Initialize Chat DB
chat_db = ChatHistoryManager()

# Session Management
if "session_id" not in st.session_state:
    st.session_state.session_id = "default_user"

session_id = st.sidebar.text_input("Session ID", value=st.session_state.session_id)
st.session_state.session_id = session_id

# Load History
if "messages" not in st.session_state or st.session_state.get("last_session_id") != session_id:
    st.session_state.messages = chat_db.get_history(session_id)
    st.session_state.last_session_id = session_id

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if query := st.chat_input("Ask Question from your Docs"):
    # 1. Handle User Input
    st.session_state.messages.append({"role": "user", "content": query})
    chat_db.add_message(session_id, "user", query)
    with st.chat_message("user"):
        st.write(query)

    # 2. Generate Response
    with st.spinner("Generating..."):
        retrieved_docs = retriver.retrive(str(query))
        response = llm.generate_response(query, retrieved_docs)

    # 3. Handle Assistant Response
    st.session_state.messages.append({"role": "assistant", "content": response})
    chat_db.add_message(session_id, "assistant", response)
    with st.chat_message("assistant"):
        st.write(response)
