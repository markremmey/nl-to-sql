import openai
import logging
import json
import os
import pandas as pd
import requests
import sqlite3

from flask import (
    Flask, request, stream_with_context, Response, flash, session
)

from flask_session import Session
from dotenv import load_dotenv
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.secret_key = b'_5#y2Y"F4P8q\n\xfc]/'

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


load_dotenv()
logging.basicConfig(level=logging.INFO)

# logging.info('KEY: ', os.getenv("AZ_APIM_KEY"))
def streamOpenAI(prompt):
    if 'messages' not in session:
        session['messages'] = []

    session['messages'].append({"role": "user", "content": prompt})

    jsonRequest = {
        "messages": session['messages'],
        "temperature": 0.7,
        "top_p": 0.95,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "max_tokens": 50,
        "stop": None,
        "stream": True # This means that the OpenAI API will return a "streaming reps"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": os.getenv("AZ_APIM_KEY")
    }
    
    url = os.getenv("AZ_APIM_BASE") + 'deployments/gpt4/chat/completions?api-version=2023-07-01-preview'
    
    try:
        response = requests.post(url, headers=headers, json=jsonRequest, stream=True)
        response.raise_for_status()
    except Exception as e:
        logging.error(f"An error occurred while requesting {url}: {e}")

    logging.info('RESPONSE: ', response)
    session.modified = True
    return response

def createSQL(fileName):
    csvPath = 'uploads/' + fileName
    data = pd.read_csv(csvPath)
    dbPath = 'finances.db'
    conn = sqlite3.connect(dbPath)
    data.to_sql('transactions', conn, if_exists='replace', index=False)

    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    for table_name in tables:
        logging.info(f"\n\nStructure of table '{table_name[0]}':")
        table_info = conn.execute(f"PRAGMA table_info('{table_name[0]}');").fetchall()
        for column_info in table_info:
            logging.info(column_info)
    conn.close()
    return None

@app.route('/getAgentResponse')
def getAgentResponse():
    prompt = request.args.get('message')
    def read_stream(reader):
        response = ''
        # The following for loop iterates over the streamed response line bby line
        # In this case, each JSON sent back by AOAI is separated by \n\n
        for chunk in reader.iter_lines():
            decoded_line = chunk.decode('utf-8')
            if chunk:
                yield decoded_line + '\n\n'
            
            try:
                data = decoded_line[len('data: '):]
                logging.info('Data: ', data)
                logging.info(type(data))

                json_string = data.strip("('").rstrip("',)")
                logging.info(f'json_string: {json_string}')
                logging.info(type(json_string))

                json_data = json.loads(json_string)
                logging.info(f'json_data: {json_data}')
                logging.info(type(json_data))

                content = json_data['choices'][0]['delta']['content']
                logging.info(f'Content: {content}')
                response+=content
        
            except:
                pass
        logging.info('RESPONSE: ', response)
        session['messages'].append({"role": "assistant", "content": response})
        session.modified = True
        # messages.append({"role": "agent", "content": response})
    reader = streamOpenAI(prompt) #Reader is a server sent event 

    return Response(stream_with_context(read_stream(reader)), 
                    content_type='text/event-stream')

@app.route('/upload', methods=['POST','GET'])
def upload_file():
    logging.info('request.file')
    logging.info(request.files)
    # Check if a file is part of the request
    if 'file' not in request.files:
        flash('No file part')
        return 'No file part', 400 
    
    file = request.files['file']
    
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        flash('No selected file')
        return 'No file part', 400 

    file.save('uploads/' + file.filename)
    createSQL(file.filename)

    return 'File uploaded successfully'

if __name__ == '__main__':
    app.run(debug=True)