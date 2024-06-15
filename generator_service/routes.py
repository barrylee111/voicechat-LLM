import json
import numpy as np
import os
import sounddevice as sd
import whisper

from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Request, Response, UploadFile, File
from fastapi.responses import FileResponse
from gtts import gTTS
from io import BytesIO
from langchain_elasticsearch import ElasticsearchStore
from langchain_openai import OpenAIEmbeddings
from openai import AsyncOpenAI
from scipy.io.wavfile import write


router = APIRouter()
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "http://localhost:9200")
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

TEMP_STORAGE_DIR = "/tmp"

recording_data = []
sampling_rate = 44100 # default, sr is read in from user's device
channels = 1 # mono to reduce data packet size

model = whisper.load_model('base')

### UTILS ###

format_dict = {
    'pirate': {"role": "system", "content": "You are a pirate chatbot who always responds in pirate speak!"},
    'scotsman': {"role": "system", "content": "You are a Scottish Highlander who always responds in a Scottish Accent regardless of the question or topic!"}
}

messages = [
    {"role": "system", "content": "You are a helpful assistant designed to output JSON and puts the answers in the response attribute of the JSON regardless of status."},
]

async def generate_response(prompt, narrator=None, documents=None):
    global messages

    try:
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")
        elif len(prompt) > 1000:
            raise HTTPException(status_code=400, detail="Prompt is too long")

        messages += [{"role": "user", "content": f'{prompt}'}]

        if narrator in format_dict:
            messages.insert(0, format_dict[narrator])
        else:
            print('Sorry, that narrator is not available at this time...')

        if documents:
            for doc in documents:
                messages.append({"role": "system", "content": f'Domain Knowledge: {doc}'})

        response = await client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            response_format={"type": "json_object"},
            messages=messages
        )

        response_content = json.loads(response.choices[0].message.content)
        if "response" not in response_content:
            raise HTTPException(status_code=500, detail="Invalid response format")

        return response_content["response"]

    except HTTPException as http_exc:
        return http_exc
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

### ELASTICSEARCH SETUP ###

es = Elasticsearch([ELASTICSEARCH_HOST])
embedding = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
vector_store = ElasticsearchStore(es_url=ELASTICSEARCH_HOST, index_name="documents", embedding=embedding)

async def store_document(text):
    vector_store.add_texts(texts=[text])

async def search_documents(query):
    return vector_store.similarity_search(query)

#############

@router.post("/load-document")
async def load_document(file: UploadFile = File(...)):
    try:
        content = await file.read()
        text = content.decode('utf-8')

        await store_document(text)
        return {"message": "Document uploaded and stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate")
async def generate_response_text(request: Request):
    global messages

    try:
        request_body = await request.json()
        prompt = request_body.get("prompt")

        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")
        elif len(prompt) > 1000:
            raise HTTPException(status_code=400, detail="Prompt is too long")

        narrator = request_body.get("narrator")

        search_results = await search_documents(prompt)
        relevant_docs = [result.page_content for result in search_results]

        response_data = await generate_response(prompt, narrator, documents=relevant_docs)
        return Response(content=json.dumps({"response": response_data}), status_code=200)

    except HTTPException as http_exc:
        return http_exc
    except ValueError as value_error:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list-devices")
async def list_audio_devices():
    devices = sd.query_devices()
    return [device['name'] for device in devices]

@router.post("/search")
async def search_responses(request: Request):
    try:
        request_body = await request.json()
        query = request_body.get("query")

        if not query:
            raise HTTPException(status_code=400, detail="Query is required")

        search_results = await search_documents(query)
        return Response(content=json.dumps({"results": search_results}), status_code=200)
    except HTTPException as http_exc:
        return http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/ws/generate")
async def generate_response_chat(websocket: WebSocket):
    global recording_data, sampling_rate, channels

    await websocket.accept()
    recording_data = []

    try:
        # Get the default input device and its sample rate
        default_device_info = sd.query_devices(None, 'input')
        if not default_device_info:
            raise HTTPException(status_code=500, detail="No default input device found.")
        sampling_rate = int(default_device_info['default_samplerate'])

        with sd.InputStream(callback=lambda indata, frames, time, status: recording_data.append(indata.copy()), channels=channels, samplerate=sampling_rate):
            await websocket.send_text("Recording started.")
            while True:
                data = await websocket.receive_json()
                narrator = None
                action = None

                # Parse JSON message from client
                try:
                    action = data['action']
                    narrator = data['narrator']
                except json.JSONDecodeError:
                    await websocket.send_text("Invalid JSON format")
                    continue

                if action == "send":
                    break
                elif action == "cancel":
                    recording_data = []
                    await websocket.send_text("Recording cancelled.")
                    break

        if action == "send" and recording_data:
            audio_data = np.concatenate(recording_data, axis=0)
            audio_data = (audio_data * np.iinfo(np.int16).max).astype(np.int16)
            temp_file_path = os.path.join(TEMP_STORAGE_DIR, "recorded_audio.wav")
            write(temp_file_path, sampling_rate, audio_data)
            await websocket.send_text(f"Audio recorded and saved as WAV. File path: {temp_file_path}")

            # Transcribe from the temporary WAV file
            prompt = model.transcribe(temp_file_path)['text']
            os.remove(temp_file_path)

            # Generate Response
            search_results = await search_documents(prompt)
            relevant_docs = [result.page_content for result in search_results]

            response_data = await generate_response(prompt, narrator, documents=relevant_docs)
            tts = gTTS(response_data, lang='en')
        
            # To test audio output locally
            # tts.save('audio_output.wav')

            audio_bytes = BytesIO()
            tts.write_to_fp(audio_bytes)
            audio_bytes.seek(0)
            
            await websocket.send_bytes(audio_bytes.read())

        elif action == "cancel":
            await websocket.send_text("Recording cancelled and data discarded.")

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        await websocket.send_text(f"Error: {str(e)}")

    await websocket.close()
