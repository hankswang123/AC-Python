# -*- coding: utf-8 -*-
import gc
import json
import os
import base64
import time

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.tts.v20190823 import tts_client, models as tts_models


#Configure Tencent TTS: Text To Speech service
def tts_config(voicetype, text):
    params = {
        "Text": text,
        "SessionId": "test_session_id",
        "Volume": 5,
        "Speed": 1,      
        "ProjectId": 0,
        "ModelType": 1,                   
        "VoiceType": voicetype, 
        "PrimaryLanguage": 1,
        "SampleRate": 16000,
        "Codec": "wav",
        #"EnableSubtitle": True,  
        "SegmentRate": 0,
        "EmotionCategory": "neutral",
        "EmotionIntensity": 100
    }

    return json.dumps(params)

#Call Tencent TTS: Text To Speech service to speak out Hunyuan's reply
#这里最关键的是使用原音频的音色speak out回答，这样听起来更自然
#播放TTS的音频时，需要在一个新的线程中运行，这样可以避免阻塞主线程，持续监听用户的问题
def handle_tts(cred, text):

#    print(f"Answers+Transition to be spoken: {text}")

    try:
        httpProfile = HttpProfile()
        httpProfile.endpoint = "tts.tencentcloudapi.com"

        cpf = ClientProfile()
        # 预先建立连接可以降低访问延迟
        cpf.httpProfile.pre_conn_pool_size = 3        
        cpf.httpProfile = httpProfile
        client = tts_client.TtsClient(cred, "ap-guangzhou", cpf)

        req = tts_models.TextToVoiceRequest()
        #v1050(voicetype): WeJack 英文 标准 男声          
        req.from_json_string(tts_config(1050, text))

        start_time = time.time()  # Record start time
        resp = client.TextToVoice(req)
        end_time = time.time()  # Record end time
        time_consumed = end_time - start_time  # Calculate time consumed
        print(f"Time consumed for __Tencent_TTS__ : {time_consumed:.2f} seconds")        

        if resp.Audio:
            try:
                audio_data = base64.b64decode(resp.Audio)
            except Exception as e:
                print(f"Error decoding audio data: {e}")
                audio_data = None

            if audio_data:
                return audio_data
            else:
                print("Error: Decoded audio data is None")
        else:
            print("TTS调用失败")

    except Exception as e:
        print(f"Error in handle_tts: {e}")
        print(e)     

# for debug purpose
if __name__ == "__main__":

    handle_tts( credential.Credential(
       os.environ.get("TENCENTCLOUD_SECRET_ID"),
       os.environ.get("TENCENTCLOUD_SECRET_KEY")),
       '这是一段测试音频，旨在测试tts能正常工作'
       )