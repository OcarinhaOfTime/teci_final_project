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

# client.delete_collection(name="rag_tec_ufpel")
collection = client.get_or_create_collection(name="rag_tec_ufpel", embedding_function=embed_model)

parsed_folder = '../tmp/'

js = json.loads(open(f'{parsed_folder}full_corpus.json', encoding="utf-8").read())

passed = 0
ignored = 0
for idx, it in tqdm(enumerate(js), total=len(js)):
    txt, emb, doc, page = it['txt'], it['emb'], it['doc'], it['page']
    txt = txt.replace("'", '')
    # print("text len: ", len(txt))
    if len(txt) <= 10000:
        collection.add(
            documents=[txt],
            # embeddings=[emb],
            metadatas=[{"doc": doc, "page": page}],
            ids=[f"document{doc}_page{page}_{idx}"]
        )
        passed += 1
    else:
        ignored += 1

print("passed: ", passed, "ignored: ", ignored)