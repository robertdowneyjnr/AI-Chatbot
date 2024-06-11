
Document Summarizer and QA Chatbot
This project is a web-based application that allows users to upload PDF, Word, or Text documents, summarize their content, and ask questions based on the summarized text. The application uses the T5 transformer model for text summarization and question answering.

Features
Document Upload: Users can upload PDF, Word, or Text documents.
Text Summarization: The uploaded document's content is summarized using the T5 model.
Question Answering: Users can ask questions based on the summarized text.
Session Timeout: The application automatically ends the session after 2 minutes of inactivity.
Reset QA: Users can reset the QA history with a button click.
Session Notification: Users are notified when their session has ended due to inactivity.

Requirements
Python 3.6+
Flask
PyPDF2
python-docx
transformers
pickle
Setup

Clone the repository:
git clone https://github.com/yourusername/document-summarizer-qa.git
cd document-summarizer-qa

Install the required packages:
pip install flask PyPDF2 python-docx transformers

Run the application:
python app.py

Access the application:
Open your web browser and navigate to http://127.0.0.1:5000.

Usage
Upload a Document:

On the main page, upload a PDF, Word, or Text document.
Click the "Submit" button.
View Summary:

After submitting the document, the summary will be displayed on the page.
Ask Questions:

Enter a question in the "Question" input field.
Click the "Ask" button to get an answer based on the summarized text.
Reset QA History:

Click the "Reset QA" button to clear the question and answer history.
Session Timeout:

If the session is inactive for 2 minutes, it will end automatically, and you will be notified.

Code Overview
Main Components
Flask Application: The main web application is built using Flask.
Model and Tokenizer: The T5 model and tokenizer are used for text summarization and question answering.
Document Readers: Functions to read content from PDF, Word, and Text documents.
Session Management: Manages user sessions, including timeout handling.

Routes
/: The main route for document upload and summarization.
/answer: The route to handle question answering based on the summarized text.
/reset_qa: The route to reset the question and answer history.

Templates
The HTML template is included as a string in the template variable. It dynamically displays the summary, QA history, and session notifications.

Session Timeout
The check_session_timeout function in the @app.before_request decorator checks for session inactivity and clears the session if it has timed out.

Contributing
If you would like to contribute to this project, please fork the repository and submit a pull request. For major changes, please open an issue first to discuss what you would like to change.
