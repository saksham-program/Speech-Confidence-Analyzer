import sounddevice as sd
import numpy as np
import speech_recognition as sr
import librosa
from scipy.io.wavfile import write
import os

# -------------------------------
# 1. Record Live Audio
# -------------------------------
def record_audio(duration=30, fs=44100):
    print("\n🎙️ Speak now... (recording)")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    print("Recording finished\n")
    return audio.flatten(), fs

# -------------------------------
# 2. Speech to Text
# -------------------------------
def speech_to_text(audio, fs):
    # Convert float audio to PCM int16
    audio_int16 = np.int16(audio / np.max(np.abs(audio)) * 32767)

    write("temp.wav", fs, audio_int16)

    r = sr.Recognizer()
    with sr.AudioFile("temp.wav") as source:
        audio_data = r.record(source)

    try:
        text = r.recognize_google(audio_data).lower()
    except:
        text = ""

    os.remove("temp.wav")
    return text

# -------------------------------
# 3. Speech Rate
# -------------------------------
def speech_rate(text, duration):
    words = len(text.split())
    return (words / duration) * 60 if duration > 0 else 0

# -------------------------------
# 4. Filler Density
# -------------------------------
def filler_density(text):
    fillers = ["um", "uh", "like", "you know", "actually"]
    total_words = len(text.split())
    count = sum(text.count(f) for f in fillers)
    return count / total_words if total_words > 0 else 0

# -------------------------------
# 5. Pause Ratio
# -------------------------------
def pause_ratio(audio, fs):
    intervals = librosa.effects.split(audio, top_db=25)
    speech_time = sum((end - start) for start, end in intervals) / fs
    total_time = len(audio) / fs
    return (total_time - speech_time) / total_time

# -------------------------------
# 6. Pitch Variation
# -------------------------------
def pitch_variance(audio, fs):
    pitches, _ = librosa.piptrack(y=audio, sr=fs)
    pitch_vals = pitches[pitches > 0]
    return np.var(pitch_vals) if len(pitch_vals) else 0

# -------------------------------
# 7. Final Confidence Score
# -------------------------------
def confidence_score(wpm, pause, filler, pitch):
    score = 100
    if wpm < 90 or wpm > 160: score -= 15
    if pause > 0.25: score -= 20
    if filler > 0.05: score -= 15
    if pitch < 50: score -= 10
    return max(score, 0)

# -------------------------------
# MAIN
# -------------------------------
def main():
    DURATION = 30  # seconds

    audio, fs = record_audio(DURATION)
    text = speech_to_text(audio, fs)

    wpm = speech_rate(text, DURATION)
    filler = filler_density(text)
    pause = pause_ratio(audio, fs)
    pitch = pitch_variance(audio, fs)
    score = confidence_score(wpm, pause, filler, pitch)

    print("SPEECH CONFIDENCE REPORT")
    print("-" * 30)
    print(f"Speech Rate (WPM): {round(wpm, 2)}")
    print(f"Pause Ratio: {round(pause, 2)}")
    print(f"Filler Density: {round(filler, 3)}")
    print(f"Pitch Variance: {round(pitch, 2)}")
    print(f"\n Confidence Score: {score}/100\n")

    if score >= 80:
        print("Excellent confidence!")
    elif score >= 60:
        print("Decent, but improve pauses & fillers.")
    else:
        print("Needs improvement. Practice structured answers.")

if __name__ == "__main__":
    main()
