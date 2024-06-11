from flask import Flask, request, render_template_string, session, redirect, url_for
import PyPDF2
import docx
import pickle
import os
from transformers import T5Tokenizer, T5ForConditionalGeneration
import time

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for session management

MODEL_PATH = "model.pkl"
TOKENIZER_PATH = "tokenizer.pkl"

TIMEOUT = 2 * 60  # 2 minutes in seconds


def save_model_and_tokenizer(model, tokenizer, model_path, tokenizer_path):
    with open(model_path, 'wb') as model_file, open(tokenizer_path, 'wb') as tokenizer_file:
        pickle.dump(model, model_file)
        pickle.dump(tokenizer, tokenizer_file)


def load_model_and_tokenizer(model_path, tokenizer_path):
    with open(model_path, 'rb') as model_file, open(tokenizer_path, 'rb') as tokenizer_file:
        model = pickle.load(model_file)
        tokenizer = pickle.load(tokenizer_file)
    return model, tokenizer


# Check if the model and tokenizer are already saved
if not os.path.exists(MODEL_PATH) or not os.path.exists(TOKENIZER_PATH):
    # Load the T5 tokenizer and model from Hugging Face
    tokenizer = T5Tokenizer.from_pretrained("t5-small")
    model = T5ForConditionalGeneration.from_pretrained("t5-small")
    # Save the model and tokenizer
    save_model_and_tokenizer(model, tokenizer, MODEL_PATH, TOKENIZER_PATH)
else:
    # Load the model and tokenizer from the saved files
    model, tokenizer = load_model_and_tokenizer(MODEL_PATH, TOKENIZER_PATH)


def read_pdf(file_path):
    text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfFileReader(file)
        for page_num in range(reader.numPages):
            page = reader.getPage(page_num)
            text += page.extract_text()
    return text


def read_docx(file_path):
    doc = docx.Document(file_path)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text


def read_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
    return text


def summarize_text(text):
    input_text = "summarize: " + text
    input_ids = tokenizer.encode(input_text, return_tensors="pt")
    output = model.generate(input_ids, max_length=150, num_return_sequences=1, no_repeat_ngram_size=2)
    summary = tokenizer.decode(output[0], skip_special_tokens=True)
    return summary


@app.before_request
def check_session_timeout():
    if 'session_ended' in session:
        return  # Don't redirect again if the session has already ended

    last_activity = session.get('last_activity')
    if last_activity and time.time() - last_activity > TIMEOUT:
        session.clear()
        session['session_ended'] = True
        return redirect(url_for('index'))

    session['last_activity'] = time.time()


@app.route('/', methods=['GET', 'POST'])
def index():
    session_ended = session.pop('session_ended', None)
    if request.method == 'POST':
        file = request.files['file']
        if file:
            file_path = f"./{file.filename}"
            file.save(file_path)
            if file.filename.endswith('.pdf'):
                text = read_pdf(file_path)
            elif file.filename.endswith('.docx'):
                text = read_docx(file_path)
            elif file.filename.endswith('.txt'):
                text = read_txt(file_path)
            else:
                return "Unsupported file type. Please upload a PDF, Word, or Text document."

            summary = summarize_text(text)
            session['context'] = text
            session['summary'] = summary
            session['qa_history'] = []
            return render_template_string(template, summary=summary, qa_history=session['qa_history'],
                                          session_ended=session_ended)
    return render_template_string(template, session_ended=session_ended)


@app.route('/answer', methods=['POST'])
def answer():
    question = request.form['question']
    context = session.get('context', '')
    qa_history = session.get('qa_history', [])

    input_text = f"question: {question} context: {context}"
    input_ids = tokenizer.encode(input_text, return_tensors="pt")
    output = model.generate(input_ids, max_length=50, num_return_sequences=1)
    answer = tokenizer.decode(output[0], skip_special_tokens=True)

    qa_history.append((question, answer))
    session['qa_history'] = qa_history
    return render_template_string(template, summary=session.get('summary', ''), qa_history=qa_history)


@app.route('/reset_qa', methods=['POST'])
def reset_qa():
    session['qa_history'] = []
    return redirect(url_for('index'))


template = '''
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>Document Summarizer and QA Chatbot</title>
  </head>
  <body>
    <div class="container">
      <h1>Document Summarizer and QA Chatbot</h1>
      {% if session_ended %}
        <div class="alert alert-warning" role="alert">
          Your session has ended due to inactivity.
        </div>
      {% endif %}
      <form method="POST" enctype="multipart/form-data">
        <div class="form-group">
          <label for="file">Upload a PDF, Word, or Text document</label>
          <input type="file" class="form-control" id="file" name="file">
        </div>
        <button type="submit" class="btn btn-primary">Submit</button>
      </form>
      {% if summary %}
        <h2>Summary</h2>
        <p>{{ summary }}</p>
        <h2>Ask a Question</h2>
        <form method="POST" action="/answer">
          <div class="form-group">
            <label for="question">Question</label>
            <input type="text" class="form-control" id="question" name="question">
          </div>
          <button type="submit" class="btn btn-primary">Ask</button>
        </form>
        {% if qa_history %}
          <h2>Questions and Answers</h2>
          <ul>
            {% for q, a in qa_history %}
              <li><strong>Q:</strong> {{ q }}<br><strong>A:</strong> {{ a }}</li>
            {% endfor %}
          </ul>
          <form method="POST" action="/reset_qa">
            <button type="submit" class="btn btn-danger">Reset QA</button>
          </form>
        {% endif %}
      {% endif %}
    </div>
  </body>
</html>
'''

if __name__ == '__main__':
    app.run()
