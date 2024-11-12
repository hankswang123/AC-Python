# -*- coding: utf-8 -*-
import gc
import json
import os
import base64
import wave
import pyaudio
from pyaudio import PyAudio, paInt16

import time
import threading

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.tts.v20190823 import tts_client, models as tts_models

last_pyaudio = None
last_player = None

#Call Tencent TTS: Text To Speech service to speak out Hunyuan's reply
#这里最关键的是使用原音频的音色speak out回答，这样听起来更自然
#The key point here is to use the original audio's voice to speak out the reply, so it sounds more natural
#这里没有还没有使用原音频的音色，后续可以尝试使用复刻音色功能
def tts_play(audio_data):

    global last_pyaudio, last_player

    if audio_data:

        if last_pyaudio is not None and last_player is not None:
            if last_player.is_active():
                print("Last TTS Play is not finish ：")
                print("Stop Last TTS Play  ：")
                last_player.stop_stream()
                last_player.close()
                last_pyaudio.terminate()
                print("Last TTS Play Stops successfully  ：")
                gc.collect()
                time.sleep(0.1)

                print("New TTS Play start ：")
                p = PyAudio()
                last_pyaudio = p
                player = p.open(format=p.get_format_from_width(2), channels=1, rate=16000, output=True)
                last_player = player
                print("TTS Play Start ：")
                player.write(audio_data)
                print("TTS Play End ：")        
                player.stop_stream()
                player.close()
                p.terminate()
                print("TTS调用成功：")                   
        else:
            p = PyAudio()
            last_pyaudio = p
            player = p.open(format=p.get_format_from_width(2), channels=1, rate=16000, output=True)
            last_player = player
            print("Frist TTS Play Start ：")
            player.write(audio_data)
            print("First TTS Play End ：")        
            player.stop_stream()
            player.close()
            p.terminate()
            print("TTS调用成功：")                        
    else:
        print("Error: Decoded audio data is None")

#Configure Tencent TTS: Text To Speech service
def tts_config(voicetype, text):
    params = {
        "Text": text,
        "SessionId": "test_session_id",
        "Volume": 0,
        "Speed": 0,      
        "ProjectId": 0,
        "ModelType": 1,                   
        "VoiceType": voicetype,       
        "PrimaryLanguage": 1,
        "SampleRate": 16000,
        "Codec": "wav",
        "SegmentRate": 0,
        "EmotionCategory": "neutral",
        "EmotionIntensity": 100
    }

    return json.dumps(params)

#Call Tencent TTS: Text To Speech service to speak out Hunyuan's reply
#这里最关键的是使用原音频的音色speak out回答，这样听起来更自然
#播放TTS的音频时，需要在一个新的线程中运行，这样可以避免阻塞主线程，持续监听用户的问题
def handle_tts(cred, text):

    try:
        httpProfile = HttpProfile()
        httpProfile.endpoint = "tts.tencentcloudapi.com"

        cpf = ClientProfile()
        # 预先建立连接可以降低访问延迟
        cpf.httpProfile.pre_conn_pool_size = 3        
        cpf.httpProfile = httpProfile
        client = tts_client.TtsClient(cred, "ap-guangzhou", cpf)

        req = tts_models.TextToVoiceRequest()
        req.from_json_string(tts_config(101002, text))

        start_time = time.time()  # Record start time
        resp = client.TextToVoice(req)
        end_time = time.time()  # Record end time
        time_consumed = end_time - start_time  # Calculate time consumed
        print(f"Time consumed for tencent TTS TextToVoice: {time_consumed:.2f} seconds")        

        if resp.Audio:
            try:
                audio_data = base64.b64decode(resp.Audio)
            except Exception as e:
                print(f"Error decoding audio data: {e}")
                audio_data = None

            if audio_data:
                # Run the audio playback in a separate thread
                audio_thread = threading.Thread(target=tts_play, args=(audio_data,))
                audio_thread.start()
            else:
                print("Error: Decoded audio data is None")
        else:
            print("TTS调用失败")

    except Exception as e:
        print(e)     

# for debug purpose
if __name__ == "__main__":

    handle_tts( credential.Credential(
       os.environ.get("TENCENTCLOUD_SECRET_ID"),
       os.environ.get("TENCENTCLOUD_SECRET_KEY")),
       '这是一段测试音频，旨在测试tts能正常工作'
       )