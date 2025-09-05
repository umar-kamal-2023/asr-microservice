import uuid
import time
import tempfile
import json
import os
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from app.separation import separate_audio
from app.transcribe import transcribe_audio
from app.diarization import diarize_audio, merge_transcript_with_diarization

app = FastAPI()


@app.post("/v1/transcribe")
async def transcribe(file: UploadFile = File(...), params: str = Form("{}")):
    request_id = str(uuid.uuid4())
    timings = {"load": 0, "separation": 0, "transcription": 0}

    try:
        params_dict = json.loads(params)
    except Exception:
        params_dict = {}

    model_size = params_dict.get("model", "small")
    language = params_dict.get("language", None)
    separation_enabled = params_dict.get("separation", True)
    diarization_enabled = params_dict.get("diarization", False)

    # Save uploaded file
    start = time.time()
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        tmp.write(await file.read())
        input_path = tmp.name
    timings["load"] = int((time.time() - start) * 1000)

    # Separation
    sep_meta = {"enabled": False, "method": None}
    sep_path = input_path
    if separation_enabled:
        start = time.time()
        try:
            sep_path, sep_meta = separate_audio(input_path)
        except Exception:
            sep_path = input_path
            sep_meta = {"enabled": False, "method": None, "error": "separation_failed"}
        timings["separation"] = int((time.time() - start) * 1000)
    else:
        timings["separation"] = 0

    # Transcription
    start = time.time()
    try:
        result = transcribe_audio(sep_path, model_size=model_size, language=language)
    except Exception as e:
        return JSONResponse({
            "request_id": request_id,
            "error": "transcription_failed",
            "message": str(e)
        }, status_code=500)
    timings["transcription"] = int((time.time() - start) * 1000)

    # Diarization
    diarization_meta = {"enabled": diarization_enabled, "method": None}
    diarization_timems = None
    merged_segments = None
    if diarization_enabled:
        start = time.time()
        try:
            diarization_segments = diarize_audio(sep_path)
            merged_segments = merge_transcript_with_diarization(
                result.get("segments", []), diarization_segments
            )
            diarization_meta["method"] = "pyannote"
        except Exception:
            merged_segments = result.get("segments", [])
            diarization_meta["method"] = None
        diarization_timems = int((time.time() - start) * 1000)

    # Pipeline metadata
    pipeline = {
        "separation": {"enabled": bool(sep_meta.get("enabled")), "method": sep_meta.get("method")},
        "transcription": {"model": f"whisper-{model_size}"},
        "diarization": diarization_meta
    }

    # Final segments
    final_segments = merged_segments if (diarization_enabled and merged_segments is not None) else result.get("segments", [])

    cleaned_segments = []
    for seg in final_segments:
        s = {"start": float(seg.get("start")), "end": float(seg.get("end")), "text": seg.get("text", "")}
        if seg.get("speaker"):
            s["speaker"] = seg.get("speaker")
        cleaned_segments.append(s)

    # timings_ms
    timings_ms = {
        "load": timings.get("load", 0),
        "separation": timings.get("separation", 0),
        "transcription": timings.get("transcription", 0)
    }
    if diarization_enabled:
        timings_ms["diarization"] = diarization_timems if diarization_timems is not None else 0
    timings_ms["total"] = sum(int(v) for v in timings_ms.values() if isinstance(v, int))

    # Final response
    response = {
        "request_id": request_id,
        "duration_sec": result.get("duration_sec"),
        "sample_rate": result.get("sample_rate"),
        "pipeline": pipeline,
        "segments": cleaned_segments,
        "text": result.get("text"),
        "language": result.get("language"),
        "timings_ms": timings_ms
    }

    return JSONResponse(response)
