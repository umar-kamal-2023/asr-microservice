import whisper
import torchaudio

_model_cache = {}

def load_model(name="small"):
    if name not in _model_cache:
        _model_cache[name] = whisper.load_model(name)
    return _model_cache[name]

def transcribe_audio(audio_path: str, model_size="small", language=None):
    model = load_model(model_size)
    audio, sr = torchaudio.load(audio_path)

    result = model.transcribe(audio_path, language=language)

    return {
        "duration_sec": float(audio.shape[1]) / sr,
        "sample_rate": sr,
        "segments": result.get("segments"),
        "text": result.get("text"),
        "language": result.get("language"),
        "model": model_size
    }