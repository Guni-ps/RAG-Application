# ------------ Notes ------------

# -> List[Dict[str, Any]]:  This is a return type hint, that this function should return 
#  query : str.   str is also a hint that parameter should be this datatype

from langchain_core.documents import Document



class RAGretriever:
    def __init__(self,EmbeddingManager,VectorDatabase):
        self.embedding_manager=EmbeddingManager
        self.vector_database=VectorDatabase

    def retrive(self, query : str, top_k : int=3 , score_threshold : float = 0.20) -> list[dict[str, any]]:    
        self.query=query
        self.top_k=top_k
        self.score_threshold=score_threshold

        print(f"Retriving Documents for query: {query}")
        print(f"Score Threshold: {score_threshold}\nTop K: {top_k}")
        
        query_embedded=self.embedding_manager.generate_embeddings_query([query])[0]
        
        try:
            results=self.vector_database.collection.query(
                query_embeddings=[query_embedded.tolist()],     # Converting a numpy array to nested list
                n_results=top_k
            )
            
            retrieved_docs=[]
            
            if results["documents"] and results["documents"][0]:
                documents=results["documents"][0]
                metadatas=results["metadatas"][0]
                distances=results["distances"][0]
                ids=results["ids"][0]
                
                for i,(doc_id,document,metadata,distance) in enumerate(zip(ids,documents,metadatas,distances)):
                    similarity_score=1-distance         # Similarity score (Cosine Similarity)
                    print(similarity_score)
                    
                    if similarity_score >= score_threshold:
                        # Merge metadata with retrieval stats
                        combined_metadata = metadata.copy() if metadata else {}
                        combined_metadata.update({
                            "id": doc_id,
                            "similarity_score": similarity_score,
                            "distance": distance,
                            "rank": i+1
                        })
                        
                        retrieved_docs.append(Document(
                            page_content=document,
                            metadata=combined_metadata
                        ))
                        
                print(f"Retrieved {len(retrieved_docs)} documents (after filtering)")                       
                # print(retrieved_docs)
                return retrieved_docs
            
            else:
                print("No Documents Found")
                
            
        except Exception as e:
            print(f"Error during retrieval:{e}")
            return []