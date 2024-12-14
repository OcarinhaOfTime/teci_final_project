from flask import Flask, make_response, json, request, jsonify
from flask_ngrok import run_with_ngrok
from chromadb_util import semantic_search, compose_info, extract_json
import json, re
import google.generativeai as genai


app = Flask(__name__)

app.config['JSON_SORT_KEYS'] = False

@app.route('/answer', methods=['GET'])
def get_answer():
    query = request.args.get('text')
    results = semantic_search(query)
    answer = {"documents": [{"text": txt, "distance": distance, "information": metadata} for idx, (txt,distance, metadata) in enumerate(zip(results['documents'][0], results['distances'][0], results['metadatas'][0]))]}

    prompt_info = compose_info(answer['documents'])
    answer["prompt_info"] = prompt_info

    template = open('../metadata/template.md').read()
    ans_template = open('../metadata/answer_template.json').read()
    prompt = template.format(query=query, ans_template=ans_template, info=prompt_info)
    model = genai.GenerativeModel("gemini-1.5-flash")
    r = model.generate_content(prompt)
    teste = json.dumps(json.loads(extract_json(r.text)))
    answer["gemini_answer"] = json.loads(teste)
    return jsonify(answer)

@app.route('/validation', methods=['GET'])
def get_validation():
    print(request.args.get('text'))
    print(request.args.get('answer'))
    # return json.dumps(request), 200
    return json.dumps(True)

@app.route('/anotherAnswer', methods=['GET'])
def get_another_answer():
    print(request.args.get('text'))
    print(request.args.get('answer'))
    text = request.args.get('text')
    # return json.dumps(request), 200
    return make_response('Diferente resposta do Gemini')

if __name__ == "__main__":
    app.run(debug=True)