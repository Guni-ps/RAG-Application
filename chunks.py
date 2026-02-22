from langchain_text_splitters import RecursiveCharacterTextSplitter,RecursiveJsonSplitter

class Chunking:
    def __init__(self,chunk_size=500,chunk_overlap=50):   # should return list[str]
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
        
    # def JsonSplitting(sef,data):
    #     json_splitter=RecursiveJsonSplitter(max_chunk_size=300)        
    #     json_chunks=json_splitter.split_json(data)