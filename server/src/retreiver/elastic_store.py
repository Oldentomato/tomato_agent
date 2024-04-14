from langchain.vectorstores import ElasticVectorSearch
from langchain.embeddings import HuggingFaceEmbeddings
from util import get_openai_embedding
# from langchain_elasticsearch.chat_history import ElasticsearchChatMessageHistory


class ElasticStore:
    def __init__(self):
        self.embeddings = get_openai_embedding()
        self.index_name = "html_store"
        db = ElasticVectorSearch(elasticsearch_url="http://localhost:9200")


    def setup_embeddings():
        # Huggingface embedding setup
        print(">> Prep. Huggingface embedding setup")
        model_name = "sentence-transformers/all-mpnet-base-v2"
        return HuggingFaceEmbeddings(model_name=model_name)

    def store_text(self, data):
        db.from_texts(texts=[""],embedding=self.embeddings, metadatas=[{}], index_name=self.index_name)

    def search(self, query):
        return db.similarity_search(query)