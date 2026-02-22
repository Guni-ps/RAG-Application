# ------------- Modules -------------------

from ingestion import TXTsource,PDFsource,YTsource,JSONsource,IngestionManager
from chunks import Chunking
from vectordb import EmbeddingManager,VectorDatabase
from retriever import RAGretriever
from llm import QwenLLM

# ----------- Data Paths ----------------

repo_path="/Users/Priyanshu/Documents/Projects/RAG/Data"        
url="https://youtu.be/c8QXUrvSSyg?si=qhISVQ0UT5N87Pk1"

# ---------- Actual Main ---------------

class RAGpipeline:
    def __init__(self,TXTsource,PDFsource,YTsource,JSONsource,IngestionManager,Chunking,EmbeddingManager,VectorDatabase,RAGretriever,QwenLLM):
        
        self.TXTsource=TXTsource
        self.PDFsource=PDFsource
        self.YTsource=YTsource
        self.JSONsource=JSONsource
        self.IngestionManager=IngestionManager
        self.Chunking=Chunking
        self.EmbeddingManager=EmbeddingManager
        self.VectorDatabase=VectorDatabase
        self.RAGretriever=RAGretriever
        self.QwenLLM=QwenLLM

#         pdf_data=self.PDFsource(repo_path)
#         # txt_data=self.TXTsource(repo_path)
#         # yt_data=self.YTsource(url)
#         # json_data=self.JSONsource(repo_path)
#         ingestion=IngestionManager()
# # ingestion.add_source(yt_data)
#         ingestion.add_source(pdf_data)
# # # # ingestion.add_source(txt_data)
# # # # ingestion.add_source(json_data)

#         data=ingestion.run()

#         chunker=Chunking()
#         chunks=chunker.TextSplitting(data)

#         embeddings=EmbeddingManager().generate_embeddings(chunks)

#         VectorDatabase().add_documents(chunks,embeddings)

        query="logistic regression"

        retriever=self.RAGretriever(EmbeddingManager(),VectorDatabase())
        retrieved_docs=retriever.retrive(query)
        print(retrieved_docs)


# llm=QwenLLM()
# response=llm.generate_response(query,retrieved_docs)

# print(f"Response:\n{response}")



# --------------------  

RAGpipeline(TXTsource,PDFsource,YTsource,JSONsource,IngestionManager,Chunking,EmbeddingManager,VectorDatabase,RAGretriever,QwenLLM)