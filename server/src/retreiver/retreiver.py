import pickle 
from soylemma import Lemmatizer
from konlpy.tag import Okt
import os.path
import os
import re
from datetime import datetime
from rank_bm25 import BM25Okapi


def _find_elements_with_specific_value(tuple_list, target_value):
    result_list = [t[0] for t in tuple_list if t[1] == target_value]
    return result_list

def _sentence_tokenizing(query):
    lemmatizer = Lemmatizer()

    t = Okt()
    stopwords=['의','가','이','은','들','는','좀','잘','걍','과','도','를','으로','자','에','와','한','하다']
    query = re.sub(r"[^\uAC00-\uD7A30-9a-zA-Z\s]", "", query)

    lemm_sentence = []
    for text in t.pos(query):
        if text[0] in stopwords:
            continue
        result_lemm = _find_elements_with_specific_value(lemmatizer.lemmatize(text[0]),text[1]) #0 = 텍스트, 1 = 품사
        if len(result_lemm) == 0:
            lemm_sentence.append(text[0])
        else:
            lemm_sentence.append(result_lemm[0])

    return lemm_sentence


def Search_Msg(name, query):
    with open(f'./out/{name}/bmvector.pkl', 'rb') as file:
        bm25 = pickle.load(file)
    with open(f'./out/{name}/content.pkl', 'rb') as file:
        doc_info = pickle.load(file)


    origin_content = doc_info["origin_content"]
    # content = doc_info["content"]
    source = doc_info["source"]

    new_query = _sentence_tokenizing(query)
    scores = bm25.get_scores(new_query)
    max_score_index = scores.argmax()

    # 원본, 날짜, 글쓴이
    return origin_content[max_score_index], source[max_score_index][0], source[max_score_index][1]



def Text_Embedding(name, datas):
    try:
        content = []
        source = []
        origin_content = []

        if os.path.exists(f'./out/{name}'):
            if os.path.isfile(f'./out/{name}/content.pkl'):
                with open(f'./out/{name}/content.pkl', 'rb') as f:
                    load_doc_info = pickle.load(f)
                    content = load_doc_info["content"]
                    origin_content = load_doc_info["origin_content"]
                    source = load_doc_info["source"]
        else:
            os.makedirs(f'./out/{name}')

        for data in datas:
            origin_content.append(data["content"])
            result_sentence = _sentence_tokenizing(data["content"])
            content.append(result_sentence)
            source.append((data["time"].strftime("%Y_%m_%d"),data["author"]))

        doc_info = {
            "content": content,
            "origin_content": origin_content,
            "source": source
        }


        bm25 = BM25Okapi(content)

        # save
        with open(f'./out/{name}/content.pkl', 'wb') as f:
            pickle.dump(doc_info, f)
        with open(f'./out/{name}/bmvector.pkl', 'wb') as file:
            pickle.dump(bm25, file)

    except Exception as e:
        print(f"error:{e}")
        return False, e
    
    return True, None   