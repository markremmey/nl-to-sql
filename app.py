import openai
import logging
import json
import os
import requests

from flask import (
    Flask, request, jsonify,  stream_with_context, Response, redirect, flash
)

from flask_cors import CORS
app = Flask(__name__)
CORS(app)
from dotenv import load_dotenv
load_dotenv()


logging.basicConfig(level=logging.INFO)

openai.api_type = "azure"
openai.api_base = os.getenv("AZ_APIM_BASE")
openai.api_version = "2023-07-01-preview"
openai.api_key =  os.getenv("AZ_APIM_KEY")

def streamOpenAI(prompt):
    messages = []    
    messages.append({"role": "user", "content": prompt})


    jsonRequest = {
        "messages": [
            {
                "role": "system",
                "content": prompt
            }
        ],
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
        "Ocp-Apim-Subscription-Key": os.getenv("AZ_APIM_BASE")
    }
    
    url = os.getenv("AZ_APIM_BASE") + '/deployments/gpt4/chat/completions?api-version=2023-07-01-preview'
    
    try:
        response = requests.post(url, headers=headers, json=jsonRequest, stream=True)
        response.raise_for_status()
    except Exception as e:
        logging.error(f"An error occurred while requesting {url}: {e}")

    logging.info('RESPONSE: ', response)
    return response

@app.route('/getAgentResponse')
def getAgentResponse():
    text = request.args.get('message')
    def read_stream(reader):
        
        # The following for loop iterates over the streamed response line bby line
        # In this case, each JSON sent back by AOAI is separated by \n\n
        for chunk in reader.iter_lines():
            
            if chunk:
                decoded_line = chunk.decode('utf-8')
                logging.info('DECODED_LINE: ')
                logging.info(decoded_line)
                yield decoded_line + '\n\n'
    
    prompt = f"{text}"

    reader = streamOpenAI(prompt) #Reader is a server sent event 

    return Response(stream_with_context(read_stream(reader)), 
                    content_type='text/event-stream')

@app.route('/upload', methods=['POST','GET'])
def upload_file():
    logging.info('request.file')
    logging.info(request.file)
    # Check if a file is part of the request
    # if 'file' not in request.files:
    #     flash('No file part')
    #     return 'No file part', 400 
    
    file = request.files['file']
    
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    # if file.filename == '':
    #     flash('No selected file')
    #     return 'No file part', 400 

    file.save('uploads/' + file.filename)
    return 'File uploaded successfully'


if __name__ == '__main__':
    app.run(debug=True)