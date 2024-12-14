import chromadb, json
import chromadb.utils.embedding_functions as embedding_functions
import re


def semantic_search(query):
    client = chromadb.HttpClient(host='localhost', port=8000)

    api_key = open('../auth/gemini_key.txt').read()
    embed_model  = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=api_key)
    collection = client.get_or_create_collection(name="rag_tec_ufpel", embedding_function=embed_model)

    results = collection.query(
        query_texts=[query],
        n_results=3
    )
    print("kkk ", results['metadatas'][0])
    return(results)

def compose_info(db_answer):
    info = ''
    for document in db_answer:
        info += '\n'
        info += f'## Document {document["information"]["doc"]}, Page {document["information"]["page"]}\n'
        info += document["text"]
        info += '\n'
        # print("mmm ", document)
    
    print(info)
    return info

def extract_json(txt):
        m = re.match('```json(.+)```', txt, re.DOTALL)
        if m is None:
            return txt
        
        return m.group(1).strip() 