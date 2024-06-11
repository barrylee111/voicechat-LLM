import json
import numpy as np
import os
import sounddevice as sd
import whisper

from dotenv import load_dotenv
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Request, Response
from openai import AsyncOpenAI
from scipy.io.wavfile import write

router = APIRouter()
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

TEMP_STORAGE_DIR = "/tmp"

recording_data = []
sampling_rate = 44100
channels = 1

model = whisper.load_model('base')

### UTILS ###

format_dict = {
    'pirate': {"role": "system", "content": "You are a pirate chatbot who always responds in pirate speak!"},
    'scotsman': {"role": "system", "content": "You are a Scottish Highlander who always responds in a Scottish Accent!"}
}

messages=[
        {"role": "system", "content": "You are a helpful assistant designed to output JSON and puts the answers in the response attribute of the JSON regardless of status."},
    ]

async def generate_response_chat(prompt, narrator=None):
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

        response = await client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            response_format={"type": "json_object"},
            messages=messages
        )

        response_content = json.loads(response.choices[0].message.content)
        if "response" not in response_content:
            raise HTTPException(status_code=500, detail="Invalid response format")

        response_data = response_content["response"]
        return Response(content=json.dumps({"response": response_data}), status_code=200)

    except HTTPException as http_exc:
        return http_exc
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#############

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
        
        messages += [{"role": "user", "content": f'{prompt}'}]
        narrator = request_body.get("narrator")

        if narrator: 
            if narrator in format_dict:
                messages = [format_dict[narrator]] + messages
                print(messages)
            else:
                print('Sorry, that narrator is not available at this time...')

        response = await client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            response_format={"type": "json_object"},
            messages=messages
        )

        response_content = json.loads(response.choices[0].message.content)
        response_data = response_content["response"]

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

@router.websocket("/ws/generate")
async def websocket_endpoint(websocket: WebSocket):
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

            # Generate Response
            response = await generate_response_chat(prompt, narrator)

            # Delete temporary file (if needed)
            os.remove(temp_file_path)

            # Return Response to client
            await websocket.send_text(response.body.decode())

        elif action == "cancel":
            await websocket.send_text("Recording cancelled and data discarded.")

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        await websocket.send_text(f"Error: {str(e)}")

    await websocket.close()
