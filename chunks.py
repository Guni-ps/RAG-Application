from langchain_text_splitters import RecursiveCharacterTextSplitter


class Chunking:
    def __init__(self,chunk_size=1000,chunk_overlap=200):
        # self.data=data
        self.chunk_size=chunk_size
        self.chunk_overlap=chunk_overlap
        
    def TextSplitting(self,data):
        text_splitter=RecursiveCharacterTextSplitter(
            chunk_overlap=self.chunk_overlap,
            chunk_size=self.chunk_size,
            length_function=len,
            separators=["\n\n","\n"," ",""]
        )
        
        split_data=text_splitter.split_documents(data)
        print(f"Made {len(data)} into {len(split_data)} chunks")
        
        return split_data
    
    print("------------- Chunking Completed ----------------")