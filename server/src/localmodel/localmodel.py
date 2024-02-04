from langchain.llms import LlamaCpp

from google.colab import drive
drive.mount('/content/drive')

llm_cpp = LlamaCpp(
            streaming = True,
            model_path="/content/drive/MyDrive/LLM_Model/zephyr-7b-beta.Q4_K_M.gguf",
            n_gpu_layers=2,
            n_batch=512,
            temperature=0.75,
            top_p=1,
            verbose=True,
            n_ctx=4096
            )


query = "Who is Elon Musk?"

prompt = f"""
 <|system|>
You are an AI assistant that follows instruction extremely well.
Please be truthful and give direct answers
</s>
 <|user|>
 {query}
 </s>
 <|assistant|>
"""

response = llm_cpp.predict(prompt)
print(response)