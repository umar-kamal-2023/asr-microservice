import uuid
import time
import tempfile
import json
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from app.separation import separate_audio
from app.transcribe import transcribe_audio

app = FastAPI()

@app.post("/v1/transcribe")
async def transcribe(file: UploadFile = File(...), params: str = Form("{}")):
    request_id = str(uuid.uuid4())
    timings = {}

    try:
        params_dict = json.loads(params)
    except Exception:
        params_dict = {}

    model_size = params_dict.get("model", "small")
    language = params_dict.get("language", None)
    separation_enabled = params_dict.get("separation", True)

    # Save uploaded file
    start = time.time()
    with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
        tmp.write(await file.read())
        input_path = tmp.name
    timings["load"] = int((time.time() - start) * 1000)

    # Separation
    if separation_enabled:
        start = time.time()
        sep_path, sep_meta = separate_audio(input_path)
        timings["separation"] = int((time.time() - start) * 1000)
    else:
        sep_path, sep_meta = input_path, {"enabled": False, "method": None}

    # Transcription
    start = time.time()
    result = transcribe_audio(sep_path, model_size, language)
    timings["transcription"] = int((time.time() - start) * 1000)

    timings["total"] = sum(timings.values())

    response = {
        "request_id": request_id,
        "duration_sec": result.get("duration_sec"),
        "sample_rate": result.get("sample_rate"),
        "pipeline": {
            "separation": sep_meta,
            "transcription": {"model": result.get("model")}
        },
        "segments": result.get("segments"),
        "text": result.get("text"),
        "language": result.get("language"),
        "timings_ms": timings
    }
    return JSONResponse(response)