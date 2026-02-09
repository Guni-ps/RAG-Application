# ------------- Modules --------------

import numpy as np
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import uuid
import os


# ------------- Embedding --------------

class EmbeddingManager:
    def __init__(self,model_name: str="all-MiniLM-L6-v2"):
        self.model_name=model_name
        self.model=None
        self._load_model()
        
    def _load_model(self):
        try:
            print(f"Loading embedding model:{self.model_name}")    
            self.model=SentenceTransformer(self.model_name)
            print(f"Model loaded successfully. Embedding dimension: {self.model.get_sentence_embedding_dimension()}")
        except Exception as e:
            print(f"Error loading model {self.model_name}:{e}")
            raise

    def generate_embeddings(self,data:list[str]) -> np.ndarray:
        
        if not self.model:
            raise ValueError("Model not loaded....")
        texts=[]
        for i in data:
            texts.append(i.page_content)
        
        print(f"Generating embeddings for {len(texts)} texts...")
        embeddings=self.model.encode(texts,show_progress_bar=True)
        print(f"Generated embeddings with shape: {embeddings.shape}")
        return embeddings
    
        print("------------- Embedding Completed ----------------")
        
        
# ----------- VECTOR DATABASE -------------

class VectorDatabase:
    def __init__(self,collection_name: str="documents",persist_directory: str="../data/vector_score"):
        self.collection_name=collection_name
        self.persist_directory=persist_directory
        self.client=None
        self.collection=None
        self._initialize_store()       
        
    def _initialize_store(self):
        try:
            os.makedirs(self.persist_directory,exist_ok=True)
            self.client=chromadb.PersistentClient(path=self.persist_directory)
            
            self.collection=self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description":"Embedded documents for RAG"}
            )
            print(f"Vector store initialized,Collection:{self.collection_name}")
            print(f"Existing documents in collection: {self.collection.count()}")
            
            
        except Exception as e:
            print(f"Error initialization vector store: {e}")    
            
    def add_documents(self,documents,embeddings):

        if len(documents) != len(embeddings):
            raise ValueError("Number of documents must match number of embeddings")
        
        print(f"Adding {len(documents)} documents to vector store...")
        
        ids=[]
        metadatas=[]
        documents_text=[]
        embeddings_list=[]
        
        for i,(doc,embedding) in enumerate(zip(documents,embeddings)):
            doc_id=f"doc_{uuid.uuid4().hex[:8]}_{i}"
            ids.append(doc_id)
            
            metadata=dict(doc.metadata)
            metadata["doc_index"]=i
            metadata["content_length"]=len(doc.page_content)
            metadatas.append(metadata)
            
            documents_text.append(doc.page_content)
            embeddings_list.append(embedding.tolist())
            
            
        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings_list,
                metadatas=metadatas,
                documents=documents_text
            )
            print(f"Successfully added {len(documents)} documents to vector store") 
            print(f"Total documents in collection:{self.collection.count()}")
           
        except Exception as e:
            print("Error adding documents to vector store: {e}")    
            raise
        
        print("------------- VectorDatabse Working ----------------")