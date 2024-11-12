# Set the device with environment, default is cuda:0
# export SENSEVOICE_DEVICE=cuda:1

import os, re, wave
from typing_extensions import Annotated
from typing import List
from enum import Enum
import torchaudio

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from model import SenseVoiceSmall
from funasr.utils.postprocess_utils import rich_transcription_postprocess
from io import BytesIO

import speech_recognition as sr
import time

class Language(str, Enum):
    auto = "auto"
    zh = "zh"
    en = "en"
    yue = "yue"
    ja = "ja"
    ko = "ko"
    nospeech = "nospeech"

model_dir = "iic/SenseVoiceSmall"
m, kwargs = SenseVoiceSmall.from_pretrained(model=model_dir, device=os.getenv("SENSEVOICE_DEVICE", "cuda:0"))
m.eval()

regex = r"<\|.*\|>"

# ASR: Automatic Speech Recognition
# Here we use the Whisper model from OpenAI to recognize the speech
def asr_whisper(recognizer, audio):
    
    start_time = time.time()  # Record start time
    
    speech_text = recognizer.recognize_whisper(audio, model="base", language="chinese")
    print(f"User said: {speech_text}")

    end_time = time.time()  # Record end time
    time_consumed = end_time - start_time  # Calculate time consumed

    print(f"Time consumed for whisper ASR: {time_consumed:.2f} seconds")    
    return speech_text

def asr_sensevoice(audio):

    audios = []
    audio_fs = 0

        # Save the audio data to a BytesIO object
    file_io = BytesIO()
    with wave.open(file_io, "wb") as wave_file:
        wave_file.setnchannels(1)  # Mono
        wave_file.setsampwidth(audio.sample_width)
        wave_file.setframerate(audio.sample_rate)
        wave_file.writeframes(audio.get_wav_data())

    # Ensure the BytesIO object is at the beginning
    file_io.seek(0)

    data_or_path_or_list, audio_fs = torchaudio.load(file_io)
    data_or_path_or_list = data_or_path_or_list.mean(0)
    audios.append(data_or_path_or_list)
    file_io.close()

    lang = "auto"
    key = ["wav_file_tmp_name"]

    start_time = time.time()
    res = m.inference(
        data_in=audios,
        language=lang, # "zh", "en", "yue", "ja", "ko", "nospeech"
        use_itn=False,
        ban_emo_unk=False,
        key=key,
        fs=audio_fs,
        **kwargs,
    )

    end_time = time.time()
    time_consumed = end_time - start_time
    print("\nTime consumed for __Ali_SenseVoice__ inference:", time_consumed, "\n")

    if len(res) == 0:
        return {"result": []}

    for it in res[0]:
        it["raw_text"] = it["text"]
        raw_text = it["text"]

        it["clean_text"] = re.sub(regex, "", it["text"], 0, re.MULTILINE)
        clean_text = it["clean_text"]

        it["text"] = rich_transcription_postprocess(it["text"])
        rich_text = it["text"]
#    return {"result": res[0]}

    #print("Raw text:\n", raw_text, "\n")
    #print("Clean text:\n", clean_text, "\n")
    #print("Rich text:\n", rich_text, "\n")

    return clean_text

   