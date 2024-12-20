from flask import Flask, make_response, json, request, jsonify
from flask_ngrok import run_with_ngrok
from chromadb_util import semantic_search, compose_info, extract_json, gemini_ask
import json, re
import google.generativeai as genai


app = Flask(__name__)

app.config['JSON_SORT_KEYS'] = False

# @app.route('/validation', methods=['POST'])
def get_validation(query, answer, context):
    #get parameters
    # data = request.get_json()
    # query = data['text']
    # answer = data['answer']
    # context = data['context']

    #load prompt templates
    template = open('../metadata/validation_template.md').read()
    validation_js_template = open('../metadata/valid_js_template.json').read()
    prompt = template.format(query=query, answer=answer, context=context, valid_js_template=validation_js_template)

    #gemini llm request
    gemini_answer = gemini_ask(prompt)

    return json.loads(extract_json(gemini_answer.text))

    # @app.route('/anotherAnswer', methods=['POST'])
def get_another_answer(query, wrong_answer, context):
    #get parameters
    # data = request.get_json()
    # query = data['text']
    # wrong_answer = data['answer']
    # context = data['context']

    #load prompt templates
    template = open('../metadata/another_answer_template.md').read()
    answer_template = open('../metadata/answer_template.json').read()
    prompt = template.format(query=query, wrong_answer=wrong_answer, context=context, ans_template=answer_template)

    #gemini llm request
    gemini_answer = gemini_ask(prompt)

    #precessing gemini answer
    gemini_json = json.dumps(json.loads(extract_json(gemini_answer.text)))

    return json.loads(gemini_json)

def json_response(data, prompt, documents_answer, validation=False, another_answer=False,second_validation=False, show_documents=False, show_prompt=False):
#generate json response
    answer = {
        "prompt": prompt if show_prompt == "true" else None,
        "gemini_answer": data,
        "validation": validation,
        "second_gemini_answer": another_answer,
        "second_validation": second_validation, 
        "documents_list": documents_answer if show_documents == "true" else None
    }
    return jsonify(answer)

@app.route('/answer', methods=['GET'])
def get_answer():
    #get parameters
    query = request.args.get('text')
    show_documents = request.args.get('showDocuments')
    show_prompt = request.args.get('showPrompt')

    #semantic search request to get context to llm
    results = semantic_search(query)
    documents_answer = {
        "total_documents": len(results['documents'][0]),
        "documents": [{"text": txt, "distance": distance, "information": metadata} for idx, (txt,distance, metadata) in enumerate(zip(results['documents'][0], results['distances'][0], results['metadatas'][0]))]
        }

    prompt_info = compose_info(documents_answer['documents'])

    query_transform_template = open('../metadata/query_transform_template.md').read()
    query_ans_template = open('../metadata/transform_answer_template.json').read()
    # transform_prompt = query_transform_template.format(query=query, ans_template=query_ans_template)
    # gemini_transform = gemini_ask(transform_prompt)
    # transform_json = json.dumps(json.loads(extract_json(gemini_transform.text)))

    #load prompt templates
    template = open('../metadata/template.md').read()   
    ans_template = open('../metadata/answer_template.json').read()
    prompt = template.format(query=query, ans_template=ans_template, info=prompt_info)

    #gemini llm request
    gemini_answer = gemini_ask(prompt)

    #precessing gemini answer
    gemini_answer = json.loads(json.dumps(json.loads(extract_json(gemini_answer.text))))

    if gemini_answer["answer_exists_in_context"] == False:
        return json_response(gemini_answer, prompt, documents_answer,show_documents=show_documents, show_prompt=show_prompt)
    elif gemini_answer["answer_exists_in_context"] == True:
        print("Validating gemini answer")
        validation = get_validation(query, gemini_answer["answer"], prompt_info)
        if validation["acceptable"] == True:
            return json_response(gemini_answer, prompt, documents_answer, validation=validation, show_documents=show_documents, show_prompt=show_prompt)
        elif validation["acceptable"] == False:
            print("Getting another gemini answer")
            another_answer = get_another_answer(query, gemini_answer["answer"], prompt_info)
            if another_answer["answer_exists_in_context"] == False:
                return json_response(gemini_answer, prompt, documents_answer, validation=validation, another_answer=another_answer, show_documents=show_documents, show_prompt=show_prompt)
            elif another_answer["answer_exists_in_context"] == True:
                print("Validating gemini answer again")
                second_validation = get_validation(query, another_answer["answer"], prompt_info)
                return json_response(gemini_answer, prompt, documents_answer, validation=validation, another_answer=another_answer, second_validation=second_validation, show_documents=show_documents, show_prompt=show_prompt)
                # if second_validation["acceptable"] == True:
                #     return json_response(gemini_answer, prompt, documents_answer, validation=validation, another_answer=another_answer, second_validation=second_validation, show_documents=show_documents, show_prompt=show_prompt)
                # elif second_validation["acceptable"] == False:
                #     return  json_response(gemini_answer, prompt, documents_answer, validation=validation, another_answer=another_answer, second_validation=second_validation, show_documents=show_documents, show_prompt=show_prompt)
    
    return "Internal ERROR", 500


if __name__ == "__main__":
    app.run(debug=True)