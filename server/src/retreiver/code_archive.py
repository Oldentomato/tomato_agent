from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain import PromptTemplate
from langchain.chains import LLMChain
import os 
import json
import random 
import string
from util import get_openai_model

os.environ["TOKENIZERS_PARALLELISM"] = "false"

class FAISS_VectorStore:
    def __init__(self, model_name="BM-K/KoSimCSE-roberta", db_path="./vector_store", db_index="index_db", json_path="./vector_store/test.json", prompt_path="./prompt/summary_prompt.txt"):
        try:
            with open(prompt_path, "r") as f: 
                prompt_txt = f.read()
            llm = get_openai_model()
            sys_prompt = PromptTemplate(
                input_variables=["code_content"],
                template=prompt_txt
            )
            self.chain = LLMChain(llm=llm, prompt=sys_prompt)
            embeddings =  HuggingFaceEmbeddings(model_name=model_name)
            if not os.path.exists(json_path):
                with open(json_path, "w+") as f:
                    json.dump({}, f)

            with open(json_path) as f:
                self.__JSON_DATA = json.load(f)
            self.__JSON_PATH = json_path
            self.__DB_PATH = db_path
            self.__DB_INDEX = db_index
            if os.path.exists(os.path.join(self.__DB_PATH,"index.faiss")):
                print("load db...")
                self.__db = FAISS.load_local(folder_path=self.__DB_PATH, embeddings=embeddings)
            else:
                print("create db...")
                self.__db = FAISS.from_texts(["test_content"], embeddings)
        except:
            raise Exception("faiss initial error")

    def __len__(self):
        return self.__db.index.ntotal

    def __random_id(self, n=10):
        rand_str = ""
        for i in range(n):
            rand_str += str(random.choice(string.ascii_uppercase + string.digits))

        return rand_str

    def add_contents(self, content, summary, save_serial=True):
        generate_key = self.__random_id()
        try:
            self.__db.add_texts([(summary)],metadatas=[{"key":generate_key}])
            self.__JSON_DATA[generate_key] = content
        except Exception as e:
            return False, f"error to save texts: {e}"
        else:
            if save_serial:
                with open(self.__JSON_PATH, "w") as f:
                    json.dump(self.__JSON_DATA, f)
                self.__db.save_local(self.__DB_PATH)
            else:
                pass
                #직렬화가 필요해지면 추가할것
            return True, ""

    #코드 자동 분석 후 요약
    def summary(self, code):
        summary_result = self.chain.run({"code_content": code})
        return summary_result


    def delete_text(self, key):
        pass

    def retrieval(self, query):
        docs = self.__db.similarity_search_with_score(query)
        print(docs[0])
        result_key = docs[0][0].metadata['key']
        result = self.__JSON_DATA[result_key]
        return {
            "summary": docs[0][0].page_content,
            "result": result
        }

__vector = FAISS_VectorStore(model_name="./model/")

def get_vectorstore():
    return __vector

