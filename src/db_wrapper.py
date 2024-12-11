import psycopg2

def execute_query(query, commit=False, fetch=False):
    conn = psycopg2.connect("dbname=emb user=vagner")
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