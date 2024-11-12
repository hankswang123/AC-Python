import json
import os
import base64
import wave
import pyaudio

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.tts.v20190823 import tts_client, models
from pyaudio import PyAudio, paInt16
#https://github.com/TencentCloud/tencentcloud-sdk-python/blob/master/tencentcloud/tts/v20190823/tts_client.py
#


#此文件演示了如何使用腾讯云的语音合成接口，这个文件可以执行成功

def tts_config(secret_id, secret_key, text):
    try:
        cred = credential.Credential(secret_id, secret_key)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "tts.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = tts_client.TtsClient(cred, "ap-guangzhou", clientProfile)

        req = models.TextToVoiceRequest()
        params = {
            "Text": text,
            "SessionId": "test_session_id",
            "Volume": 5,
            "Speed": 1,      
            "ProjectId": 0,
            "ModelType": 1,                   
#            "VoiceType": 101002,            
            "VoiceType": 1050,  #WeJack 英文 标准 男声          
            "PrimaryLanguage": 1,
            "SampleRate": 16000,
            "Codec": "wav",
            "EnableSubtitle": True,           
            "SegmentRate": 0,
            "EmotionCategory": "neutral",
            "EmotionIntensity": 100
        }

        params_json = json.dumps(params)
        req.from_json_string(params_json)

        resp = client.TextToVoice(req)

        print(resp.to_json_string(indent=2))
#        print(resp.Subtitles.to_json_string(indent=2))
#        return resp.to_json_string(indent=2)
#        for subtitle in resp.Subtitles:
#            print(json.dumps(subtitle, ensure_ascii=False, indent=2))
#            print(subtitle.to_json_string(indent=2))
#            print(resp.Subtitles)
#            resp = client.TextToVoice(req)
        return resp.Audio

    except Exception as e:
        print(e)
        return None

if __name__ == "__main__":
    secret_id = os.environ.get("TENCENTCLOUD_SECRET_ID")
    secret_key = os.environ.get("TENCENTCLOUD_SECRET_KEY")
#     text =  '''
# May 22-26, the World Economic Forum’s Annual Meeting will take place in Davos-Klosters, Switzerland, under the theme of Working Together, Restoring Trust. Business leaders, international political leaders, economists, celebrities and journalists come together to discuss global issues such as climate change and broader social challenges with regards to a sustainable future.

# SAP announced that the jobs at SAP Landing Page for refugees from Ukraine is live.
#     '''    
    text =  '''
To support refugees from Ukraine, S A P is rolling out a dedicated onboarding process for refugees who have arrived in Bulgaria, Czech Republic, Germany, Hungary, Poland, Romania and Slovakia. This includes buddy support with an existing Ukrainian employee, mental health support and dedicated learning and language courses, childcare options (in selected countries) and advanced payment options for new hires. S A P is also working to extend this to other countries.
    '''
    result = tts_config(secret_id, secret_key, text)

    if result:
        try:
            with open("output2.wav", "wb") as f:
                f.write(base64.b64decode(result))

            # with wave.open("output.wav", "rb") as wf:
            #     format = pyaudio.paInt16  # Assuming 16-bit PCM
            #     channels = wf.getnchannels()
            #     rate = wf.getframerate()
            # print(f"Format: {format}, Channels: {channels}, Rate: {rate}")
 
            # p1 = pyaudio.PyAudio()
            # stream = p1.open(format=format, channels=channels, rate=rate, output=True)

            # # Play the audio data
            # data = wf.readframes(1024)
            # while data:
            #     stream.write(data)
            #     data = wf.readframes(1024)

            # stream.stop_stream()
            # stream.close()
            # p1.terminate()

            audio_data = base64.b64decode(result)
        except Exception as e:
            print(f"Error decoding audio data: {e}")
            audio_data = None

        if audio_data:

            p = PyAudio()
            player = p.open(format=p.get_format_from_width(2), channels=1, rate=16000, output=True)
            player.write(audio_data)
            player.stop_stream()
            player.close()
            p.terminate()
            print("TTS调用成功：")
#            print(result)            
#    for chunk in result(chunk_size=1024):
#        player.write(chunk)

        else:
            print("Error: Decoded audio data is None")
    else:
        print("TTS调用失败")