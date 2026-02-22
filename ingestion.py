# -------------- Modules ------------
from langchain_community.document_loaders import PyMuPDFLoader,TextLoader,YoutubeLoader,JSONLoader,UnstructuredPDFLoader
import os
from pathlib import Path
# from langchain.schema import Document
from langchain_core.documents import Document

#-------------

# import sys
# !{sys.executable} -m pip install pytesseract

import fitz
import pytesseract
from pdf2image import convert_from_path

#----------

# ------------ Note ---------------

# Document = MetaData + Content (Langchain Document)

# -------------- Code -------------

class BaseSource:
    def extract(self):
        raise NotImplementedError
    
    
class JSONsource(BaseSource):
    def __init__(self, repo_path, ignore_files=None):
        self.repo_path=repo_path
        self.documents=None
        self.ignore_files = ignore_files if ignore_files else []
        # self.extract()

    def extract(self):
        self.documents=[]
        try:
            json_repo=Path(self.repo_path)                   
            json_files=list(json_repo.glob("**/*.jsonl"))+\
                       list(json_repo.glob("**/*.json"))
                       
            if json_files:           
            
                print(f"Total JSONs found:{len(json_files)}")  
                
                for json_file in json_files:
                    if json_file.name in self.ignore_files:
                        print(f"Skipping {json_file.name} (already processed)")
                        continue
                        
                    print(f"Processing:{json_file.name}")
                    
                    json_loader=JSONLoader(json_file,
                                        jq_schema='.',
                                        json_lines=True,
                                        text_content=False)
                    document=json_loader.load()
                    
                    for doc in document:
                        
                        # text=doc.get("text", "")
                        text=doc.page_content
                    
                        data=Document(
                            page_content=text,
                            metadata={
                                "source_file":json_file.name,
                                "file_type":"JSON File"
                            }
                        )
                    
                        self.documents.append(data)
                    
                    # for doc in document:
                    #     doc.metadata["source_file"]=json_file.name
                    #     doc.metadata["file_type"]='JSONL'
                    
                    # self.documents.extend(document)
                    print(f"{len(document)} pages loaded")
                    print("*******************Workingggggggggg***********************")
                    # breakpoint()
                # return json_files
            
            else:
                print("No JSON files found")
        except Exception as e:
            print(f"Error: {e}")   
        return self.documents
        
        
class PDFsource(BaseSource):
    def __init__(self, repo_path, ignore_files=None):
        self.repo_path=repo_path
        self.documents=None
        self.ignore_files = ignore_files if ignore_files else []
        
    def extract(self):   
        self.documents=[]
        try:
            pdf_repo=Path(self.repo_path)                   # Creates Path object (helps in alien OS)
            pdf_files=list(pdf_repo.glob("**/*.pdf"))       # Searches for pdf files only in entire repo and list because glob function returns generator(yield)
            
            if pdf_files:
            
                print(f"Total PDFs found:{len(pdf_files)}")  

#-----------------------------
                
                for pdf_file in pdf_files:
                    if pdf_file.name in self.ignore_files:
                        print(f"Skipping {pdf_file.name} (already processed)")
                        continue
                        
                    print(f"Processing:{pdf_file.name}")
                    
                    try:
                        doc=fitz.open(str(pdf_file))
                    except Exception as e:
                        print("Error Opening{pdf_file.name}")    
                        continue
                    
                    for page_num, page in enumerate(doc):
                        
                        # 1. Attempt to extract digital text
                        text = page.get_text()
                        
                        # 2. Hybrid Check: If text is sparse, assume scanned image -> Run OCR
                        # You can adjust the threshold (currently 50 characters)
                        if len(text.strip()) < 50:
                            print(f"  > Page {page_num + 1} seems scanned. Running OCR...")
                            
                            try:
                                # Convert specific page to image
                                # fmt='jpeg' and dpi=300 improves OCR accuracy
                                images = convert_from_path(
                                    str(pdf_file), 
                                    first_page=page_num + 1, 
                                    last_page=page_num + 1,
                                    dpi=300
                                )
                                
                                # Run Tesseract on the image
                                if images:
                                    text = pytesseract.image_to_string(images[0])
                            
                            except Exception as ocr_error:
                                print(f"    OCR failed for page {page_num + 1}: {ocr_error}")
                                # Fallback: keep the empty/short text or mark as unreadable
                    pdf_loader=PyMuPDFLoader(pdf_file)
                    # pdf_loader=UnstructuredPDFLoader(pdf_file)
                    
                    
#-----------------------------                    
                    
                    
                    
                                    
                # for pdf_file in pdf_files:
                #     print(f"Processing:{pdf_file.name}")
                    
                #     # pdf_loader=PyMuPDFLoader(pdf_file,extract_images=True)
                #     pdf_loader=UnstructuredPDFLoader(pdf_file)

                    
                    document=pdf_loader.load()
                        
                    for doc in document:
                        
                        text=doc.page_content
                    
                        data=Document(
                            page_content=text,
                            metadata={
                                "source_file":pdf_file.name,
                                "file_type":"PDF"
                            }
                        )
                        # self.documents.extend(data)
                        self.documents.append(data)    
                    
                    print(f"{len(document)} pages loaded")
                    
        except Exception as e:
            print(f"Error: {e}")
        return self.documents
                    
                    
class TXTsource:
    def __init__(self, repo_path, ignore_files=None):
        self.repo_path=repo_path
        self.documents=None
        self.ignore_files = ignore_files if ignore_files else []
                    
    def extract(self):
        self.documents=[]
        try:
            txt_repo=Path(self.repo_path)
            txt_files=list(txt_repo.glob("**/*.txt"))
            
            if txt_files:
            
                print(f"Total Txt Files found:{len(txt_files)}")
                
                for txt_file in txt_files:
                    if txt_file.name in self.ignore_files:
                        print(f"Skipping {txt_file.name} (already processed)")
                        continue
                        
                    print(f"Processing:{txt_file.name}")
                    
                    txt_loader=TextLoader(txt_file)
                    document=txt_loader.load()
                    
                    for doc in document:
                        doc.metadata["source_file"]=txt_file.name
                        doc.metadata["file_type"]='txt'
                        
                    self.documents.extend(document)
                print(f"Txt Files Loaded")
                
        except Exception as e:
            print(f"Error: {e}")
        return self.documents
                    
                    
class YTsource:
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
            
            if yt_loader:
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
        print("Data Extractedddd......")
        
    def run(self):
        self.documents = []
    
        self.documents.extend(self.sources)
        print("------------- Ingestion Completed ----------------")
        return self.documents       # -> List[Document]