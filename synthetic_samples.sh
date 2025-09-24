mkdir -p samples

# 1) clean 10s
espeak "Hello, this is a clean test audio. One two three, testing." -w samples/sample_clean_10s.wav

# 2) noisy background 15s
espeak "Now I'm speaking with background noise. The quick brown fox jumped over the lazy dog." -w tmp_clean.wav
# get publicly available noise file or record one; here we use the same clean file repeated as placeholder
ffmpeg -stream_loop -1 -i tmp_clean.wav -t 15 -f wav tmp_clean_15.wav
# mix with low-level synthetic noise (white noise)
ffmpeg -f lavfi -i "sine=frequency=200:duration=15" -t 15 noise_tone.wav
ffmpeg -i tmp_clean_15.wav -i noise_tone.wav -filter_complex "[0:a]volume=1[a0];[1:a]volume=0.2[a1];[a0][a1]amix=inputs=2:duration=shortest" samples/sample_noisy_background_15s.wav

# 3) overlapping speakers 20s - create two voices and mix partially overlapped
espeak "Hi I'm speaker one. I will speak for the first part." -w s1.wav
espeak "And I'm speaker two. I talk over in the middle." -w s2.wav
# align and mix to create overlap
ffmpeg -i s1.wav -i s2.wav -filter_complex "[0:a]adelay=0|0[a0];[1:a]adelay=5000|5000[a1];[a0][a1]amix=inputs=2:duration=shortest" samples/sample_overlapping_20s.wav

# 4) phone call style (band-limited)
espeak "This is a phone call style sample." -w tmp_phone.wav
ffmpeg -i tmp_phone.wav -af "highpass=f=300, lowpass=f=3400" samples/sample_phone_call_25s.wav