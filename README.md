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
- Health check:  
  ```bash
  curl http://localhost:8000/health
  ```

---

## Testing with Sample Audio

This repo includes **5 sample clips** (`sample_audio/`) to test noise, overlap, and diarization.  

Run:
```bash
curl -X POST "http://localhost:8000/v1/transcribe" \
     -F "file=@sample_audio/noisy_clip.wav"
```

### Expected Behaviors

1. **`noisy_clip.wav`**  
   - Café background noise, one speaker.  
   - Output (approx.):  
     ```json
     {
       "text": "Can I get a coffee please?"
     }
     ```

2. **`overlap.wav`**  
   - Two people speaking at once.  
   - Output: diarization splits them.  
     ```json
     {
       "segments": [
         {"speaker": "SPEAKER_0", "text": "Hey, are you free later?"},
         {"speaker": "SPEAKER_1", "text": "Yes, after 6 pm works."}
       ]
     }
     ```

3. **`clean.wav`**  
   - Studio quality, one speaker.  
   - Output:  
     ```json
     {
       "text": "This is a clean audio test."
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
{
  "request_id": "3aef9c1f-5f3a-4a64-b3a2-6bbac3fd9187",
  "duration_sec": 4.0,
  "sample_rate": 16000,
  "pipeline": {
    "separation": {"enabled": true, "method": "demucs"},
    "transcription": {"model": "whisper-small"},
    "diarization": {"enabled": true, "method": "pyannote"}
  },
  "segments": [
    {"start": 0.0, "end": 4.0, "speaker": "SPEAKER_0", "text": "This is a clean audio test."}
  ],
  "text": "This is a clean audio test.",
  "language": "en",
  "timings_ms": {"load": 420, "separation": 1800, "transcription": 4100, "total": 6400}
}
```
