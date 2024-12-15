import psycopg2, json
conn_str = "dbname=emb user=henry"

def execute_query(query, commit=False, fetch=False):
    conn = psycopg2.connect(conn_str)
    cur = conn.cursor()

    cur.execute(query)

    r = None
    if fetch:
        r = cur.fetchall()

    if commit:
        conn.commit()    

    cur.close()
    conn.close()

    return r

def insert(doc, page, emb, txt):
    query = f"INSERT INTO bcorpus (doc, page, embedding, txt) VALUES ({doc}, {page}, '{emb}', '{txt}');"
    execute_query(query, True)

def semantic_search(emb, lim=10):
    query = f"SELECT * FROM bcorpus ORDER BY embedding <-> '{emb}' LIMIT {lim};"
    return execute_query(query, fetch=True)

def retrieve(doc, page):
    query = f"SELECT * FROM bcorpus WHERE doc={doc} AND page={page-1}"
    return execute_query(query, fetch=True)[0]

def setup_pg():
    print('Setting up postgres')
    parsed_folder = '../BData/parsed_data/'
    conn = psycopg2.connect(conn_str) # Customize
    cur = conn.cursor()

    #cur.execute("CREATE EXTENSION vector;") # Execute this to enable embeddings, if this wasn't already
    cur.execute("CREATE TABLE bcorpus (id bigserial PRIMARY KEY, doc INT, page INT, txt VARCHAR(10000), embedding vector(768));")

    js = json.loads(open(f'{parsed_folder}corpus.json').read())

    for it in js:
        txt, emb, doc, page = it['txt'], it['emb'], it['doc'], it['page']
        txt = txt.replace("'", '')
        query = f"INSERT INTO bcorpus (doc, page, embedding, txt) VALUES ({doc}, {page}, '{emb}', '{txt}');"
        cur.execute(query)

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    setup_pg()