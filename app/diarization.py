import os
from pyannote.audio import Pipeline

_pipeline_cache = None

def load_diarization_pipeline():
    global _pipeline_cache
    if _pipeline_cache is None:
        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            raise RuntimeError("HF_TOKEN not set. Please add it to your environment.")
        _pipeline_cache = Pipeline.from_pretrained(
            "pyannote/speaker-diarization",
            use_auth_token=hf_token
        )
    return _pipeline_cache

def diarize_audio(audio_path: str):
    pipeline = load_diarization_pipeline()
    diarization = pipeline(audio_path)

    segments = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segments.append({
            "start": turn.start,
            "end": turn.end,
            "speaker": speaker
        })
    return segments

def merge_transcript_with_diarization(transcript_segments, diarization_segments):
    """
    Align diarization output with Whisper transcript segments.
    """
    merged = []
    for ts in transcript_segments:
        start, end, text = ts.get("start"), ts.get("end"), ts.get("text")
        # Find speaker overlapping with this transcript segment
        speaker = None
        for d in diarization_segments:
            if d["start"] <= start < d["end"] or d["start"] < end <= d["end"]:
                speaker = d["speaker"]
                break
        merged.append({
            "start": start,
            "end": end,
            "speaker": speaker if speaker else "UNKNOWN",
            "text": text
        })
    return merged
