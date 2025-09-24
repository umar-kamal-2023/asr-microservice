import os
import random
import soundfile as sf
from datasets import load_dataset

# 1. Load the dataset
# You can choose any version available on the Hugging Face Hub.
# The `load_dataset` function will automatically handle the download and caching.
dataset_name = "mozilla-foundation/common_voice_13_0"
language_code = "en"
split = "train"

print(f"Loading '{dataset_name}' for language '{language_code}'...")
dataset = load_dataset(dataset_name, language_code, split=split, use_auth_token=True)

# 2. Extract a random sample of a certain size
num_samples = 10
sample_indices = random.sample(range(len(dataset)), num_samples)
sample_dataset = dataset.select(sample_indices)

# 3. Create a directory to save the audio files
output_dir = "./common_voice_audio_sample"
os.makedirs(output_dir, exist_ok=True)
print(f"Saving {num_samples} audio files to '{output_dir}'...")

# 4. Iterate through the sample and save each audio file
for i, item in enumerate(sample_dataset):
    audio_data = item['audio']['array']
    sampling_rate = item['audio']['sampling_rate']
    
    # Create a descriptive filename based on the sample index
    file_path = os.path.join(output_dir, f"sample_{i}.wav")
    
    # Use the soundfile library to write the audio data to a WAV file
    sf.write(file_path, audio_data, sampling_rate)
    
    # Print a confirmation message
    print(f"Saved: {file_path} (Text: '{item['sentence']}')")

print("\nDownload and saving complete.")