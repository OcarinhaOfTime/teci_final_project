import psycopg2, json, yaml

auth = yaml.safe_load(open('../auth/db.yaml'))
dbname, user = auth['dbname'], auth['user']
conn_str = f"dbname={dbname} user={user}"
table_name = 'bcorpus'

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
    query = f"INSERT INTO {table_name} (doc, page, embedding, txt) VALUES ({doc}, {page}, '{emb}', '{txt}');"
    execute_query(query, True)

def delete_table():
    query = f'DROP TABLE {table_name};'
    execute_query(query, True)

def semantic_search(emb, lim=10):
    query = f"SELECT * FROM {table_name} ORDER BY embedding <-> '{emb}' LIMIT {lim};"
    return execute_query(query, fetch=True)

def retrieve(doc, page):
    query = f"SELECT * FROM {table_name} WHERE doc={doc} AND page={page-1}"
    return execute_query(query, fetch=True)[0]

def setup_pg():
    print('Setting up postgres')
    parsed_folder = '../BData/parsed_data/'
    conn = psycopg2.connect(conn_str) # Customize
    cur = conn.cursor()

    #cur.execute("CREATE EXTENSION vector;") # Execute this to enable embeddings, if this wasn't already
    cur.execute(f"CREATE TABLE {table_name} (id bigserial PRIMARY KEY, doc INT, page INT, txt VARCHAR(20000), embedding vector(768));")

    js = json.loads(open(f'{parsed_folder}corpus.json').read())

    for it in js:
        txt, emb, doc, page = it['txt'], it['emb'], it['doc'], it['page']
        txt = txt.replace("'", '')
        query = f"INSERT INTO {table_name} (doc, page, embedding, txt) VALUES ({doc}, {page}, '{emb}', '{txt}');"
        cur.execute(query)

    conn.commit()
    cur.close()
    conn.close()
    print('Setup finished')

if __name__ == "__main__":
    setup_pg()