# Speech Separation + Transcription Service

This project provides a microservice that isolates vocals from audio files and transcribes them using [OpenAI Whisper](https://github.com/openai/whisper). It’s packaged with Docker for easy deployment.

## Features
- HTTP API (`/v1/transcribe`) for uploading audio and receiving transcription.
- Source separation (vocals vs background) using Demucs.
- Noise reduction fallback when separation fails.
- Whisper-based ASR with selectable model sizes (`tiny`, `base`, `small`, `medium`, `large`).
- Dockerized for local or server deployment.
- Optional CLI utility for quick usage.

## Requirements
- Docker & docker-compose
- (Optional) Python 3.10+ if running locally without Docker

## Quickstart

### Run with Docker
```bash
docker build -t speech-sep-transcribe:local .
docker compose up --build