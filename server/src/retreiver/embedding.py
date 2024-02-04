from konlpy.tag import Okt
from soylemma import Lemmatizer
from rank_bm25 import BM25Okapi
from sklearn.metrics.pairwise import cosine_similarity
import re
import os 
import pickle
import openai

class Embedding:
    def __init__(self):
        self.__save_bm_dir = "./store/bmcontents.pkl"
        self.__save_openai_dir = ""
        self.__EMBEDDING_MODEL = "text-embedding-ada-002"

    def __find_elements_with_specific_value(self, tuple_list, target_value):
        result_list = [t[0] for t in tuple_list if t[1] == target_value]
        return result_list

    def __sentence_tokenizing(self, query):
        lemmatizer = Lemmatizer()

        t = Okt()
        stopwords=["의","가","이","은","들","는","좀","잘","걍","과","도","를","으로","자","에","와","한","하다"]
        query = re.sub(r"\uAC00-\uD7A30-9a-zA-Z\s","",query)

        lemm_sentence = []
        for text in t.pos(query):
            if text[0] in stopwords:
                continue
            result_lemm = self.__find_elements_with_specific_value(lemmatizer.lemmatize(text[0]),text[1])#0 텍스트 1 품사
            if len(result_lemm) == 0:
                lemm_sentence.append(text[0])
            else:
                lemm_sentence.append(result_lemm[0])

        return lemm_sentence

    def openai_embedding(self, content, url):
        try:
            contents = []
            if os.path.isfile(self.__save_openai_dir):
                with open(self.__save_openai_dir) as f:
                    load_content_info = pickle.load(f)
                    embedd_content = load_content_info["embedd_content"]
                    contents = load_content_info["content"]
                    urls = load_content_info["urls"]

            result = openai.embeddings.create(
                model = self.__EMBEDDING_MODEL,
                input=content
            )

            contents.append(content)
            result_content.append(result["data"][0]["embedding"])

            save_info = {
                "embedd_content": result_content,
                "origin_content": contents,
                "url": url
            }

            with open(self.__save_bm_dir, "wb") as f:
                pickle.dump(save_info, f)

        except Exception as e:
            print(f"error:{e}")
            return False,e
        return True, None

# 위에거 보고 수정이 필요함 content불러오는 부분에서...
    def bm25_embedding(self, content, url):
        try:
            origin_content = []
            if os.path.isfile(self.__save_bm_dir):
                with open(self.__save_bm_dir) as f:
                    load_content_info = pickle.load(f)
                    embedd_content = load_content_info["embedd_content"]
                    origin_content = load_content_info["origin_content"]

            result_content = self.__sentence_tokenizing(content)
            origin_content.append(result_content)
            embedd_content = BM25Okapi(origin_content)

            save_info = {
                "embedd_content": embedd_content,
                "origin_content": origin_content,
                "url": url
            }

            with open(self.__save_bm_dir, "wb") as f:
                pickle.dump(save_info, f)

        except Exception as e:
            print(f"error:{e}")
            return False,e
        return True, None
