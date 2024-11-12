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
            "Volume": 0,
            "Speed": 0,      
            "ProjectId": 0,
            "ModelType": 1,                   
#            "VoiceType": 101002,            
            "voiceType": 200000000,  #复刻音色
            "PrimaryLanguage": 1,
            "SampleRate": 16000,
            "Codec": "wav",
            "SegmentRate": 0,
            "EmotionCategory": "neutral",
            "EmotionIntensity": 100,
            "FastvoiceType": 200011055,  # My voice
        }

        params_json = json.dumps(params)
        req.from_json_string(params_json)

        resp = client.TextToVoice(req)
#        return resp.to_json_string(indent=2)
        return resp.Audio

    except Exception as e:
        print(e)
        return None

if __name__ == "__main__":
    secret_id = os.environ.get("TENCENTCLOUD_SECRET_ID"
    secret_key = os.environ.get("TENCENTCLOUD_SECRET_KEY")
    text =  '''
    在这个示例中，我们定义了一个名为play_mp3的函数，该函数接受一个MP3文件路径作为参数。函数首先初始化pygame.mixer模块，然后加载并播放指定的MP3文件。while循环会一直执行，直到音乐播放完毕。
请将your_mp3_file.mp3替换为您要播放的MP3文件的路径。
    '''
    result = tts_config(secret_id, secret_key, text)

    if result:
        try:
            # with open("output.wav", "wb") as f:
            #     f.write(base64.b64decode(result))

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
            print(result)            
#    for chunk in result(chunk_size=1024):
#        player.write(chunk)

        else:
            print("Error: Decoded audio data is None")
    else:
        print("TTS调用失败")