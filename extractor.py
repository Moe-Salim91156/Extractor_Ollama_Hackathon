import  requests
import  yaml
import  json
import sys
from PyPDF2 import PdfReader

def read_file   (path):
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def load_rules(path):
    with open(path, 'r') as file:
        data = yaml.safe_load(file)
    return data


def send_to_ollama(prompt, model):
    response = requests.post("http://localhost:11434/api/generate", json={"model": model, "prompt": prompt}, stream=True)
    return response

def ask_ollama(model, text, rules):
    fields = [f['name'] for f in rules['fields']]
    prompt = f"""Extract these fields from the text below and return valid JSON only: {fields} Text: {text}"""
# respone = requests.post("http://localhost:11434/api/generate", json={"model": model, "prompt": prompt}, stream=True)
    response = send_to_ollama(prompt,model)

    output = ""
    for line in response.iter_lines():
        if line:
            data = json.loads(line.decode())
            if "response" in data:
                output += data["response"]
    try:
        return json.loads(output)
    except:
        start = output.find("{")
        end = output.rfind("}") + 1
        cleaned = output[start:end]
        return json.loads(cleaned)


def process_files(file_path,rule_path):
    text = read_file(file_path)
    rules = load_rules(rule_path)
    result = ask_ollama("llama3",text, rules)
    print(json.dumps(result, indent=2))

file_path = sys.argv[1]
rules_path = sys.argv[2]
process_files(file_path, rules_path)
