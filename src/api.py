from flask import Flask, make_response, json, request, jsonify
from flask_ngrok import run_with_ngrok
from chromadb_util import semantic_search, compose_info, extract_json, gemini_ask
import json, re
import google.generativeai as genai


app = Flask(__name__)

app.config['JSON_SORT_KEYS'] = False

@app.route('/answer', methods=['GET'])
def get_answer():
    #get parameters
    query = request.args.get('text')
    show_documents = request.args.get('showDocuments')

    #semantic search request to get context to llm
    results = semantic_search(query)
    documents_answer = {"documents": [{"text": txt, "distance": distance, "information": metadata} for idx, (txt,distance, metadata) in enumerate(zip(results['documents'][0], results['distances'][0], results['metadatas'][0]))]}

    prompt_info = compose_info(documents_answer['documents'])

    query_transform_template = open('../metadata/query_transform_template.md').read()
    query_ans_template = open('../metadata/transform_answer_template.json').read()
    transform_prompt = query_transform_template.format(query=query, ans_template=query_ans_template)
    gemini_transform = gemini_ask(transform_prompt)
    transform_json = json.dumps(json.loads(extract_json(gemini_transform.text)))

    #load prompt templates
    template = open('../metadata/template.md').read()   
    ans_template = open('../metadata/answer_template.json').read()
    prompt = template.format(query=query, ans_template=ans_template, info=prompt_info)

    #gemini llm request
    gemini_answer = gemini_ask(prompt)

    #precessing gemini answer
    gemini_json = json.dumps(json.loads(extract_json(gemini_answer.text)))

    #generate json response
    if show_documents:
        answer = {
            "gemini_answer": json.loads(gemini_json),
            "gemini_query_transform": json.loads(transform_json),
            "prompt": prompt,
            "prompt_info": prompt_info,
            "documents": documents_answer['documents']
        }
    else:
        answer = {
            "gemini_answer": json.loads(gemini_json),
            "gemini_query_transform": json.loads(transform_json),
            "prompt": prompt,
            "prompt_info": prompt_info
        }

    return jsonify(answer)

@app.route('/validation', methods=['POST'])
def get_validation():
    #get parameters
    data = request.get_json()
    query = data['text']
    answer = data['answer']
    context = data['context']

    #load prompt templates
    template = open('../metadata/validation_template.md').read()
    validation_js_template = open('../metadata/valid_js_template.json').read()
    prompt = template.format(query=query, answer=answer, context=context, valid_js_template=validation_js_template)

    #gemini llm request
    gemini_answer = gemini_ask(prompt)

    return jsonify(json.loads(extract_json(gemini_answer.text)))

@app.route('/anotherAnswer', methods=['POST'])
def get_another_answer():
    #get parameters
    data = request.get_json()
    query = data['text']
    wrong_answer = data['answer']
    context = data['context']

    #load prompt templates
    template = open('../metadata/another_answer_template.md').read()
    answer_template = open('../metadata/answer_template.json').read()
    prompt = template.format(query=query, wrong_answer=wrong_answer, context=context, ans_template=answer_template)

    #gemini llm request
    gemini_answer = gemini_ask(prompt)

    #precessing gemini answer
    gemini_json = json.dumps(json.loads(extract_json(gemini_answer.text)))

    #generate json response
    answer = {
        "gemini_answer": json.loads(gemini_json),
        "prompt": prompt,
        "prompt_info": context
    }

    return jsonify(answer)

if __name__ == "__main__":
    app.run(debug=True)