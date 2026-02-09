# -------------- Modules ------------
from langchain_community.document_loaders import PyMuPDFLoader,TextLoader,YoutubeLoader
import os
from pathlib import Path

# ------------ Note ---------------

# Document = MetaData + Content (Langchain Document)

# -------------- Code -------------

class BaseSource:
    def extract(self):
        raise NotImplementedError


class PDFsource(BaseSource):
    def __init__(self,repo_path):
        self.repo_path=repo_path
        self.documents=None
        self.extract()
        
    def extract(self):    
        self.documents=[]
        try:
            pdf_repo=Path(self.repo_path)                   # Creates Path object (helps in alien OS)
            pdf_files=list(pdf_repo.glob("**/*.pdf"))       # Searches for pdf files only in entire repo and list because glob function returns generator(yield)
            
            print(f"Total PDFs found:{len(pdf_files)}")  
            
            for pdf_file in pdf_files:
                print(f"Processing:{pdf_file.name}")
                
                pdf_loader=PyMuPDFLoader(pdf_file)
                document=pdf_loader.load()
                
                for doc in document:
                    doc.metadata["source_file"]=pdf_file.name
                    doc.metadata["file_type"]='PDF'
                
                self.documents.extend(document)
                print(f"{len(document)} pages loaded")
                # breakpoint()
            return self.documents
                
        except Exception as e:
            print(f"Error: {e}")    
                    
                    
class TXTsource(BaseSource):
    def __init__(self,repo_path):
        self.repo_path=repo_path
        self.documents=None
        self.extract()
                    
    def extract(self):
        self.documents=[]
        try:
            txt_repo=Path(self.repo_path)
            txt_files=list(txt_repo.glob("**/*.txt"))
            
            print(f"Total Txt Files found:{len(txt_files)}")
            
            for txt_file in txt_files:
                print(f"Processing:{txt_file.name}")
                
                txt_loader=TextLoader(txt_file)
                document=txt_loader.load()
                
                for doc in document:
                    doc.metadata["source_file"]=txt_file.name
                    doc.metadata["file_type"]='txt'
                    
                self.documents.extend(document)
            print(f"{len(document)} Txt File Loaded")
            return self.documents
                
        except Exception as e:
            print(f"Error: {e}")
                    
                    
class YTsource(BaseSource):
    def __init__(self,yt_url):
        self.yt_url=yt_url
        self.transcript=None
        self.extract()

    def extract(self):
        try:
            yt_loader=YoutubeLoader.from_youtube_url(
                self.yt_url,
                add_video_info=False
            )
            self.transcript=yt_loader.load()
            for i in self.transcript:
                i.metadata["source"]="YouTube"
                i.metadata["file_type"]="Youtube Transcript" 
            return self.transcript    
            
        except Exception as e:
            print(f"Error: {e}")
            print("Some issue with url")
            
                            
class IngestionManager: 

    def __init__(self):
        self.sources = []
        self.documents=None

    def add_source(self, source):
        self.sources.extend(source.extract())       # extract keyword extracts important words from documents

    def run(self):
        self.documents = []
        
        self.documents.extend(self.sources)
        return self.documents       # -> List[Document]
    
    print("------------- Ingestion Completed ----------------")
    