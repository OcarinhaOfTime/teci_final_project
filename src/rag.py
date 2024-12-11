
import db_wrapper as db
import gemini_wrapper as gemini
import re
from datetime import datetime
import pandas as pd

class Rag:
    def __init__(self):
        gemini.configure()        
        self.ts = datetime.strftime(datetime.now(), '%y-%b-%d')
        self.context_size = 10 #pages

    def log(self, txt):
        print(txt)
        open(f'../logs/{self.ts}.txt', 'a+').write(txt + '\n')

    def log_data(self, txt):
        open(f'../logs/{self.ts}_data.txt', 'a+').write(txt + '\n')

    def compose_info(self, db_answer):
        info = ''
        for _, doc, page, txt, _ in db_answer:
            info += '\n'
            info += f'## Document {doc}, Page {page+1}\n'
            info += txt
            info += '\n'

        return info
    
    def extract_meta(self, db_answer):
        info = []
        for _, doc, page, txt, _ in db_answer:
            info.append([doc, page+1])

        return pd.DataFrame(info, columns=['Doc', 'Page'])


    def compose_prompt(self, query, db_answer):
        template = open('../metadata/template.md').read()
        ans_template = open('../metadata/answer_template.json').read()
        info = self.compose_info(db_answer)
        prompt = template.format(query=query, ans_template=ans_template, info=info)

        return prompt

    def extract_json(self, txt):
        m = re.match('```json(.+)```', txt, re.DOTALL)
        if m is None:
            return txt
        
        return m.group(1).strip()        

    def execute(self, query):
        self.log('Creating embedding...')
        emb = gemini.create_embedding(query)
        self.log('semantic search...')
        db_answer = db.semantic_search(emb, self.context_size)
        prompt = self.compose_prompt(query, db_answer)

        meta = self.extract_meta(db_answer)
        self.log(f'data used:\n{meta}')

        self.log('Asking gemini...')
        self.log_data(prompt)
        answer = gemini.ask(prompt)
        answer = self.extract_json(answer)
        self.log('received answer')
        self.log(answer)


query = 'What is the maximum rating for RCBO in the small power system?'
query = 'What are the two programming methods used for QUANTEC?'
rag = Rag()
rag.execute(query)