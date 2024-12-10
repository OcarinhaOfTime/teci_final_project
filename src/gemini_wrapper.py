import google.generativeai as genai


def configure():
    api_key = open('../auth/gemini_key.txt').read()
    genai.configure(api_key=api_key)

def create_embedding(txt):
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=txt)
    
    return result['embedding']

def ask(prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    r = model.generate_content(prompt)
    return r.text