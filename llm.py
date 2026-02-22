# api = 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

# --------Note-------

# AutoTokenizer creates tokens from user query for giving it to llm which is eligible or workable for specific llm model you are using


# ---------- Modules ------------

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os

from openai import OpenAI
from dotenv import load_dotenv

from google import genai


load_dotenv()

# -------------------------------

class QwenLLM:
    def __init__(self, model_name: str = "Qwen/Qwen2.5-1.5B-Instruct"):
        self.model_name = model_name
        
        # mps makes macos use gpu rather than cpu for fast performance
        if torch.backends.mps.is_available():
            self.device = torch.device("mps")
        else:
            self.device = torch.device("cpu")

        print(f"Loading tokenizer for {self.model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
        print(f"Loading model {self.model_name}...")
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            # float16 bit is better for low end system than the default float32
            # torch_dtype=torch.float16, 
            low_cpu_mem_usage=True 
        ).to(self.device)
        
        print("Model loaded successfully.")
        
    def generate_response(self,query,retrieved_docs):    
        self.query=query
        self.retrieved_docs=retrieved_docs
        
        context_text="--".join([doc.page_content for doc in self.retrieved_docs])        # join build a single large string
        
        
        prompt = [
        {
            "role": "system", 
            "content": f"You are a helpful assistant. Answer the user's question strictly using the following context.\n\nContext:\n{context_text}"
        },
        {
            "role": "user", 
            "content": self.query
        }
    ]
        
        text_prompt = self.tokenizer.apply_chat_template(
        prompt,
        tokenize=False,
        add_generation_prompt=True
        )
        
        model_inputs = self.tokenizer(text_prompt, return_tensors="pt").to(self.device)

        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=500,
            do_sample=True,
            temperature=0.4
        )
        
        response_ids = [
            output_ids[len(input_ids):] 
            for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        
        print(model_inputs.input_ids.shape)
    
        print("Generating Response...")
        
        
        response = self.tokenizer.batch_decode(response_ids, skip_special_tokens=True)[0]
        
        print("...Response Generated")
        
        return response
    
    
class GeminiLLM:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.model_name = model_name
        self.api_key = "AIzaSyB3EZmeFYfWN-BGvL-oi-SUQlb-oGGfz98"

        self.client = genai.Client(
            api_key=self.api_key
        )
        
    def generate_response(self, query, retrieved_docs):
        context_text = "\n\n".join([doc.page_content for doc in retrieved_docs])
        
        messages = f"""You are a helpful assistant. Answer the user's question strictly using the following context.
                    Context:\n{context_text}\n\nQuestion: {query} """
        print(messages)
        print("Generating Response via Gemini...")
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=messages,
            # max_tokens=1024
        )
        
        answer = response.text#.choices[0].message.content
        print(answer)
        print("...Response Generated")
        
        
        return answer
    
    
    
class OpenRouterLLM:
    def __init__(self, model_name: str = "arcee-ai/trinity-large-preview:free"):
        self.model_name = model_name
        self.api_key = "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"

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key
        )
        
    def generate_response(self, query, retrieved_docs):
        context_text = "\n\n".join([doc.page_content for doc in retrieved_docs])
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Answer the user's question strictly using the following context."},
            {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {query}"}
        ]
        
        print("Generating Response via OpenRouter...")
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            max_tokens=1024
        )
        
        answer = response.choices[0].message.content
        print("...Response Generated")
        
        return answer