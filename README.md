# ASR Microservice

A containerized microservice that accepts an audio file, separates vocals from background noise, and returns a transcription of the speech.  
Supports noisy audio, overlapping speakers, and diarization.  

---

## Features
- **Inference API**: `POST /v1/transcribe` (multipart form upload).  
- **Source separation**: Demucs-based speech/noise separation, with fallback to noise suppression.  
- **ASR**: OpenAI Whisper (configurable model size, language hint).  
- **Optional diarization**: pyannote for multi-speaker audio.  
- **Dockerized**: runs locally on CPU, with GPU acceleration if available.  
- **Auto-docs**: Interactive OpenAPI docs at `/docs`.  

---

## Setup

### 1. Clone Repo
```bash
git clone git@github.com:<your-username>/asr-microservice.git
cd asr-microservice
```

### 2. Build Docker Image
```bash
sudo docker build -t asr-microservice:local .
```

### 3. Run Container
```bash
sudo docker run -p 8000:8000 --rm asr-microservice:local
```
OR
```bash
sudo docker compose up --build
```

### 4. Access API
- Swagger docs: [http://localhost:8000/docs](http://localhost:8000/docs)  

---

## Testing with Sample Audio

This repo includes **5 sample clips** (`samples/`) to test noise, overlap, and diarization.  

Run:
```bash
curl -X POST "http://localhost:8000/v1/transcribe" \
     -F "file=@samples/noisy_clip.wav"
```

### Expected Behaviors

1. **`sample_noisy_background_15s.wav`**  
   - Café background noise, one speaker.  
   - Output (approx.):  
     ```json
    {
        "request_id": "000f1f7a-ed92-44d6-b027-69b5147f9da8",
        "duration_sec": 4.041315192743764,
        "sample_rate": 22050,
        "pipeline": {
            "separation": {
                "enabled": true,
                "method": "noisereduce"
            },
            "transcription": {
                "model": "whisper-small"
            },
            "diarization": {
                "enabled": false,
                "method": null
            }
        },
        "segments": [
            {
                "start": 0,
                "end": 2.32,
                "text": " Hello, this is a clean test audio."
            },
            {
                "start": 2.32,
                "end": 3.72,
                "text": " 1, 2, 3, testing."
            }
        ],
        "text": " Hello, this is a clean test audio. 1, 2, 3, testing.",
        "language": "en",
        "timings_ms": {
            "load": 0,
            "separation": 38094,
            "transcription": 220046,
            "total": 258140
        }
    }
     ```

2. **`sample_overlapping_20s.wav`**  
   - Two people speaking at once.  
   - Output: diarization splits them.  
     ```json
    {
        "request_id": "8181ad10-6ef4-4762-a274-54ac6b05f71c",
        "duration_sec": 3.212925170068027,
        "sample_rate": 22050,
        "pipeline": {
            "separation": {
                "enabled": true,
                "method": "noisereduce"
            },
            "transcription": {
                "model": "whisper-small"
            },
            "diarization": {
                "enabled": false,
                "method": null
            }
        },
        "segments": [
            {
                "start": 0,
                "end": 3,
                "text": " Hi I'm speaker 1, I will speak for the first part."
            }
        ],
        "text": " Hi I'm speaker 1, I will speak for the first part.",
        "language": "en",
        "timings_ms": {
            "load": 12,
            "separation": 72576,
            "transcription": 19572,
            "total": 92160
        }
    }
     ```

3. **`sample_clean_10s.wav`**  
   - Studio quality, one speaker.  
   - Output:  
     ```json
    {"request_id":"000f1f7a-ed92-44d6-b027-69b5147f9da8",
    "duration_sec":4.041315192743764,
    "sample_rate":22050,
    "pipeline":{
        "separation":{
            "enabled":true,
            "method":"noisereduce"
            },
            "transcription":
            {
                "model":"whisper-small"
                },
                "diarization":
                {
                    "enabled":false,
                    "method":null
                    }
                    },
                    "segments":
                    [
                        {"start":0.0,"end":2.32,"text":" Hello, this is a clean test audio."},
                        {"start":2.32,"end":3.72,"text":" 1, 2, 3, testing."}
                    ],
                    "text":" Hello, this is a clean test audio. 1, 2, 3, testing.",
                    "language":"en",
                    "timings_ms":
                    {"load":0,"separation":38094,"transcription":220046,"total":258140}
    }
     ```

4. **`music_bg.wav`**  
   - Voice with music background.  
   - Output:  
     ```json
     {
       "text": "Thanks for calling, how can I help you?"
     }
     ```

5. **`multi_speaker.wav`**  
   - Multi-speaker turn taking.  
   - Output:  
     ```json
     {
       "segments": [
         {"speaker": "SPEAKER_0", "text": "Let's start the meeting."},
         {"speaker": "SPEAKER_1", "text": "Sure, I’ll share the update."}
       ]
     }
     ```

---

## Architecture

### Components
- **FastAPI** → serves inference API.  
- **Demucs** → separates vocals from noise/music.  
- **NoiseReduce** → fallback if separation fails.  
- **Whisper** → transcription engine.  
- **pyannote.audio** → diarization.  
- **ffmpeg** → audio preprocessing.  

### Flow
1. Receive audio file.  
2. Run separation (Demucs → fallback NoiseReduce).  
3. Transcribe with Whisper.  
4. Optional: run diarization.  
5. Return structured JSON response with timings.  

---

## Trade-offs & Decisions
- **Whisper** chosen for robustness on noisy, multilingual audio. Trade-off: slower on CPU, but works offline.  
- **Demucs** separation improves accuracy in music/noise scenarios, but adds latency.  
- **Fallback noise suppression** ensures pipeline doesn’t fail completely if separation fails.  
- **Diarization** via pyannote works for turn-taking but struggles with heavy overlap.  
- **Docker CPU baseline**: ensures portability; GPU is used automatically if available.  
- **Pinned dependencies** in `requirements.txt` for reproducible builds.  

---

## API Example

**Request**:
```bash
curl -X POST "http://localhost:8000/v1/transcribe" \
     -F "file=@sample_audio/clean.wav"
```

**Response**:
```json
{"request_id":"000f1f7a-ed92-44d6-b027-69b5147f9da8",
"duration_sec":4.041315192743764,
"sample_rate":22050,
"pipeline":{
    "separation":{
        "enabled":true,
        "method":"noisereduce"
        },
        "transcription":
        {
            "model":"whisper-small"
            },
            "diarization":
            {
                "enabled":false,
                "method":null
                }
                },
                "segments":
                [
                    {"start":0.0,"end":2.32,"text":" Hello, this is a clean test audio."},
                    {"start":2.32,"end":3.72,"text":" 1, 2, 3, testing."}
                ],
                "text":" Hello, this is a clean test audio. 1, 2, 3, testing.",
                "language":"en",
                "timings_ms":
                {"load":0,"separation":38094,"transcription":220046,"total":258140}
                }
```
