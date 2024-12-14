import chromadb, json
from tqdm import tqdm
from llama_index.embeddings.gemini import GeminiEmbedding
import chromadb.utils.embedding_functions as embedding_functions

# Example setup of the client to connect to your chroma server
client = chromadb.HttpClient(host='localhost', port=8000)

api_key = open('../auth/gemini_key.txt').read()

# model_name = "models/embedding-001"
# embed_model = GeminiEmbedding(
#     model_name=model_name, api_key=api_key, title="this is a document"
# )
embed_model  = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=api_key)

collection = client.get_or_create_collection(name="rag_tec_ufpel", embedding_function=embed_model)

parsed_folder = '../BData/parsed_data/'

js = json.loads(open(f'{parsed_folder}corpus.json', encoding="utf-8").read())


for idx, it in tqdm(enumerate(js), total=len(js)):
    txt, emb, doc, page = it['txt'], it['emb'], it['doc'], it['page']
    txt = txt.replace("'", '')
    collection.add(
        documents=[txt],
        # embeddings=[emb],
        metadatas=[{"doc": doc, "page": page}],
        ids=[f"document{doc}_page{page}_{idx}"]
    )