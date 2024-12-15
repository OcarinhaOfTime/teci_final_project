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

    #semantic search request to get context to llm
    results = semantic_search(query)
    answer = {"documents": [{"text": txt, "distance": distance, "information": metadata} for idx, (txt,distance, metadata) in enumerate(zip(results['documents'][0], results['distances'][0], results['metadatas'][0]))]}

    prompt_info = compose_info(answer['documents'])
    answer["prompt_info"] = prompt_info

    #load prompt templates
    template = open('../metadata/template.md').read()
    ans_template = open('../metadata/answer_template.json').read()
    prompt = template.format(query=query, ans_template=ans_template, info=prompt_info)
    answer["prompt"] = prompt

    #gemini llm request
    gemini_answer = gemini_ask(prompt)

    #precessing gemini answer
    gemini_json = json.dumps(json.loads(extract_json(gemini_answer.text)))
    answer["gemini_answer"] = json.loads(gemini_json)

    return jsonify(answer)

@app.route('/validation', methods=['GET'])
def get_validation():
    #get parameters
    query = request.args.get('text')
    answer = request.args.get('answer')
    context = request.args.get('context')

    #load prompt templates
    template = open('../metadata/validation_template.md').read()
    validation_js_template = open('../metadata/valid_js_template.json').read()
    prompt = template.format(query=query, answer=answer, context=context, valid_js_template=validation_js_template)

    #gemini llm request
    gemini_answer = gemini_ask(prompt)

    return jsonify(json.loads(extract_json(gemini_answer.text)))

@app.route('/anotherAnswer', methods=['GET'])
def get_another_answer():
    #get parameters
    query = request.args.get('text')
    wrong_answer = request.args.get('answer')
    context = request.args.get('context')

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