# Set the device with environment, default is cuda:0
# export SENSEVOICE_DEVICE=cuda:1

import os, re, wave
from fastapi import FastAPI, File, Form
#from fastapi.responses import HTMLResponse
from typing_extensions import Annotated
from typing import List
from enum import Enum
import torchaudio
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

def audio_callback(recognizer, audio):

    # Wait for user to press 'q' to quit
    # input()  # Wait for user to press Enter
    print("Listening for questions...")

    audios = []
    audio_fs = 0

    # with microphone as source:
    #     recognizer.adjust_for_ambient_noise(source)
    #     # Speack should be less than 10 seconds
    #     audio = recognizer.listen(source, phrase_time_limit=10)

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
    print("\nTime consumed for calling inference:", time_consumed, "\n")

    if len(res) == 0:
        return {"result": []}

    for it in res[0]:
        it["raw_text"] = it["text"]
        raw_text = it["text"]

        it["clean_text"] = re.sub(regex, "", it["text"], 0, re.MULTILINE)
        clean_text = it["clean_text"]

        it["text"] = rich_transcription_postprocess(it["text"])
        rich_text = it["text"]

    print("Raw text:\n", raw_text, "\n")
    print("Clean text:\n", clean_text, "\n")
    print("Rich text:\n", rich_text, "\n")


def listen_to_questions():

    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    while True:
        # Wait for user to press 'q' to quit
#        input()  # Wait for user to press Enter
        print("Listening for questions...")

        if input() == 'q':
            break

        audios = []
        audio_fs = 0

        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            # Speack should be less than 10 seconds
            audio = recognizer.listen(source, phrase_time_limit=10)

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
        print("\nTime consumed for calling inference:", time_consumed, "\n")

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

        print("Raw text:\n", raw_text, "\n")
        print("Clean text:\n", clean_text, "\n")
        print("Rich text:\n", rich_text, "\n")

#    recognizer.non_speaking_duration

if __name__ == "__main__":

#    listen_to_questions()

    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)

    stop_listening = recognizer.listen_in_background(microphone, audio_callback, phrase_time_limit=8)

    while True:
        if input() == 'q':
            break

    stop_listening(wait_for_stop=False)    