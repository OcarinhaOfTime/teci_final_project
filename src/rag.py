
import db_wrapper as db
import gemini_wrapper as gemini
import re, json
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

    def compose_query_transform(self, query):
        template = open('../metadata/query_transform_template.md').read()
        prompt = template.format(query=query)
        return prompt

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
    
    def compose_val_prompt(self, query, answer, context):        
        template = open('../metadata/validation_template.md').read()
        vjs = open('../metadata/valid_js_template.json').read()
        prompt = template.format(query=query, answer=answer, context=context, valid_js_template=vjs)

        return prompt
    
    def compose_validation_report(self, txt):
        js = json.loads(self.extract_json(txt))
        ans = 'The answer is valid.' if js['acceptable'] else 'The answer is not valid.'
        ans += '\n'
        ans += js['explanation']
        return ans

    def extract_json(self, txt):
        m = re.match('```json(.+)```', txt, re.DOTALL)
        if m is None:
            return txt
        
        return m.group(1).strip()    

    def generate_sample_answer(self, query):
        print('Generating sample answer...')
        prompt = self.compose_query_transform(query)
        answer = gemini.ask(prompt)
        print(answer)

        return answer    

    def execute(self, query):
        self.log('Creating embedding...')
        trans_query = self.generate_sample_answer(query)        
        self.log(trans_query)


        self.log('semantic search...')
        emb = gemini.create_embedding(trans_query)
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

        #validation
        self.log('validating...')
        js_answer = json.loads(answer)
        answer = js_answer['answer']
        _, _, _, context, _ = db.retrieve(js_answer['doc'], js_answer['page'])

        val_prompt = self.compose_val_prompt(query, answer, context)        
        val_answer = gemini.ask(val_prompt)

        valid = self.compose_validation_report(val_answer)
        report_template = open('../metadata/report_template.md').read()
        report = report_template.format(query=query, answer=answer, context=context, valid=valid)
        self.log(val_answer)
        self.log('finished!')
        return report




if __name__ == "__main__":
    i = 3
    query = 'What is the maximum rating for RCBO in the small power system?'
    query = 'What are the two programming methods used for QUANTEC?'
    rag = Rag()
    report = rag.execute(query)
    open(f'../tmp/report{i}.md', 'w+').write(report)