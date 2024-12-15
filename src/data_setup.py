import google.generativeai as genai
import os, json
from pypdf import PdfReader
import db_wrapper as db
import gemini_wrapper as gemini
from pathlib import Path

api_key = open('../auth/gemini_key.txt').read()
genai.configure(api_key=api_key)

separator = '\n$$$\n'

# Parse
print('Parsing pdfs...')
pdf_paths = [
    '../BData/4326-2 - Kier - RUH Bath Cancer Centre - BUG - Technical User__S3 Suitable for Review and Comment_B.pdf',
    '../BData/Mech - Section 2 - Systems Description_Mech - Section 2 - Systems Description_S3 Suitable for Review and Comment_A.pdf',
    '../BData/5127-WSP-RP-MEP-001_MEP Specification_Costing_C02.pdf'
    ]

parsed_folder = '../BData/parsed_data/'
Path(parsed_folder).mkdir(parents=True, exist_ok=True)

for i in range(len(pdf_paths)):
    print('parsing', i)
    pdf_path = pdf_paths[i]
    reader = PdfReader(pdf_path)
    number_of_pages = len(reader.pages)
    txt = separator.join([page.extract_text() for page in reader.pages])
    open(f'{parsed_folder}{i}.txt', 'w+', encoding="utf-8").write(txt)

print('Creating embeddings...')
# Create db
min_thres = 500
corpus = []
for i in range(len(pdf_paths)):
    txt = open(f'../BData/parsed_data/{i}.txt', encoding="utf-8").read()
    pages = txt.split(separator)
    for k, txt in zip(range(len(pages)), pages):
        if len(txt) < min_thres:
            print(f'skipped emb doc {i} page {k}')    
            continue
        
        print(f'creating emb doc {i} page {k}')        
        emb = gemini.create_embedding(txt)
        corpus.append(
            {
                'txt':txt,
                'emb': emb,
                'doc':i,
                'page':k
            }
        )

open(f'{parsed_folder}corpus.json', 'w+', encoding="utf-8").write(json.dumps(corpus))


