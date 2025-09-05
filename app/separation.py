import subprocess
import os
import noisereduce as nr
import soundfile as sf

def separate_audio(input_path: str):
    try:
        # Use Demucs for separation
        cmd = ["demucs", "--two-stems", "vocals", input_path]
        subprocess.run(cmd, check=True)

        sep_path = find_vocals_file(input_path)
        return sep_path, {"enabled": True, "method": "demucs"}
    except Exception:
        # Fallback: noise reduction
        data, sr = sf.read(input_path)
        reduced = nr.reduce_noise(y=data, sr=sr)
        fallback_path = input_path.replace(".wav", "_denoised.wav")
        sf.write(fallback_path, reduced, sr)
        return fallback_path, {"enabled": True, "method": "noisereduce"}

def find_vocals_file(input_path):
    base = os.path.basename(input_path).split(".")[0]
    for root, _, files in os.walk("separated"):
        for f in files:
            if base in f and "vocals" in f:
                return os.path.join(root, f)
    raise FileNotFoundError("Demucs output not found")